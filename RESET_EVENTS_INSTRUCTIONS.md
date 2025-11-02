# Инструкция по сбросу событий Larnaka

Эта инструкция объясняет как удалить события от 3 ноября и позже, чтобы скрапер заново их обнаружил и отправил с правильными русскими саммари.

## Команды для выполнения на сервере

### Шаг 1: Подключитесь к серверу

```bash
ssh root@161.35.157.202
```

### Шаг 2: Перейдите в директорию проекта и получите изменения

```bash
cd /opt/f1documents
git pull origin main
```

### Шаг 3: Проверьте .env файл

```bash
nano .env
```

Убедитесь что есть:
```
LARNAKA_TELEGRAM_CHAT_ID=-1001974716718
ANTHROPIC_API_KEY=sk-ant-api03-ваш_ключ
```

Сохраните: `Ctrl+X`, `Y`, `Enter`

### Шаг 4: Посмотрите какие события будут удалены

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "SELECT id, title, date FROM larnaka_events WHERE date >= '2024-11-03' ORDER BY date DESC;"
```

### Шаг 5: Удалите события от 3 ноября

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "DELETE FROM larnaka_events WHERE date >= '2024-11-03';"
```

### Шаг 6: Проверьте что события удалены

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "SELECT COUNT(*) FROM larnaka_events WHERE date >= '2024-11-03';"
```

Должно показать `0`

### Шаг 7: Перезапустите scraper

```bash
sudo systemctl restart larnaka-scraper
```

### Шаг 8: Следите за логами

```bash
sudo journalctl -u larnaka-scraper -f
```

Должны увидеть:
- `Found X events` - найдены события
- `New event found` - новое событие
- `Generating AI summary...` - генерация саммари
- `Summary generated` - саммари на русском
- `Successfully sent event to Telegram` - отправлено!

## Что должно получиться

В Telegram группе появятся сообщения на русском:

```
🎭 Культурное событие в Ларнаке

📌 [Название на русском]

📅 Дата: 15 декабря 2024
🕐 Время: 19:00
📍 Место: Муниципальный театр

📝 Описание:
[Краткое описание на русском языке, переведенное Claude AI]

🔗 Подробнее
```

## Проблемы и решения

### Сообщения на греческом вместо русского

Проверьте логи:
```bash
sudo journalctl -u larnaka-scraper -n 50 | grep -i "anthropic\|summary"
```

Должно быть:
```
INFO - Anthropic API key found, summary generation enabled
INFO - Summary generated successfully
```

Если видите `WARNING - ANTHROPIC_API_KEY not found` - проверьте .env

### События не отправляются

Проверьте статус:
```bash
sudo systemctl status larnaka-scraper
sudo journalctl -u larnaka-scraper -n 100
```

## Дополнительные команды

Посмотреть все события:
```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "SELECT id, title, date FROM larnaka_events ORDER BY date DESC LIMIT 10;"
```

Посмотреть статистику:
```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "SELECT COUNT(*) as total, MIN(date) as earliest, MAX(date) as latest FROM larnaka_events;"
```
