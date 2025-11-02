import requests
from bs4 import BeautifulSoup
import hashlib
import logging
import re
from urllib.parse import urljoin, urlparse
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FIAScraper:
    """Scraper for FIA documents website"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def fetch_page(self):
        """Fetch the FIA documents page"""
        try:
            logger.info(f"Fetching page: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            raise

    def parse_documents(self, html_content):
        """Parse HTML and extract PDF document links"""
        soup = BeautifulSoup(html_content, 'lxml')
        documents = []

        # Find all links that point to PDF files
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))

        logger.info(f"Found {len(pdf_links)} PDF links on the page")

        for link in pdf_links:
            try:
                pdf_url = link.get('href')

                # Make URL absolute if it's relative
                if pdf_url:
                    if not pdf_url.startswith('http'):
                        pdf_url = urljoin(self.base_url, pdf_url)

                    # Get document name
                    document_name = link.get_text(strip=True)

                    # If no text in link, try to get from URL
                    if not document_name:
                        document_name = pdf_url.split('/')[-1]

                    documents.append({
                        'name': document_name,
                        'url': pdf_url
                    })

            except Exception as e:
                logger.warning(f"Error parsing link: {e}")
                continue

        # Also search for PDF links in other possible structures
        # Some sites use data attributes or JavaScript
        for element in soup.find_all(attrs={'data-document-url': True}):
            try:
                pdf_url = element.get('data-document-url')
                if pdf_url and pdf_url.lower().endswith('.pdf'):
                    if not pdf_url.startswith('http'):
                        pdf_url = urljoin(self.base_url, pdf_url)

                    document_name = element.get_text(strip=True) or pdf_url.split('/')[-1]

                    if not any(doc['url'] == pdf_url for doc in documents):
                        documents.append({
                            'name': document_name,
                            'url': pdf_url
                        })
            except Exception as e:
                logger.warning(f"Error parsing data attribute: {e}")
                continue

        # Look for document tables or lists
        document_sections = soup.find_all(['table', 'div'], class_=re.compile(r'document|file|download', re.IGNORECASE))

        for section in document_sections:
            links = section.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
            for link in links:
                try:
                    pdf_url = link.get('href')
                    if pdf_url:
                        if not pdf_url.startswith('http'):
                            pdf_url = urljoin(self.base_url, pdf_url)

                        document_name = link.get_text(strip=True) or pdf_url.split('/')[-1]

                        # Avoid duplicates
                        if not any(doc['url'] == pdf_url for doc in documents):
                            documents.append({
                                'name': document_name,
                                'url': pdf_url
                            })
                except Exception as e:
                    logger.warning(f"Error parsing section link: {e}")
                    continue

        logger.info(f"Total unique PDF documents found: {len(documents)}")
        return documents

    def get_document_metadata(self, document_url):
        """Get metadata about a PDF document without downloading it"""
        try:
            # Send HEAD request to get file info
            response = self.session.head(document_url, timeout=30, allow_redirects=True)

            metadata = {
                'size': None,
                'content_type': None
            }

            if response.status_code == 200:
                metadata['size'] = response.headers.get('Content-Length')
                metadata['content_type'] = response.headers.get('Content-Type')

                if metadata['size']:
                    metadata['size'] = int(metadata['size'])

            return metadata

        except Exception as e:
            logger.warning(f"Could not fetch metadata for {document_url}: {e}")
            return {'size': None, 'content_type': None}

    def calculate_document_hash(self, document_url):
        """Calculate hash of document content"""
        try:
            logger.info(f"Calculating hash for: {document_url}")

            # Download first 1MB to calculate hash (enough for uniqueness)
            response = self.session.get(
                document_url,
                timeout=30,
                stream=True,
                headers={'Range': 'bytes=0-1048576'}
            )

            if response.status_code in [200, 206]:
                content = response.content
                document_hash = hashlib.sha256(content).hexdigest()
                logger.info(f"Hash calculated: {document_hash}")
                return document_hash
            else:
                logger.warning(f"Could not download document for hashing: {response.status_code}")
                # Fallback: hash the URL
                return hashlib.sha256(document_url.encode()).hexdigest()

        except Exception as e:
            logger.warning(f"Error calculating hash for {document_url}: {e}")
            # Fallback: hash the URL
            return hashlib.sha256(document_url.encode()).hexdigest()

    def scrape_documents(self):
        """Main method to scrape all documents from the page"""
        try:
            # Fetch page
            html_content = self.fetch_page()

            # Parse documents
            documents = self.parse_documents(html_content)

            # Enrich with metadata and hash
            enriched_documents = []

            for doc in documents:
                try:
                    # Get metadata
                    metadata = self.get_document_metadata(doc['url'])

                    # Calculate hash
                    doc_hash = self.calculate_document_hash(doc['url'])

                    enriched_doc = {
                        'name': doc['name'],
                        'url': doc['url'],
                        'hash': doc_hash,
                        'size': metadata['size'],
                        'type': 'PDF',
                        'season': '2025'
                    }

                    enriched_documents.append(enriched_doc)

                    # Be polite to the server
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error enriching document {doc['url']}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(enriched_documents)} documents")
            return enriched_documents

        except Exception as e:
            logger.error(f"Error in scrape_documents: {e}")
            raise

    def download_document(self, document_url, save_path):
        """Download a PDF document to local file system"""
        try:
            logger.info(f"Downloading: {document_url}")

            response = self.session.get(document_url, timeout=60, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Document downloaded successfully: {save_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading document: {e}")
            return False
