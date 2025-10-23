# Telegram Bot Commands

## Overview

The FIA Documents Scraper now supports Telegram bot commands for dynamic control and monitoring.

## Available Commands

### ⚙️ Interval Management

**`/interval`**
- Show current check interval
- Usage: `/interval`
- Example output:
  ```
  ⏱ Текущий интервал проверки:
  🕐 3600 секунд
  📅 60 минут
  ⏰ 1 часов
  ```

**`/interval <seconds>`**
- Set new check interval
- Usage: `/interval 1800` (30 minutes)
- Minimum: 60 seconds
- Maximum: 86400 seconds (24 hours)
- Changes take effect after current check completes
- Example: `/interval 1800` sets 30-minute interval

### 📊 Status & Statistics

**`/status`**
- Show scraper status, last check time, and document count
- Usage: `/status`
- Example output:
  ```
  ✅ Статус скрапера
  📊 Статус: Включен
  ⏱ Интервал: 3600 сек (60 мин)
  🕐 Последняя проверка: 15 мин. назад
  📄 Документов в БД: 42
  ```

**`/stats`**
- Show document statistics (count, total size, latest document)
- Usage: `/stats`
- Example output:
  ```
  📊 Статистика документов
  📄 Всего документов: 42
  💾 Общий размер: 125.43 MB
  📌 Последний добавленный:
     Doc 58 - Championship Points
     🕐 2025-10-23 12:34:56
  ```

### 🔧 Scraper Control

**`/enable`**
- Enable automatic scraping
- Usage: `/enable`
- Scraper will resume checking at configured interval

**`/disable`**
- Disable automatic scraping
- Usage: `/disable`
- Scraper stops checking until re-enabled
- Bot commands still work

**`/check`**
- Force immediate document check
- Usage: `/check`
- Bypasses current wait interval
- Results sent automatically if new documents found

### 📝 Help

**`/start` or `/help`**
- Show command reference
- Usage: `/start` or `/help`

## Setup

### Running with Bot Commands

The scraper can run in different modes:

1. **Continuous mode** (scraper only, dynamic interval from database):
   ```bash
   python main.py continuous
   ```

2. **Bot + Scraper mode** (recommended):
   ```bash
   python run_with_bot.py
   ```
   or via Docker:
   ```bash
   docker-compose up -d
   ```

### Environment Variables

Ensure these are set in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Database Settings

Settings are stored in the `bot_settings` table:

| Setting Key | Description | Default |
|------------|-------------|---------|
| `check_interval` | Seconds between checks | 3600 |
| `scraper_enabled` | Enable/disable scraping | true |
| `last_check_time` | Unix timestamp of last check | 0 |
| `force_check` | Trigger immediate check | false |

## Security

- Only the configured `TELEGRAM_CHAT_ID` can use bot commands
- Unauthorized users receive no response
- All command attempts are logged

## Examples

### Change interval to 30 minutes
```
/interval 1800
```

### Check status
```
/status
```

### Force immediate check
```
/check
```

### Disable scraping temporarily
```
/disable
```
(Later: `/enable` to resume)

## Architecture

The bot runs in parallel with the scraper:
- **Scraper thread**: Monitors FIA website at configured intervals
- **Bot thread**: Listens for Telegram commands
- Both share the same database for settings
- Interval changes are picked up automatically (no restart needed)

## Logs

All commands are logged to `fia_scraper.log`:
```
2025-10-23 12:00:00 - bot_commands - INFO - Interval updated to 1800 seconds by username
2025-10-23 12:05:00 - bot_commands - INFO - Force check triggered
```
