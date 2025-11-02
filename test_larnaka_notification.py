#!/usr/bin/env python3
"""
Quick test script to send a Larnaka event notification
Tests the exact code path that main_larnaka.py uses
"""

import os
import sys
from dotenv import load_dotenv
from telegram_notifier import TelegramNotifier
from formatters.larnaka_formatter import format_larnaka_event_post

# Load environment variables
load_dotenv()

def main():
    print("="*60)
    print("Testing Larnaka Event Notification")
    print("="*60)

    # Get configuration
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    admin_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    larnaka_chat_id = os.getenv('LARNAKA_TELEGRAM_CHAT_ID')

    print(f"\nConfiguration:")
    print(f"Bot Token: {bot_token[:20] if bot_token else 'NOT SET'}...")
    print(f"Admin Chat ID: {admin_chat_id or 'NOT SET'}")
    print(f"Larnaka Chat ID: {larnaka_chat_id or 'NOT SET'}")
    print()

    if not bot_token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    if not larnaka_chat_id:
        print("❌ ERROR: LARNAKA_TELEGRAM_CHAT_ID not set in .env")
        sys.exit(1)

    # Initialize notifier (same way as main_larnaka.py)
    telegram = TelegramNotifier(bot_token, admin_chat_id)

    # Create test event data
    event_data = {
        'event_title': 'Test Event - Διαγνωστικό Τεστ',
        'event_date': '15 December 2024',
        'event_time': '19:00',
        'event_location': 'Larnaka Municipal Theatre',
        'summary': 'Αυτό είναι ένα τεστ μήνυμα από το διαγνωστικό εργαλείο. This is a test message from the diagnostic tool.',
        'event_url': 'https://www.larnaka.org.cy/en/test-event'
    }

    # Format message (same way as main_larnaka.py)
    message = format_larnaka_event_post(event_data)

    print("Formatted message:")
    print("-"*60)
    print(message)
    print("-"*60)
    print()

    # Test 1: Send to Admin Chat (if configured)
    if admin_chat_id:
        print(f"Test 1: Sending to Admin Chat ({admin_chat_id})...")
        try:
            result = telegram.send_message(message, chat_id=admin_chat_id)
            if result:
                print(f"✅ SUCCESS: Message sent to admin chat")
            else:
                print(f"❌ FAILED: Could not send to admin chat")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        print()

    # Test 2: Send to Larnaka Channel (main target)
    print(f"Test 2: Sending to Larnaka Channel ({larnaka_chat_id})...")
    try:
        result = telegram.send_message(message, chat_id=larnaka_chat_id)
        if result:
            print(f"✅ SUCCESS: Message sent to Larnaka channel")
            print(f"\nCheck your Telegram group to verify the message arrived!")
        else:
            print(f"❌ FAILED: Could not send to Larnaka channel")
            print(f"\nPossible issues:")
            print(f"  - Bot not added to the group")
            print(f"  - Bot not an administrator")
            print(f"  - Incorrect chat ID")
            print(f"  - Bot was removed from the group")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"\nError details:")
        print(f"  {type(e).__name__}: {str(e)}")

    print()
    print("="*60)
    print("Test Complete")
    print("="*60)

    # Cleanup
    telegram.cleanup()

if __name__ == '__main__':
    main()
