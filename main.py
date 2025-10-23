#!/usr/bin/env python3
"""
FIA Documents Scraper Service

This service monitors the FIA Formula One documents page,
extracts PDF documents, and stores them in PostgreSQL database
if they don't already exist.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
from database import Database
from scraper import FIAScraper
from telegram_notifier import TelegramNotifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fia_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class FIADocumentService:
    """Main service to coordinate scraping and database operations"""

    def __init__(self):
        self.db = Database()
        self.fia_url = os.getenv(
            'FIA_URL',
            'https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071'
        )
        self.scraper = FIAScraper(self.fia_url)
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 3600))  # Default: 1 hour
        self.telegram = TelegramNotifier()  # Initialize Telegram notifier

    def get_check_interval(self):
        """Get current check interval from database or environment"""
        try:
            interval_str = self.db.get_setting('check_interval', str(self.check_interval))
            return int(interval_str)
        except Exception as e:
            logger.warning(f"Could not get interval from DB, using default: {e}")
            return self.check_interval

    def is_scraper_enabled(self):
        """Check if scraper is enabled"""
        try:
            enabled = self.db.get_setting('scraper_enabled', 'true')
            return enabled.lower() == 'true'
        except Exception as e:
            logger.warning(f"Could not get enabled status, assuming true: {e}")
            return True

    def check_force_flag(self):
        """Check and reset force check flag"""
        try:
            force = self.db.get_setting('force_check', 'false')
            if force == 'true':
                self.db.set_setting('force_check', 'false', 'system')
                return True
            return False
        except Exception as e:
            logger.warning(f"Could not check force flag: {e}")
            return False

    def update_last_check_time(self):
        """Update last check timestamp"""
        try:
            self.db.set_setting('last_check_time', str(int(time.time())), 'system')
        except Exception as e:
            logger.warning(f"Could not update last check time: {e}")

    def initialize(self):
        """Initialize the service"""
        logger.info("Initializing FIA Document Service...")

        # Create database tables if they don't exist
        try:
            self.db.create_tables()
            self.db.create_settings_table()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def process_documents(self):
        """Scrape documents and save new ones to database"""
        try:
            logger.info("="*60)
            logger.info("Starting document processing...")

            # Scrape documents from FIA website
            documents = self.scraper.scrape_documents()

            if not documents:
                logger.warning("No documents found on the page")
                return 0

            # Process each document
            new_documents_count = 0
            existing_documents_count = 0

            for doc in documents:
                try:
                    # Check if document already exists by URL
                    if self.db.document_exists(doc['url']):
                        existing_documents_count += 1
                        logger.info(f"Document already exists (skipping): {doc['name']}")
                        continue

                    # Check if document with same hash exists
                    if self.db.document_exists_by_hash(doc['hash']):
                        existing_documents_count += 1
                        logger.info(f"Document with same content exists (skipping): {doc['name']}")
                        continue

                    # Insert new document
                    document_id = self.db.insert_document(doc)

                    if document_id:
                        new_documents_count += 1
                        logger.info(f"NEW DOCUMENT ADDED: {doc['name']} (ID: {document_id})")
                        logger.info(f"  URL: {doc['url']}")
                        logger.info(f"  Size: {doc['size']} bytes" if doc['size'] else "  Size: Unknown")

                        # Send Telegram notification
                        try:
                            if self.telegram.notify_new_document(doc):
                                logger.info(f"Telegram notification sent for: {doc['name']}")
                            else:
                                logger.warning(f"Failed to send Telegram notification for: {doc['name']}")
                        except Exception as e:
                            logger.error(f"Error sending Telegram notification: {e}")
                    else:
                        existing_documents_count += 1

                except Exception as e:
                    logger.error(f"Error processing document {doc.get('name', 'Unknown')}: {e}")
                    continue

            # Summary
            logger.info("="*60)
            logger.info(f"Processing completed:")
            logger.info(f"  Total documents found: {len(documents)}")
            logger.info(f"  New documents added: {new_documents_count}")
            logger.info(f"  Existing documents skipped: {existing_documents_count}")
            logger.info("="*60)

            return new_documents_count

        except Exception as e:
            logger.error(f"Error in process_documents: {e}")
            raise

    def run_once(self):
        """Run the service once"""
        try:
            self.initialize()
            new_docs = self.process_documents()
            logger.info(f"Service run completed. {new_docs} new documents added.")
            return new_docs
        except Exception as e:
            logger.error(f"Error running service: {e}")
            raise
        finally:
            self.db.close_all_connections()

    def run_continuous(self):
        """Run the service continuously with dynamic interval from database"""
        try:
            self.initialize()

            initial_interval = self.get_check_interval()
            logger.info(f"Starting continuous monitoring (initial interval: {initial_interval} seconds)")

            while True:
                try:
                    # Get current interval from database (allows dynamic updates)
                    current_interval = self.get_check_interval()

                    # Check if scraping is enabled
                    if not self.is_scraper_enabled():
                        logger.info("Scraping is disabled, skipping check...")
                    else:
                        # Process documents
                        new_docs = self.process_documents()
                        self.update_last_check_time()

                        if new_docs > 0:
                            logger.info(f"Added {new_docs} new document(s)")

                    logger.info(f"Waiting {current_interval} seconds until next check...")

                    # Sleep in smaller intervals to check for force flag
                    sleep_time = 0
                    while sleep_time < current_interval:
                        time.sleep(10)  # Check every 10 seconds
                        sleep_time += 10

                        # Check for force check flag
                        if self.check_force_flag():
                            logger.info("Force check triggered!")
                            break

                except KeyboardInterrupt:
                    logger.info("Received interrupt signal. Shutting down...")
                    break
                except Exception as e:
                    logger.error(f"Error in continuous run: {e}")
                    logger.info("Waiting 60 seconds before retry...")
                    time.sleep(60)

        except Exception as e:
            logger.error(f"Fatal error in continuous mode: {e}")
            raise
        finally:
            self.db.close_all_connections()
            logger.info("Service stopped")

    def list_documents(self):
        """List all documents in database"""
        try:
            self.initialize()
            documents = self.db.get_all_documents()

            print("\n" + "="*80)
            print(f"Total documents in database: {len(documents)}")
            print("="*80)

            for idx, doc in enumerate(documents, 1):
                print(f"\n{idx}. {doc['document_name']}")
                print(f"   URL: {doc['document_url']}")
                print(f"   Added: {doc['created_at']}")
                print(f"   Size: {doc['file_size']} bytes" if doc['file_size'] else "   Size: Unknown")

            print("\n" + "="*80)

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
        finally:
            self.db.close_all_connections()

    def test_telegram(self):
        """Test Telegram bot connection"""
        try:
            logger.info("Testing Telegram connection...")
            if self.telegram.test_connection():
                logger.info("✅ Telegram connection successful!")
                return True
            else:
                logger.error("❌ Telegram connection failed!")
                return False
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            raise


    def run_with_bot(self):
        """Run service with Telegram bot command handling"""
        try:
            import asyncio
            from telegram.ext import Application
            from bot_commands import setup_bot_handlers

            self.initialize()

            # Get bot token and chat ID
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')

            if not bot_token or not chat_id:
                logger.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set for bot mode")
                raise ValueError("Missing Telegram credentials")

            logger.info("Starting bot mode with command handling...")

            # Create bot application
            application = Application.builder().token(bot_token).build()

            # Setup command handlers
            asyncio.run(setup_bot_handlers(application, self.db, chat_id))

            # Start bot in background
            logger.info("Starting Telegram bot...")
            application.run_polling(drop_pending_updates=True, allowed_updates=['message'])

            # This won't be reached while bot is running
            # The continuous monitoring happens in parallel through force_check flags

        except Exception as e:
            logger.error(f"Error in bot mode: {e}")
            raise
        finally:
            self.db.close_all_connections()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='FIA Documents Scraper Service')
    parser.add_argument(
        'mode',
        choices=['once', 'continuous', 'list', 'test-telegram', 'bot'],
        help='Run mode: once (single run), continuous (periodic checks with dynamic interval), '
             'list (show all documents), test-telegram (test Telegram connection), '
             'bot (run with Telegram bot command handling)'
    )

    args = parser.parse_args()

    service = FIADocumentService()

    try:
        if args.mode == 'once':
            service.run_once()
        elif args.mode == 'continuous':
            service.run_continuous()
        elif args.mode == 'list':
            service.list_documents()
        elif args.mode == 'test-telegram':
            service.test_telegram()
        elif args.mode == 'bot':
            service.run_with_bot()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
