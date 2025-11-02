"""
Main script for Larnaka Events Scraper
Monitors Larnaka cultural events calendar and posts to Telegram
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from scrapers.larnaka_scraper import LarnakaScraper
from database.larnaka_database import LarnakaDatabase
from formatters.larnaka_formatter import format_larnaka_event_post
from telegram_notifier import TelegramNotifier
from claude_summarizer import ClaudeSummarizer
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('larnaka_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def process_new_event(event, db, telegram, admin_chat_id):
    """Process a new event: generate summary and send to Telegram"""
    try:
        logger.info(f"Processing new event: {event['title']}")

        # Prepare event description for summary generation
        event_info = f"Событие: {event['title']}\n"
        if event.get('date'):
            event_info += f"Дата: {event['date']}\n"
        if event.get('time'):
            event_info += f"Время: {event['time']}\n"
        if event.get('location'):
            event_info += f"Место: {event['location']}\n"
        if event.get('description'):
            event_info += f"Описание: {event['description']}\n"

        # Generate AI summary
        logger.info("Generating AI summary...")
        summarizer = ClaudeSummarizer()
        summary = None
        if summarizer.is_available():
            summary = summarizer.generate_summary(event_info, "Larnaka Event")
        else:
            logger.warning("Claude summarizer not available")

        if summary:
            logger.info(f"Summary generated: {summary[:100]}...")
            event['summary'] = summary
        else:
            logger.warning("Could not generate summary, using description")
            event['summary'] = event.get('description', '')

        # Insert into database
        event_id = db.insert_event(event)

        if not event_id:
            logger.error("Failed to insert event into database")
            return False

        # Format and send Telegram message
        event_data = {
            'event_title': event['title'],
            'event_date': event.get('date'),
            'event_time': event.get('time', ''),
            'event_location': event.get('location', ''),
            'summary': event.get('summary', ''),
            'event_url': event['url']
        }

        message = format_larnaka_event_post(event_data)

        # Get Larnaka channel chat ID
        larnaka_chat_id = os.getenv('LARNAKA_TELEGRAM_CHAT_ID')

        if not larnaka_chat_id:
            logger.warning("LARNAKA_TELEGRAM_CHAT_ID not set, sending to admin chat")
            larnaka_chat_id = admin_chat_id

        # Send to Larnaka channel
        if telegram.send_message(message, chat_id=larnaka_chat_id):
            logger.info(f"Successfully sent event to Telegram: {event['title']}")
            return True
        else:
            logger.error(f"Failed to send event to Telegram: {event['title']}")
            return False

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return False


def check_for_new_events():
    """Main function to check for new events"""
    logger.info("=== Starting Larnaka Events Check ===")

    try:
        # Initialize components
        scraper = LarnakaScraper(Config.LARNAKA_URL)

        db_config = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        admin_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not set!")
            return

        telegram = TelegramNotifier(bot_token, admin_chat_id)

        # Scrape events
        logger.info("Scraping events from Larnaka website...")
        events = scraper.scrape_events()

        if not events:
            logger.info("No events found on the page")
            return

        logger.info(f"Found {len(events)} events")

        # Process events
        new_events_count = 0

        with LarnakaDatabase(db_config) as db:
            for event in events:
                # Check if event already exists
                if db.event_exists_by_url(event['url']):
                    logger.debug(f"Event already exists (by URL): {event['title']}")
                    continue

                if db.event_exists_by_hash(event['hash']):
                    logger.debug(f"Event already exists (by hash): {event['title']}")
                    continue

                # Process new event
                logger.info(f"New event found: {event['title']}")
                if process_new_event(event, db, telegram, admin_chat_id):
                    new_events_count += 1

                # Be polite to servers
                time.sleep(2)

        logger.info(f"=== Check Complete: {new_events_count} new events processed ===")

    except Exception as e:
        logger.error(f"Error in check_for_new_events: {e}", exc_info=True)


def main():
    """Main entry point"""
    logger.info("Larnaka Events Scraper Started")
    logger.info(f"URL: {Config.LARNAKA_URL}")
    logger.info(f"Check Interval: {Config.LARNAKA_CHECK_INTERVAL} seconds")

    if not Config.LARNAKA_ENABLED:
        logger.warning("Larnaka scraper is DISABLED in config")
        return

    # Run first check immediately
    check_for_new_events()

    # Continue checking at intervals
    while True:
        try:
            logger.info(f"Sleeping for {Config.LARNAKA_CHECK_INTERVAL} seconds...")
            time.sleep(Config.LARNAKA_CHECK_INTERVAL)
            check_for_new_events()

        except KeyboardInterrupt:
            logger.info("Scraper stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)


if __name__ == "__main__":
    main()
