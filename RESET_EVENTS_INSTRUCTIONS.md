# Инструкция по сбросу событий Larnaka

Эта инструкция объясняет как удалить события от 3 ноября и позже, чтобы скрапер заново их обнаружил и отправил с правильными русскими саммари.

## Быстрый способ (рекомендуется)

```bash
# На сервере
cd /opt/f1documents

# Сделайте скрипт исполняемым
chmod +x reset_larnaka_events.sh

# Запустите скрипт
./reset_larnaka_events.sh
```

Скрипт покажет:
1. Какие события будут удалены
2. Сколько событий будет удалено
3. Попросит подтверждение
4. Удалит события
5. Покажет статистику оставшихся событий

## Ручной способ (через SQL)

### Вариант 1: Предварительный просмотр

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "
SELECT
    id,
    title,
    date,
    created_at
FROM larnaka_events
WHERE date >= '2024-11-03'
ORDER BY date DESC;
"
```

### Вариант 2: Удаление всех событий с 3 ноября

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "
DELETE FROM larnaka_events WHERE date >= '2024-11-03';
"
```

### Вариант 3: Удаление конкретных событий по ID

```bash
# Если хотите удалить конкретные события
docker exec fia_postgres psql -U postgres -d fia_documents -c "
DELETE FROM larnaka_events WHERE id IN (21, 22, 23);
"
```

## После удаления

### 1. Убедитесь что .env настроен правильно

```bash
nano /opt/f1documents/.env
```

Проверьте:
```bash
LARNAKA_TELEGRAM_CHAT_ID=-1001974716718
ANTHROPIC_API_KEY=sk-ant-api03-... # Ваш ключ
```

### 2. Получите последние изменения из GitHub

```bash
cd /opt/f1documents
git pull origin main
```

### 3. Перезапустите скрапер

```bash
sudo systemctl restart larnaka-scraper
```

### 4. Следите за логами

```bash
sudo journalctl -u larnaka-scraper -f
```

Вы должны увидеть:
```
INFO - Found 20 events
INFO - New event found: [название события]
INFO - Generating AI summary...
INFO - Summary generated: [русское описание]...
INFO - Successfully sent event to Telegram: [название]
```

## Проверка в Telegram

В группе Larnaka Events должны появиться сообщения с:
- ✅ Названием на русском (если было на греческом)
- ✅ Описанием на русском
- ✅ Правильным форматированием

## Troubleshooting

### События не появляются

**Проблема:** Скрапер не находит новые события

**Решение:**
```bash
# Проверьте что события действительно удалены
docker exec fia_postgres psql -U postgres -d fia_documents -c "
SELECT COUNT(*) FROM larnaka_events WHERE date >= '2024-11-03';
"

# Должно быть 0
```

### Сообщения все еще на греческом

**Проблема:** ANTHROPIC_API_KEY не настроен или неверный

**Решение:**
```bash
# Проверьте .env
cat /opt/f1documents/.env | grep ANTHROPIC

# Проверьте логи
sudo journalctl -u larnaka-scraper -n 50 | grep -i "anthropic\|summary"
```

Должны видеть:
```
INFO - Anthropic API key found, summary generation enabled
INFO - Generating summary for: [название]
INFO - Summary generated successfully
```

Если видите:
```
WARNING - ANTHROPIC_API_KEY not found in environment variables
WARNING - Summary generation will be disabled
```

Значит ключ не настроен или неверный.

### Scraper не запускается

**Проблема:** Ошибки при запуске

**Решение:**
```bash
# Проверьте статус
sudo systemctl status larnaka-scraper

# Проверьте подробные логи
sudo journalctl -u larnaka-scraper -n 100 --no-pager
```

## Полезные команды

### Посмотреть все события в базе

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "
SELECT id, title, date FROM larnaka_events ORDER BY date DESC LIMIT 10;
"
```

### Посмотреть статистику событий

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "
SELECT
    COUNT(*) as total_events,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(CASE WHEN summary IS NOT NULL AND summary != '' THEN 1 END) as events_with_summary
FROM larnaka_events;
"
```

### Найти события без саммари

```bash
docker exec fia_postgres psql -U postgres -d fia_documents -c "
SELECT id, title, date
FROM larnaka_events
WHERE summary IS NULL OR summary = ''
ORDER BY date DESC;
"
```

## Связанные файлы

- [reset_larnaka_events.sh](reset_larnaka_events.sh) - Скрипт для удаления событий
- [delete_november_events.sql](delete_november_events.sql) - SQL запросы
- [LARNAKA_FIX_SUMMARY.md](LARNAKA_FIX_SUMMARY.md) - Общая информация о фиксе
- [NEXT_STEPS_SERVER.md](NEXT_STEPS_SERVER.md) - Подробная инструкция по настройке
