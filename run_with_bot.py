#!/usr/bin/env python3
"""
Run FIA Scraper with Telegram Bot in parallel
Starts both the continuous scraper and bot command handler
"""

import os
import sys
import time
import logging
import threading
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fia_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_scraper():
    """Run continuous scraper in a separate thread"""
    from main import FIADocumentService

    logger.info("Starting scraper thread...")
    service = FIADocumentService()

    try:
        service.initialize()
        initial_interval = service.get_check_interval()
        logger.info(f"Scraper initialized with interval: {initial_interval} seconds")

        while True:
            try:
                current_interval = service.get_check_interval()

                if not service.is_scraper_enabled():
                    logger.info("Scraping disabled, waiting...")
                    time.sleep(30)
                    continue

                # Process documents
                new_docs = service.process_documents()
                service.update_last_check_time()

                if new_docs > 0:
                    logger.info(f"Added {new_docs} new document(s)")

                # Sleep with force check monitoring
                sleep_time = 0
                while sleep_time < current_interval:
                    time.sleep(10)
                    sleep_time += 10

                    if service.check_force_flag():
                        logger.info("Force check triggered, running immediately!")
                        break

            except Exception as e:
                logger.error(f"Error in scraper thread: {e}")
                time.sleep(60)

    except Exception as e:
        logger.error(f"Fatal error in scraper thread: {e}")
    finally:
        service.db.close_all_connections()


def run_bot():
    """Run Telegram bot"""
    from database import Database
    from bot_commands import setup_bot_handlers

    logger.info("Starting Telegram bot...")

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        logger.error("Missing Telegram credentials!")
        return

    db = Database()

    # Create application
    application = Application.builder().token(bot_token).build()

    # Setup handlers synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_bot_handlers(application, db, chat_id))

    logger.info("Bot handlers registered, starting polling...")

    # Run polling (this is blocking and manages its own event loop)
    application.run_polling(drop_pending_updates=True, allowed_updates=['message'])


def main():
    """Main entry point - run both scraper and bot"""
    logger.info("="*60)
    logger.info("Starting FIA Scraper with Bot Control")
    logger.info("="*60)

    # Start scraper in a background thread
    scraper_thread = threading.Thread(target=run_scraper, daemon=True)
    scraper_thread.start()
    logger.info("Scraper thread started")

    # Run bot in main thread (blocking)
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
