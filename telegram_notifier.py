#!/usr/bin/env python3
"""
Telegram Notifier Module

This module handles sending notifications to Telegram channels
when new FIA documents are discovered.
"""

import os
import logging
from typing import Optional, Dict
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handles sending notifications to Telegram channels"""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram Notifier

        Args:
            bot_token: Telegram Bot API token
            chat_id: Telegram chat/channel ID
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        self.event_loop = None  # Persistent event loop

        if not self.enabled:
            logger.warning("Telegram notifications disabled: missing bot token or chat ID")
        else:
            # Create a dedicated httpx client with its own connection pool
            # This prevents pool conflicts with the bot command handler
            from telegram.request import HTTPXRequest

            request = HTTPXRequest(
                connection_pool_size=8,  # Increased pool size for notifications
                connect_timeout=30.0,
                read_timeout=30.0,
                write_timeout=30.0,
                pool_timeout=10.0  # Increased from default 1.0 second
            )
            self.bot = Bot(token=self.bot_token, request=request)
            logger.info(f"Telegram notifier initialized with dedicated connection pool (size=8) for chat ID: {self.chat_id}")

    def format_document_message(self, document: Dict) -> str:
        """
        Format a document into a nice Telegram message

        Args:
            document: Document dictionary with name, url, size, summary, etc.

        Returns:
            Formatted message string
        """
        # Format size if available
        size_str = ""
        if document.get('size'):
            size_bytes = document['size']
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"

        # Build message
        message_parts = [
            "🏎️ <b>Новый документ FIA</b>\n",
            f"📄 <b>{document.get('name', 'Unknown Document')}</b>\n"
        ]

        if size_str:
            message_parts.append(f"📊 Размер: {size_str}\n")

        if document.get('season'):
            message_parts.append(f"🏁 Сезон: {document['season']}\n")

        # Add summary if available
        if document.get('summary'):
            message_parts.append(f"\n📝 <b>Краткое содержание:</b>\n{document['summary']}\n")

        message_parts.append(f"\n🔗 <a href=\"{document['url']}\">Открыть документ</a>")

        return "".join(message_parts)

    async def _send_message_async(self, message: str, chat_id: str = None) -> bool:
        """
        Send message asynchronously

        Args:
            message: Message text to send
            chat_id: Optional chat ID to send to (uses default if not specified)

        Returns:
            True if successful, False otherwise

        Raises:
            Exception if sending fails (for retry logic)
        """
        target_chat_id = chat_id or self.chat_id
        await self.bot.send_message(
            chat_id=target_chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        logger.info(f"Message sent to Telegram chat {target_chat_id}")
        return True

    def send_message(self, message: str, chat_id: str = None) -> bool:
        """
        Send a plain text message to Telegram

        Args:
            message: Message text to send
            chat_id: Optional chat ID to send to (uses default if not specified)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping message")
            return False

        import time
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds

        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to send message (attempt {attempt + 1}/{max_retries})")

                # Create or reuse persistent event loop for this instance
                if self.event_loop is None or self.event_loop.is_closed():
                    logger.debug("Creating new persistent event loop for notifier")
                    self.event_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.event_loop)

                # Run the async send operation
                self.event_loop.run_until_complete(self._send_message_async(message, chat_id))
                logger.info(f"Message sent successfully on attempt {attempt + 1}")
                return True

            except Exception as e:
                error_str = str(e)
                # Check if this is a retryable error
                is_retryable = any(keyword in error_str.lower() for keyword in [
                    'pool timeout', 'event loop is closed', 'connection', 'timeout'
                ])

                # If event loop error, reset it
                if 'event loop is closed' in error_str.lower():
                    logger.debug("Event loop was closed, will create new one on retry")
                    self.event_loop = None

                if is_retryable and attempt < max_retries - 1:
                    logger.warning(f"Retryable error ({error_str}), retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue  # Try again
                else:
                    logger.error(f"Error in send_message (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        logger.error("Non-retryable error, aborting")
                    return False

        logger.error(f"Failed to send message after {max_retries} attempts")
        return False

    def notify_new_document(self, document: Dict) -> bool:
        """
        Send notification about a new document

        Args:
            document: Document dictionary containing name, url, size, etc.

        Returns:
            True if notification was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping document notification")
            return False

        try:
            message = self.format_document_message(document)
            return self.send_message(message)

        except Exception as e:
            logger.error(f"Error notifying about document: {e}")
            return False

    def notify_multiple_documents(self, documents: list) -> int:
        """
        Send notifications for multiple new documents

        Args:
            documents: List of document dictionaries

        Returns:
            Number of successfully sent notifications
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping notifications")
            return 0

        success_count = 0

        for doc in documents:
            if self.notify_new_document(doc):
                success_count += 1
                # Small delay between messages to avoid rate limiting
                import time
                time.sleep(0.5)

        logger.info(f"Sent {success_count}/{len(documents)} Telegram notifications")
        return success_count

    def test_connection(self) -> bool:
        """
        Test Telegram bot connection

        Returns:
            True if connection is successful, False otherwise
        """
        if not self.enabled:
            logger.error("Cannot test connection: Telegram not configured")
            return False

        try:
            test_message = "✅ Telegram уведомления настроены!\n\nБот FIA Documents Scraper готов к работе."
            return self.send_message(test_message)

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def cleanup(self):
        """Clean up resources (event loop)"""
        if self.event_loop and not self.event_loop.is_closed():
            logger.debug("Closing persistent event loop")
            self.event_loop.close()
            self.event_loop = None
