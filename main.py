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

    def initialize(self):
        """Initialize the service"""
        logger.info("Initializing FIA Document Service...")

        # Create database tables if they don't exist
        try:
            self.db.create_tables()
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
        """Run the service continuously with specified interval"""
        try:
            self.initialize()

            logger.info(f"Starting continuous monitoring (interval: {self.check_interval} seconds)")

            while True:
                try:
                    new_docs = self.process_documents()

                    if new_docs > 0:
                        logger.info(f"Added {new_docs} new document(s)")

                    logger.info(f"Waiting {self.check_interval} seconds until next check...")
                    time.sleep(self.check_interval)

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


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='FIA Documents Scraper Service')
    parser.add_argument(
        'mode',
        choices=['once', 'continuous', 'list', 'test-telegram'],
        help='Run mode: once (single run), continuous (periodic checks), list (show all documents), test-telegram (test Telegram connection)'
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
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
