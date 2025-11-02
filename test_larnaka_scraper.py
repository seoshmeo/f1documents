"""
Test script for Larnaka scraper
Tests scraping without database or Telegram
"""

import logging
from scrapers.larnaka_scraper import LarnakaScraper
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test the Larnaka scraper"""
    logger.info("=== Testing Larnaka Scraper ===")
    logger.info(f"URL: {Config.LARNAKA_URL}")

    try:
        # Create scraper
        scraper = LarnakaScraper(Config.LARNAKA_URL)

        # Scrape events
        logger.info("Starting scraping...")
        events = scraper.scrape_events()

        # Display results
        logger.info(f"\n{'='*60}")
        logger.info(f"Found {len(events)} events")
        logger.info(f"{'='*60}\n")

        for i, event in enumerate(events, 1):
            logger.info(f"Event #{i}:")
            logger.info(f"  Title: {event.get('title', 'N/A')}")
            logger.info(f"  Date: {event.get('date', 'N/A')}")
            logger.info(f"  Time: {event.get('time', 'N/A')}")
            logger.info(f"  Location: {event.get('location', 'N/A')}")
            logger.info(f"  Category: {event.get('category', 'N/A')}")
            logger.info(f"  URL: {event.get('url', 'N/A')}")
            logger.info(f"  Hash: {event.get('hash', 'N/A')[:16]}...")
            logger.info(f"  Description: {event.get('description', 'N/A')[:100]}...")
            logger.info("")

        logger.info("=== Test Complete ===")

    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)


if __name__ == "__main__":
    main()
