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
from telegram.error import TelegramError
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

        if not self.enabled:
            logger.warning("Telegram notifications disabled: missing bot token or chat ID")
        else:
            self.bot = Bot(token=self.bot_token)
            logger.info(f"Telegram notifier initialized for chat ID: {self.chat_id}")

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

    async def _send_message_async(self, message: str) -> bool:
        """
        Send message asynchronously

        Args:
            message: Message text to send

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            logger.info(f"Message sent to Telegram chat {self.chat_id}")
            return True

        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """
        Send a plain text message to Telegram

        Args:
            message: Message text to send

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping message")
            return False

        try:
            # Try to get existing event loop, create new one if needed
            try:
                loop = asyncio.get_running_loop()
                # If we're in a running loop, create task instead
                task = loop.create_task(self._send_message_async(message))
                # Wait for completion using asyncio.run_coroutine_threadsafe
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(self._send_message_async(message), loop)
                result = future.result(timeout=30)
                return result
            except RuntimeError:
                # No running loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._send_message_async(message))
                    return result
                finally:
                    loop.close()

        except Exception as e:
            logger.error(f"Error in send_message: {e}")
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
