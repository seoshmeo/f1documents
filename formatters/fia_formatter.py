"""
Telegram post formatter for FIA documents
"""


def format_fia_document_post(document_data):
    """
    Format FIA document data for Telegram post

    Args:
        document_data: dict with keys: document_name, file_size, season, summary, document_url

    Returns:
        str: Formatted message for Telegram
    """
    message = "🏎️ Новый документ FIA\n\n"

    # Document name
    message += f"📄 {document_data.get('document_name', 'Unnamed Document')}\n\n"

    # File size (if available)
    if document_data.get('file_size'):
        size_kb = document_data['file_size'] / 1024
        if size_kb > 1024:
            size_mb = size_kb / 1024
            message += f"📊 Размер: {size_mb:.1f} MB\n"
        else:
            message += f"📊 Размер: {size_kb:.1f} KB\n"

    # Season (if available)
    if document_data.get('season'):
        message += f"🏁 Сезон: {document_data['season']}\n"

    # Summary (if available)
    if document_data.get('summary'):
        message += f"\n📝 Краткое содержание:\n{document_data['summary']}\n"

    # Document URL (always last)
    message += f"\n🔗 [Открыть документ]({document_data.get('document_url', '')})"

    return message
