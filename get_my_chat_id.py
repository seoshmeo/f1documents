#!/usr/bin/env python3
"""
Узнать свой Telegram Chat ID

Запустите этот скрипт и напишите боту любое сообщение
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any message and show chat ID"""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Без username"
    first_name = update.effective_user.first_name or ""

    print("\n" + "="*60)
    print("✅ ВАШИ ДАННЫЕ:")
    print("="*60)
    print(f"Chat ID: {chat_id}")
    print(f"Имя: {first_name}")
    print(f"Username: @{username}")
    print("="*60)
    print("\nДобавьте эту строку в .env файл:")
    print(f"TELEGRAM_ADMIN_CHAT_ID={chat_id}")
    print("="*60)

    await update.message.reply_text(
        f"✅ Ваш Chat ID: <code>{chat_id}</code>\n\n"
        f"Добавьте в .env:\n"
        f"<code>TELEGRAM_ADMIN_CHAT_ID={chat_id}</code>",
        parse_mode='HTML'
    )


async def main():
    """Run the bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        sys.exit(1)

    print("="*60)
    print("🤖 БОТ ЗАПУЩЕН")
    print("="*60)
    print("Напишите боту ЛЮБОЕ сообщение в Telegram")
    print("Бот покажет ваш Chat ID")
    print("\nДля остановки: Ctrl+C")
    print("="*60)

    # Create application
    application = Application.builder().token(bot_token).build()

    # Add handler for any message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    await application.run_polling(allowed_updates=['message'])


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nБот остановлен")
