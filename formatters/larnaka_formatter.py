"""
Telegram post formatter for Larnaka cultural events
"""


def format_larnaka_event_post(event_data):
    """
    Format Larnaka event data for Telegram post

    Args:
        event_data: dict with keys: event_title, event_date, event_time,
                   event_location, summary, event_url

    Returns:
        str: Formatted message for Telegram
    """
    message = "🎭 Культурное событие в Ларнаке\n\n"

    # Event title
    message += f"📌 {event_data.get('event_title', 'Без названия')}\n\n"

    # Date (if available)
    if event_data.get('event_date'):
        date = event_data['event_date']
        # Format date nicely (e.g., "19 января 2025")
        if hasattr(date, 'strftime'):
            month_names_ru = {
                1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
                5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
                9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
            }
            day = date.day
            month = month_names_ru.get(date.month, str(date.month))
            year = date.year
            message += f"📅 Дата: {day} {month} {year}\n"
        else:
            message += f"📅 Дата: {date}\n"

    # Time (if available)
    if event_data.get('event_time'):
        message += f"🕐 Время: {event_data['event_time']}\n"

    # Location (if available)
    if event_data.get('event_location'):
        message += f"📍 Место: {event_data['event_location']}\n"

    # Summary (if available)
    if event_data.get('summary'):
        message += f"\n📝 Описание:\n{event_data['summary']}\n"
    elif event_data.get('event_description'):
        # Fallback to description if no summary
        message += f"\n📝 Описание:\n{event_data['event_description']}\n"

    # Event URL (always last)
    if event_data.get('event_url'):
        message += f"\n🔗 [Подробнее]({event_data['event_url']})"

    return message
