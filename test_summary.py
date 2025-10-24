#!/usr/bin/env python3
"""
Test Summary Generation

Скачивает случайный FIA документ, генерирует саммари и отправляет в личный Telegram
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from claude_summarizer import ClaudeSummarizer
from telegram_notifier import TelegramNotifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def get_personal_chat_id():
    """Get personal chat ID from environment"""
    # Для личного тестирования используем TELEGRAM_ADMIN_CHAT_ID или попросим ввести
    admin_chat = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

    if admin_chat:
        logger.info(f"Используется TELEGRAM_ADMIN_CHAT_ID: {admin_chat}")
        return admin_chat

    # Если нет - попросим ввести
    print("\n" + "="*60)
    print("Чтобы получить ваш Chat ID:")
    print("1. Напишите боту @userinfobot в Telegram")
    print("2. Он пришлёт ваш Chat ID")
    print("="*60)

    chat_id = input("Введите ваш личный Chat ID: ").strip()
    return chat_id


def test_summary_generation(test_pdf_url=None, personal_chat_id=None):
    """
    Test summary generation with a FIA document

    Args:
        test_pdf_url: URL to test PDF (if None, will use example)
        personal_chat_id: Your personal Telegram chat ID
    """

    logger.info("="*60)
    logger.info("ТЕСТ ГЕНЕРАЦИИ САММАРИ")
    logger.info("="*60)

    # Get personal chat ID if not provided
    if not personal_chat_id:
        personal_chat_id = get_personal_chat_id()
        if not personal_chat_id:
            logger.error("Chat ID не указан!")
            return False

    # Use test PDF URL or ask for one
    if not test_pdf_url:
        print("\nВведите URL FIA документа для теста")
        print("(или нажмите Enter для использования тестового документа)")
        user_input = input("PDF URL: ").strip()

        if user_input:
            test_pdf_url = user_input
        else:
            # Пример - последний документ с FIA (нужно будет обновить на реальный)
            test_pdf_url = "https://www.fia.com/sites/default/files/decision-document/2024%20United%20States%20Grand%20Prix%20-%20Offence%20-%20Car%2055%20-%20Impeding.pdf"
            logger.info(f"Используется тестовый URL: {test_pdf_url}")

    # Initialize components
    logger.info("\n1. Инициализация компонентов...")
    pdf_processor = PDFProcessor()
    summarizer = ClaudeSummarizer()

    # Check Claude Code availability
    if not summarizer.is_available():
        logger.error("❌ Claude Code недоступен!")
        logger.error("Убедитесь что команда 'claude' работает: claude 'тест'")
        return False

    logger.info("✓ Claude Code доступен")

    # Download and process PDF
    logger.info(f"\n2. Скачивание и обработка PDF...")
    logger.info(f"   URL: {test_pdf_url}")

    result = pdf_processor.process_pdf(test_pdf_url)
    pdf_path = result.get('pdf_path')
    pdf_text = result.get('text')

    if not pdf_text:
        logger.error("❌ Не удалось извлечь текст из PDF")
        if pdf_path:
            pdf_processor.cleanup_temp_file(pdf_path)
        return False

    logger.info(f"✓ Текст извлечён: {len(pdf_text)} символов")

    # Generate summary
    logger.info("\n3. Генерация саммари через Claude Code...")
    logger.info("   (это может занять 10-30 секунд)")

    document_name = test_pdf_url.split('/')[-1].replace('.pdf', '')
    summary = summarizer.generate_summary(pdf_text, document_name)

    # Cleanup PDF
    if pdf_path:
        pdf_processor.cleanup_temp_file(pdf_path)

    if not summary:
        logger.error("❌ Не удалось сгенерировать саммари")
        logger.error("   Проверьте квоту Claude Code или логи выше")
        return False

    logger.info("✓ Саммари сгенерировано!")
    logger.info("\n" + "="*60)
    logger.info("САММАРИ:")
    logger.info("="*60)
    print(summary)
    logger.info("="*60)

    # Send to Telegram
    logger.info("\n4. Отправка в ваш личный Telegram...")

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return False

    # Create notifier with personal chat ID
    telegram = TelegramNotifier(bot_token=bot_token, chat_id=personal_chat_id)

    # Create test document dict
    test_doc = {
        'name': f'[ТЕСТ] {document_name}',
        'url': test_pdf_url,
        'size': len(pdf_text),
        'season': '2024/2025',
        'summary': summary
    }

    success = telegram.notify_new_document(test_doc)

    if success:
        logger.info("✓ Сообщение отправлено в ваш Telegram!")
        logger.info(f"   Chat ID: {personal_chat_id}")
    else:
        logger.error("❌ Не удалось отправить сообщение")
        logger.error("   Проверьте:")
        logger.error("   - Правильность Chat ID")
        logger.error("   - Начали ли вы диалог сботом")
        return False

    logger.info("\n" + "="*60)
    logger.info("✅ ТЕСТ УСПЕШНО ЗАВЕРШЁН!")
    logger.info("="*60)

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Test AI Summary Generation')
    parser.add_argument(
        '--pdf-url',
        help='URL FIA документа для теста',
        default=None
    )
    parser.add_argument(
        '--chat-id',
        help='Ваш личный Telegram Chat ID',
        default=None
    )

    args = parser.parse_args()

    try:
        success = test_summary_generation(
            test_pdf_url=args.pdf_url,
            personal_chat_id=args.chat_id
        )

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\nТест прерван пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\n❌ Ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
