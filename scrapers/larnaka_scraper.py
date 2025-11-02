import requests
from bs4 import BeautifulSoup
import hashlib
import logging
from urllib.parse import urljoin
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LarnakaScraper:
    """Scraper for Larnaka cultural events calendar"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8'
        })

    def fetch_page(self):
        """Fetch the Larnaka events calendar page"""
        try:
            logger.info(f"Fetching page: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            raise

    def parse_date(self, date_str):
        """Parse date string from the page (e.g., '19Jan' or 'DDMon')"""
        try:
            if not date_str:
                return None

            # Handle format like "19Jan"
            # Extract day and month
            match = re.match(r'(\d+)(\w+)', date_str.strip())
            if match:
                day = match.group(1)
                month_str = match.group(2)

                # Get current date
                current_date = datetime.now()
                current_year = current_date.year

                # Try to parse month from Greek or English abbreviation
                month_map_en = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                month_map_gr = {
                    'Ιαν': 1, 'Φεβ': 2, 'Μαρ': 3, 'Απρ': 4, 'Μαϊ': 5, 'Ιουν': 6,
                    'Ιουλ': 7, 'Αυγ': 8, 'Σεπ': 9, 'Οκτ': 10, 'Νοε': 11, 'Δεκ': 12
                }

                month = month_map_en.get(month_str[:3]) or month_map_gr.get(month_str[:3])

                if month:
                    try:
                        event_date = datetime(current_year, month, int(day))

                        # If the event is more than 30 days in the past, assume it's for next year
                        # This handles events at the beginning of the year when we're at the end
                        days_diff = (current_date - event_date).days
                        if days_diff > 30:
                            event_date = datetime(current_year + 1, month, int(day))

                        # If event is more than 365 days in the future, it's probably current year
                        # This fixes the issue where Jan events show as next year when we're in Nov
                        days_ahead = (event_date - current_date).days
                        if days_ahead > 365:
                            event_date = datetime(current_year, month, int(day))

                        return event_date.date()
                    except ValueError:
                        logger.warning(f"Invalid date values: day={day}, month={month}, year={current_year}")
                        return None

            return None
        except Exception as e:
            logger.warning(f"Error parsing date '{date_str}': {e}")
            return None

    def parse_events(self, html_content):
        """Parse HTML and extract events"""
        soup = BeautifulSoup(html_content, 'lxml')
        events = []

        # Find the MEC events container
        mec_container = soup.find('div', id='mec_skin_15101')

        if not mec_container:
            logger.warning("Could not find MEC events container")
            # Try alternative selectors
            mec_container = soup.find('div', class_=re.compile(r'mec-wrap'))

        if not mec_container:
            logger.error("Could not find events container on page")
            return events

        # Find all event articles
        event_articles = mec_container.find_all('article', class_='mec-event-article')

        logger.info(f"Found {len(event_articles)} event articles")

        for article in event_articles:
            try:
                event = self._parse_single_event(article)
                if event:
                    events.append(event)
            except Exception as e:
                logger.warning(f"Error parsing event article: {e}")
                continue

        logger.info(f"Successfully parsed {len(events)} events")
        return events

    def _parse_single_event(self, article):
        """Parse a single event article"""
        event = {}

        # Find the link (contains most information)
        link = article.find('a', href=True)
        if not link:
            logger.warning("No link found in event article")
            return None

        # Get URL
        event_url = link.get('href')
        if event_url:
            if not event_url.startswith('http'):
                event_url = urljoin(self.base_url, event_url)
            event['url'] = event_url
        else:
            return None

        # Get title (clean it from category labels)
        title_elem = article.find('h4', class_='mec-event-title')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # Remove category labels from title (e.g., "ΘΕΑΤΡΟ", "ΜΟΥΣΙΚΗ", etc.)
            # These are usually in ALL CAPS at the end, sometimes combined
            title_text = re.sub(r'(ΘΕΑΤΡΟ|ΜΟΥΣΙΚΗ|ΚΙΝΗΜΑΤΟΓΡΑΦΟΣ|ΕΚΘΕΣΗ|ΧΕΙΡΟΤΕΧΝΙΑ|ΔΙΑΛΕΞΗ|ΧΟΡΟΣ|ΤΕΧΝΗ|Ongoing)+$', '', title_text)
            event['title'] = title_text.strip()
        else:
            # Fallback: try to get any h4
            title_elem = article.find('h4')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                title_text = re.sub(r'(ΘΕΑΤΡΟ|ΜΟΥΣΙΚΗ|ΚΙΝΗΜΑΤΟΓΡΑΦΟΣ|ΕΚΘΕΣΗ|ΧΕΙΡΟΤΕΧΝΙΑ|ΔΙΑΛΕΞΗ|ΧΟΡΟΣ|ΤΕΧΝΗ|Ongoing)+$', '', title_text)
                event['title'] = title_text.strip()
            else:
                event['title'] = 'Untitled Event'

        # Get date
        date_elem = article.find('span', class_='mec-event-day')
        if not date_elem:
            date_elem = article.find('div', class_='mec-event-date')

        if date_elem:
            date_str = date_elem.get_text(strip=True)
            event['date'] = self.parse_date(date_str)
            event['date_string'] = date_str
        else:
            event['date'] = None
            event['date_string'] = ''

        # Get time
        time_elem = article.find('div', class_='mec-time-details')
        if not time_elem:
            time_elem = article.find('span', class_='mec-event-time')

        if time_elem:
            event['time'] = time_elem.get_text(strip=True)
        else:
            event['time'] = ''

        # Get location (try multiple selectors)
        location_elem = article.find('div', class_='mec-event-location')
        if not location_elem:
            location_elem = article.find('span', class_='mec-event-place')
        if not location_elem:
            location_elem = article.find('div', class_='mec-local-time-details')
        if not location_elem:
            # Try to find location in the description
            location_elem = article.find('div', class_='mec-venue-description')

        if location_elem:
            location_text = location_elem.get_text(strip=True)
            event['location'] = location_text
        else:
            # Try to extract from description
            desc_elem = article.find('div', class_='mec-event-detail')
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                # Look for location patterns (usually starts with capital letters)
                location_match = re.search(r'([Α-ΩA-Z][Α-ΩA-Zα-ωa-z\s\.]+(?:ΘΕΑΤΡΟ|ΠΙΝΑΚΟΘΗΚΗ|ΚΕΝΤΡΟ|ΠΛΑΤΕΙΑ)[^,]*)', desc_text)
                if location_match:
                    event['location'] = location_match.group(1).strip()
                else:
                    event['location'] = ''
            else:
                event['location'] = ''

        # Get description/category
        category_elem = article.find('div', class_='mec-event-label')
        if not category_elem:
            category_elem = article.find('span', class_='mec-event-label')

        if category_elem:
            event['category'] = category_elem.get_text(strip=True)
        else:
            event['category'] = ''

        # Get full description from event detail if available
        detail_elem = article.find('div', class_='mec-event-detail')
        if detail_elem:
            event['description'] = detail_elem.get_text(strip=True)
        else:
            # Build description from available info
            parts = []
            if event.get('category'):
                parts.append(event['category'])
            if event.get('location'):
                parts.append(event['location'])
            event['description'] = ' - '.join(parts) if parts else ''

        logger.debug(f"Parsed event: {event['title']}")
        return event

    def calculate_event_hash(self, event):
        """Calculate hash of event content for deduplication"""
        try:
            # Create a unique string from event data
            hash_content = f"{event.get('title', '')}|{event.get('url', '')}|{event.get('date_string', '')}|{event.get('time', '')}"
            event_hash = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
            logger.debug(f"Hash calculated for '{event.get('title', '')}': {event_hash}")
            return event_hash
        except Exception as e:
            logger.warning(f"Error calculating hash: {e}")
            # Fallback: hash the URL
            return hashlib.sha256(event.get('url', '').encode('utf-8')).hexdigest()

    def scrape_events(self):
        """Main method to scrape all events from the page"""
        try:
            # Fetch page
            html_content = self.fetch_page()

            # Parse events
            events = self.parse_events(html_content)

            # Enrich with hash
            enriched_events = []

            for event in events:
                try:
                    # Calculate hash for deduplication
                    event_hash = self.calculate_event_hash(event)

                    enriched_event = {
                        'title': event.get('title', ''),
                        'url': event.get('url', ''),
                        'hash': event_hash,
                        'date': event.get('date'),
                        'time': event.get('time', ''),
                        'location': event.get('location', ''),
                        'description': event.get('description', ''),
                        'category': event.get('category', '')
                    }

                    enriched_events.append(enriched_event)

                except Exception as e:
                    logger.error(f"Error enriching event {event.get('url', '')}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(enriched_events)} events")
            return enriched_events

        except Exception as e:
            logger.error(f"Error in scrape_events: {e}")
            raise
