#!/usr/bin/env python3
"""
PDF Processor Module

Downloads and extracts text from PDF documents
"""

import os
import logging
import tempfile
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF downloading and text extraction"""

    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize PDF Processor

        Args:
            session: Optional requests session to reuse connections
        """
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def download_pdf(self, url: str, save_path: Optional[str] = None) -> Optional[str]:
        """
        Download PDF from URL

        Args:
            url: PDF document URL
            save_path: Optional path to save PDF. If not provided, uses temp file

        Returns:
            Path to downloaded PDF file, or None if failed
        """
        try:
            logger.info(f"Downloading PDF from: {url}")

            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            # Use temp file if no path provided
            if not save_path:
                # Create temp file with .pdf extension
                fd, save_path = tempfile.mkstemp(suffix='.pdf', prefix='fia_doc_')
                os.close(fd)  # Close the file descriptor

            # Download PDF
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(save_path)
            logger.info(f"PDF downloaded successfully: {save_path} ({file_size} bytes)")

            return save_path

        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {e}")
            return None

    def extract_text_with_pypdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using PyPDF2

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        try:
            import PyPDF2

            text_parts = []

            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                logger.info(f"Extracting text from {num_pages} pages...")

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

            full_text = '\n\n'.join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")

            return full_text if full_text.strip() else None

        except ImportError:
            logger.warning("PyPDF2 not installed, trying alternative method")
            return None
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return None

    def extract_text_with_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using pdfplumber (better for complex layouts)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        try:
            import pdfplumber

            text_parts = []

            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"Extracting text from {num_pages} pages using pdfplumber...")

                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

            full_text = '\n\n'.join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")

            return full_text if full_text.strip() else None

        except ImportError:
            logger.warning("pdfplumber not installed")
            return None
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            return None

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using available methods

        Tries multiple extraction methods in order of preference:
        1. pdfplumber (best for complex layouts)
        2. PyPDF2 (fallback)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if all methods failed
        """
        # Try pdfplumber first (better quality)
        text = self.extract_text_with_pdfplumber(pdf_path)
        if text:
            return text

        # Fallback to PyPDF2
        text = self.extract_text_with_pypdf(pdf_path)
        if text:
            return text

        logger.error("All text extraction methods failed")
        return None

    def process_pdf(self, url: str) -> Dict[str, Optional[str]]:
        """
        Download PDF and extract text in one call

        Args:
            url: PDF document URL

        Returns:
            Dictionary with 'text' and 'pdf_path' keys
        """
        result = {
            'text': None,
            'pdf_path': None
        }

        try:
            # Download PDF
            pdf_path = self.download_pdf(url)
            if not pdf_path:
                return result

            result['pdf_path'] = pdf_path

            # Extract text
            text = self.extract_text(pdf_path)
            result['text'] = text

            return result

        except Exception as e:
            logger.error(f"Error processing PDF {url}: {e}")
            return result

    def cleanup_temp_file(self, file_path: str):
        """
        Remove temporary PDF file

        Args:
            file_path: Path to file to remove
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not remove temp file {file_path}: {e}")
