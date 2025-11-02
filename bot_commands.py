#!/usr/bin/env python3
"""
Telegram Bot Command Handlers
Handles bot commands for controlling the FIA scraper
"""

import os
import time
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from old_database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotCommandHandler:
    """Handles Telegram bot commands"""

    def __init__(self, db: Database, allowed_chat_id: str):
        self.db = db
        self.allowed_chat_id = allowed_chat_id
        logger.info(f"Bot command handler initialized for chat: {allowed_chat_id}")

    def is_authorized(self, update: Update) -> bool:
        """Check if user is authorized to use bot commands"""
        chat_id = str(update.effective_chat.id)
        if chat_id != self.allowed_chat_id:
            logger.warning(f"Unauthorized access attempt from chat {chat_id}")
            return False
        return True

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self.is_authorized(update):
            return

        message = (
            "🏎️ <b>FIA Documents Scraper Bot</b>\n\n"
            "Доступные команды:\n\n"
            "⚙️ <b>Управление интервалом:</b>\n"
            "/interval - показать текущий интервал\n"
            "/interval 1800 - установить интервал (в секундах)\n"
            "  Примеры: 1800 = 30 мин, 3600 = 1 час\n\n"
            "📊 <b>Статистика:</b>\n"
            "/status - статус скрапера\n"
            "/stats - статистика документов\n\n"
            "🔧 <b>Управление:</b>\n"
            "/check - принудительная проверка сейчас\n"
            "/enable - включить автоматический скрапинг\n"
            "/disable - выключить автоматический скрапинг\n\n"
            "📝 <b>Информация:</b>\n"
            "/help - показать эту справку"
        )
        await update.message.reply_text(message, parse_mode='HTML')

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.cmd_start(update, context)

    async def cmd_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /interval command - get or set check interval"""
        if not self.is_authorized(update):
            return

        # If no argument, show current interval
        if not context.args:
            interval = self.db.get_setting('check_interval', '3600')
            interval_int = int(interval)
            minutes = interval_int // 60
            hours = interval_int // 3600

            message = f"⏱ <b>Текущий интервал проверки:</b>\n\n"
            message += f"🕐 {interval} секунд\n"
            if minutes > 0:
                message += f"📅 {minutes} минут\n"
            if hours > 0:
                message += f"⏰ {hours} часов\n"
            message += f"\n💡 Для изменения: /interval <секунды>"

            await update.message.reply_text(message, parse_mode='HTML')
            return

        # Set new interval
        try:
            new_interval = int(context.args[0])

            # Validate interval (minimum 60 seconds, maximum 24 hours)
            if new_interval < 60:
                await update.message.reply_text(
                    "❌ Ошибка: минимальный интервал 60 секунд"
                )
                return

            if new_interval > 86400:
                await update.message.reply_text(
                    "❌ Ошибка: максимальный интервал 24 часа (86400 секунд)"
                )
                return

            # Update setting
            username = update.effective_user.username or update.effective_user.first_name
            self.db.set_setting('check_interval', str(new_interval), username)

            minutes = new_interval // 60
            hours = new_interval // 3600

            message = f"✅ <b>Интервал обновлен!</b>\n\n"
            message += f"🕐 {new_interval} секунд\n"
            if minutes > 0:
                message += f"📅 {minutes} минут\n"
            if hours > 0:
                message += f"⏰ {hours} часов\n"
            message += f"\n⚠️ Изменения вступят в силу после следующей проверки"

            await update.message.reply_text(message, parse_mode='HTML')
            logger.info(f"Interval updated to {new_interval} seconds by {username}")

        except ValueError:
            await update.message.reply_text(
                "❌ Ошибка: укажите число в секундах\n"
                "Например: /interval 1800 (30 минут)"
            )
        except Exception as e:
            logger.error(f"Error setting interval: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - show scraper status"""
        if not self.is_authorized(update):
            return

        try:
            # Get settings
            interval = self.db.get_setting('check_interval', '3600')
            enabled = self.db.get_setting('scraper_enabled', 'true')
            last_check = self.db.get_setting('last_check_time', '0')

            # Get document count
            docs = self.db.get_all_documents()
            doc_count = len(docs)

            # Calculate time since last check
            last_check_int = int(last_check)
            if last_check_int > 0:
                time_diff = int(time.time()) - last_check_int
                minutes_ago = time_diff // 60
                hours_ago = time_diff // 3600
                if hours_ago > 0:
                    last_check_str = f"{hours_ago} ч. {(minutes_ago % 60)} мин. назад"
                else:
                    last_check_str = f"{minutes_ago} мин. назад"
            else:
                last_check_str = "Никогда"

            status_emoji = "✅" if enabled == 'true' else "⏸"
            status_text = "Включен" if enabled == 'true' else "Выключен"

            message = f"{status_emoji} <b>Статус скрапера</b>\n\n"
            message += f"📊 Статус: {status_text}\n"
            message += f"⏱ Интервал: {interval} сек ({int(interval)//60} мин)\n"
            message += f"🕐 Последняя проверка: {last_check_str}\n"
            message += f"📄 Документов в БД: {doc_count}\n"

            if docs and len(docs) > 0:
                latest = docs[0]
                message += f"\n📌 Последний документ:\n"
                message += f"   {latest['document_name'][:50]}..."

            await update.message.reply_text(message, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await update.message.reply_text(f"❌ Ошибка получения статуса: {e}")

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - show statistics"""
        if not self.is_authorized(update):
            return

        try:
            docs = self.db.get_all_documents()
            doc_count = len(docs)

            if doc_count == 0:
                await update.message.reply_text("📊 В базе данных пока нет документов")
                return

            # Calculate statistics
            total_size = sum(doc['file_size'] or 0 for doc in docs)
            total_size_mb = total_size / (1024 * 1024)

            # Get latest document
            latest = docs[0] if docs else None

            message = f"📊 <b>Статистика документов</b>\n\n"
            message += f"📄 Всего документов: {doc_count}\n"
            message += f"💾 Общий размер: {total_size_mb:.2f} MB\n"

            if latest:
                message += f"\n📌 Последний добавленный:\n"
                message += f"   {latest['document_name'][:60]}\n"
                message += f"   🕐 {latest['created_at']}\n"

            await update.message.reply_text(message, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await update.message.reply_text(f"❌ Ошибка получения статистики: {e}")

    async def cmd_enable(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /enable command - enable scraping"""
        if not self.is_authorized(update):
            return

        try:
            username = update.effective_user.username or update.effective_user.first_name
            self.db.set_setting('scraper_enabled', 'true', username)
            await update.message.reply_text(
                "✅ Автоматический скрапинг включен"
            )
            logger.info(f"Scraping enabled by {username}")
        except Exception as e:
            logger.error(f"Error enabling scraping: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def cmd_disable(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disable command - disable scraping"""
        if not self.is_authorized(update):
            return

        try:
            username = update.effective_user.username or update.effective_user.first_name
            self.db.set_setting('scraper_enabled', 'false', username)
            await update.message.reply_text(
                "⏸ Автоматический скрапинг выключен\n"
                "Для включения используйте /enable"
            )
            logger.info(f"Scraping disabled by {username}")
        except Exception as e:
            logger.error(f"Error disabling scraping: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def cmd_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command - force immediate check"""
        if not self.is_authorized(update):
            return

        await update.message.reply_text(
            "🔄 Принудительная проверка запущена...\n"
            "Результаты будут отправлены автоматически"
        )
        # Set a flag to trigger immediate check
        self.db.set_setting('force_check', 'true', 'bot_command')
        logger.info("Force check triggered")


async def setup_bot_handlers(application: Application, db: Database, chat_id: str):
    """Setup bot command handlers"""
    handler = BotCommandHandler(db, chat_id)

    application.add_handler(CommandHandler("start", handler.cmd_start))
    application.add_handler(CommandHandler("help", handler.cmd_help))
    application.add_handler(CommandHandler("interval", handler.cmd_interval))
    application.add_handler(CommandHandler("status", handler.cmd_status))
    application.add_handler(CommandHandler("stats", handler.cmd_stats))
    application.add_handler(CommandHandler("enable", handler.cmd_enable))
    application.add_handler(CommandHandler("disable", handler.cmd_disable))
    application.add_handler(CommandHandler("check", handler.cmd_check))

    logger.info("Bot command handlers registered")
