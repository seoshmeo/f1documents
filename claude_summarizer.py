#!/usr/bin/env python3
"""
Claude Summarizer Module

Generates document summaries using Anthropic API
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ClaudeSummarizer:
    """Generates summaries using Anthropic API"""

    def __init__(self):
        """Initialize Claude Summarizer"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.api_available = bool(self.api_key)

        if not self.api_available:
            logger.warning("ANTHROPIC_API_KEY not found in environment variables")
            logger.warning("Summary generation will be disabled")
        else:
            logger.info("Anthropic API key found, summary generation enabled")

            # Import anthropic only if API key is available
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized successfully")
            except ImportError:
                logger.error("anthropic package not installed. Install with: pip install anthropic")
                self.api_available = False
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {e}")
                self.api_available = False

    def _create_summary_prompt(self, document_text: str, document_name: str) -> str:
        """
        Create prompt for Claude to generate summary

        Args:
            document_text: Full text of the document
            document_name: Name of the document

        Returns:
            Formatted prompt string
        """
        prompt = f"""Проанализируй этот технический документ FIA Formula 1 и создай краткое саммари на русском языке.

Документ: {document_name}

ВАЖНО:
- Саммари должно быть на РУССКОМ языке
- Максимум 5-7 предложений
- Выдели ключевые моменты и изменения
- Укажи какие команды/пилоты затронуты (если применимо)
- Используй технические термины корректно
- Формат: краткий параграф без лишнего форматирования

Текст документа:
---
{document_text[:15000]}
---

Создай краткое саммари этого документа на русском языке:"""

        return prompt

    def generate_summary(self, document_text: str, document_name: str = "FIA Document") -> Optional[str]:
        """
        Generate summary using Anthropic API

        Args:
            document_text: Full text of the document
            document_name: Name of the document

        Returns:
            Generated summary text or None if failed
        """
        if not self.api_available:
            logger.info("Anthropic API not available, skipping summary generation")
            return None

        if not document_text or not document_text.strip():
            logger.warning("Empty document text, cannot generate summary")
            return None

        try:
            logger.info(f"Generating summary for: {document_name}")

            # Create prompt
            prompt = self._create_summary_prompt(document_text, document_name)

            # Call Anthropic API
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fastest and cheapest model
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract summary from response
            if message.content and len(message.content) > 0:
                summary = message.content[0].text.strip()

                if summary:
                    logger.info(f"Summary generated successfully ({len(summary)} chars)")
                    return summary
                else:
                    logger.warning("API returned empty response")
                    return None
            else:
                logger.warning("API returned no content")
                return None

        except Exception as e:
            error_msg = str(e).lower()

            # Check for specific error types
            if any(keyword in error_msg for keyword in ['quota', 'limit', 'billing', 'credit']):
                logger.warning(f"API quota/billing issue: {e}")
            elif 'authentication' in error_msg or 'api key' in error_msg:
                logger.error(f"API authentication error: {e}")
            else:
                logger.error(f"Error generating summary: {e}")

            return None

    def is_available(self) -> bool:
        """
        Check if summarizer is available

        Returns:
            True if Anthropic API is available, False otherwise
        """
        return self.api_available
