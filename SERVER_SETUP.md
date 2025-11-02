# Server Setup Instructions

Инструкции по настройке FIA Documents Scraper на production сервере.

## Важные настройки .env

После клонирования репозитория и перед запуском, убедитесь что `.env` файл содержит правильные настройки:

### Database Configuration

```bash
# Для подключения к PostgreSQL в Docker контейнере из хост-системы
DB_HOST=localhost
DB_PORT=5433  # или 5432, в зависимости от вашей конфигурации Docker
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=your_actual_password
```

**ВАЖНО:** `DB_HOST` должен быть `localhost`, НЕ `postgres`!
- `postgres` работает только внутри Docker сети
- Для подключения с хост-системы используйте `localhost`

### Проверка портов PostgreSQL

Найдите на каком порту работает ваш PostgreSQL контейнер:

```bash
docker ps | grep postgres
```

Ищите строку типа:
```
127.0.0.1:5433->5432/tcp    fia_postgres
```

Используйте порт слева (5433 в примере) в настройке `DB_PORT`.

### Telegram Configuration

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# FIA Documents Channel
FIA_TELEGRAM_CHAT_ID=your_fia_channel_chat_id

# Larnaka Events Channel
LARNAKA_TELEGRAM_CHAT_ID=your_larnaka_channel_chat_id

# Admin Chat (for bot commands)
TELEGRAM_ADMIN_CHAT_ID=your_personal_chat_id
```

### AI Summary (Optional)

```bash
# Для генерации AI саммари на русском языке
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Если не указан, скраперы будут работать без AI саммари.

## Systemd Services

Сервисы должны использовать Python из виртуального окружения:

```ini
ExecStart=/opt/f1documents/venv/bin/python main.py continuous
ExecStart=/opt/f1documents/venv/bin/python main_larnaka.py
```

## Troubleshooting

### "could not translate host name postgres"

❌ **Неправильно:**
```bash
DB_HOST=postgres
```

✅ **Правильно:**
```bash
DB_HOST=localhost
```

### "Connection refused" на порту 5432

Проверьте что используете правильный порт:
```bash
docker ps | grep postgres
# Используйте внешний порт (127.0.0.1:XXXX->5432)
```

### Scrapers постоянно перезапускаются

Смотрите логи:
```bash
tail -f fia_scraper.log
tail -f larnaka_scraper.log
sudo journalctl -u fia-scraper -f
sudo journalctl -u larnaka-scraper -f
```

## Обновление кода с GitHub

```bash
cd /opt/f1documents
sudo systemctl stop fia-scraper larnaka-scraper
git pull origin main
sudo systemctl start fia-scraper larnaka-scraper
sudo systemctl status fia-scraper larnaka-scraper
```
