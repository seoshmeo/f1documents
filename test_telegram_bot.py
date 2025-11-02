#!/usr/bin/env python3
"""
Telegram Bot Diagnostic Tool
Helps diagnose Telegram bot configuration and get group chat IDs
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()


async def main():
    """Test bot and show diagnostic information"""

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not bot_token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    print("="*60)
    print("Telegram Bot Diagnostic Tool")
    print("="*60)
    print(f"Bot Token: {bot_token[:20]}...")
    print()

    bot = Bot(token=bot_token)

    # Test 1: Get bot info
    print("1. Testing bot connection and getting bot info...")
    try:
        bot_info = await bot.get_me()
        print(f"✅ Bot is working!")
        print(f"   Bot Name: {bot_info.first_name}")
        print(f"   Bot Username: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        print()
    except TelegramError as e:
        print(f"❌ Error getting bot info: {e}")
        sys.exit(1)

    # Test 2: Get updates to see recent messages
    print("2. Checking recent messages/updates...")
    print("   (Bot needs to receive at least one message to detect chats)")
    print()
    try:
        updates = await bot.get_updates(limit=10)

        if not updates:
            print("⚠️  No recent updates found.")
            print()
            print("📝 To get group chat ID:")
            print("   1. Add the bot to your group as administrator")
            print("   2. Send a message in the group (e.g., /start)")
            print("   3. Run this script again")
            print()
        else:
            print(f"✅ Found {len(updates)} recent updates:")
            print()

            seen_chats = {}

            for update in updates:
                if update.message:
                    chat = update.message.chat
                    chat_id = chat.id

                    if chat_id not in seen_chats:
                        seen_chats[chat_id] = {
                            'type': chat.type,
                            'title': chat.title or chat.first_name or 'Unknown',
                            'username': chat.username
                        }

            print("Chats where bot has received messages:")
            print()
            for chat_id, info in seen_chats.items():
                chat_type = info['type']
                title = info['title']
                username = info['username']

                emoji = {
                    'private': '👤',
                    'group': '👥',
                    'supergroup': '👥',
                    'channel': '📢'
                }.get(chat_type, '💬')

                print(f"{emoji} Chat ID: {chat_id}")
                print(f"   Type: {chat_type}")
                print(f"   Name: {title}")
                if username:
                    print(f"   Username: @{username}")
                print()

    except TelegramError as e:
        print(f"❌ Error getting updates: {e}")
        print()

    # Test 3: Test sending to configured chats
    print("3. Testing configured chat IDs from .env...")
    print()

    admin_chat = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    larnaka_chat = os.getenv('LARNAKA_TELEGRAM_CHAT_ID')
    fia_chat = os.getenv('FIA_TELEGRAM_CHAT_ID')

    test_chats = {
        'Admin Chat': admin_chat,
        'Larnaka Channel': larnaka_chat,
        'FIA Channel': fia_chat
    }

    for name, chat_id in test_chats.items():
        if not chat_id:
            print(f"⚠️  {name}: Not configured in .env")
            continue

        print(f"Testing {name} (ID: {chat_id})...")
        try:
            # Try to get chat info
            chat_info = await bot.get_chat(chat_id)
            print(f"✅ {name} is accessible!")
            print(f"   Type: {chat_info.type}")
            print(f"   Title: {chat_info.title or chat_info.first_name or 'N/A'}")

            # Test sending a message
            test_msg = f"🔧 Test message from bot diagnostic tool\n\nChat ID: {chat_id}"
            await bot.send_message(chat_id=chat_id, text=test_msg)
            print(f"   ✅ Test message sent successfully!")

        except TelegramError as e:
            print(f"❌ Error accessing {name}: {e}")

        print()

    print("="*60)
    print("Diagnostic complete!")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
