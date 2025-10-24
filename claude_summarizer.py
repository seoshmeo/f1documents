#!/usr/bin/env python3
"""
Claude Summarizer Module

Generates document summaries using Claude Code CLI
"""

import os
import logging
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


class ClaudeSummarizer:
    """Generates summaries using Claude Code"""

    def __init__(self):
        """Initialize Claude Summarizer"""
        self.claude_code_available = self._check_claude_code()

    def _check_claude_code(self) -> bool:
        """
        Check if Claude Code CLI is available

        Returns:
            True if claude command is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['which', 'claude'],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0

            if available:
                logger.info(f"Claude Code found at: {result.stdout.strip()}")
            else:
                logger.warning("Claude Code CLI not found in PATH")

            return available

        except Exception as e:
            logger.warning(f"Error checking for Claude Code: {e}")
            return False

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
        Generate summary using Claude Code

        Args:
            document_text: Full text of the document
            document_name: Name of the document

        Returns:
            Generated summary text or None if failed
        """
        if not self.claude_code_available:
            logger.info("Claude Code not available, skipping summary generation")
            return None

        if not document_text or not document_text.strip():
            logger.warning("Empty document text, cannot generate summary")
            return None

        try:
            logger.info(f"Generating summary for: {document_name}")

            # Create prompt
            prompt = self._create_summary_prompt(document_text, document_name)

            # Save prompt to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                prompt_file = f.name
                f.write(prompt)

            try:
                # Call Claude Code CLI
                # Using --quiet flag to get only the response without extra output
                result = subprocess.run(
                    ['claude', '--quiet', prompt],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutes timeout
                )

                # Clean up prompt file
                os.unlink(prompt_file)

                if result.returncode == 0:
                    summary = result.stdout.strip()

                    if summary:
                        logger.info(f"Summary generated successfully ({len(summary)} chars)")
                        return summary
                    else:
                        logger.warning("Claude Code returned empty response")
                        return None
                else:
                    # Check if it's a quota/subscription error
                    error_msg = result.stderr.strip()

                    if any(keyword in error_msg.lower() for keyword in ['quota', 'limit', 'subscription', 'billing']):
                        logger.warning(f"Claude Code quota/subscription issue: {error_msg}")
                    else:
                        logger.error(f"Claude Code error (code {result.returncode}): {error_msg}")

                    return None

            except subprocess.TimeoutExpired:
                logger.error("Claude Code request timed out after 120 seconds")
                os.unlink(prompt_file)
                return None

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    def is_available(self) -> bool:
        """
        Check if summarizer is available

        Returns:
            True if Claude Code is available, False otherwise
        """
        return self.claude_code_available
