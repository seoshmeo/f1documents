# Larnaka Events Scraper Setup

Руководство по настройке и запуску scraper для культурных событий Ларнаки.

## 🎯 Что делает этот scraper?

Автоматически мониторит [календарь культурных событий Ларнаки](https://www.larnaka.org.cy/en/information/cultural-activities-initiatives/events-calendar/) и отправляет новые события в Telegram канал с AI-саммари на русском языке.

---

## 📋 Требования

1. **PostgreSQL база данных** (та же, что используется для FIA)
2. **Telegram бот токен** (можно использовать тот же бот)
3. **Telegram канал** для событий Ларнаки (отдельный от FIA)
4. **Claude Code** для AI-саммари (опционально)
5. **Python 3.11+**

---

## 🚀 Быстрый старт

### Шаг 1: Создать таблицу в базе данных

```bash
# Если PostgreSQL запущен локально
psql -h localhost -U postgres -d fia_documents -f migrations/create_larnaka_events_table.sql

# Если используете Docker
docker exec -i fia_postgres psql -U postgres -d fia_documents < migrations/create_larnaka_events_table.sql
```

### Шаг 2: Настроить .env файл

Добавьте в ваш `.env` файл:

```bash
# Larnaka Events Scraper Configuration
LARNAKA_URL=https://www.larnaka.org.cy/en/information/cultural-activities-initiatives/events-calendar/
LARNAKA_CHECK_INTERVAL=7200  # 2 часа
LARNAKA_ENABLED=true

# Larnaka Telegram Channel
LARNAKA_TELEGRAM_CHAT_ID=your_larnaka_channel_chat_id_here
```

**Как получить Chat ID для канала:**
1. Добавьте бота в ваш канал как администратора
2. Отправьте тестовое сообщение в канал
3. Откройте: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Найдите chat ID в ответе (обычно начинается с `-100`)

### Шаг 3: Тестирование

```bash
# Тест scraper (без БД и Telegram)
python3 test_larnaka_scraper.py

# Должен показать ~20 событий с парсингом всех полей
```

### Шаг 4: Запуск

```bash
# Запустить только Larnaka scraper
python3 main_larnaka.py

# Или запустить оба scraper (FIA + Larnaka) - coming soon
python3 run_both_scrapers.py
```

---

## 📊 Структура базы данных

### Таблица: `larnaka_events`

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Primary key |
| event_title | VARCHAR(500) | Название события |
| event_url | VARCHAR(1000) | URL (уникальный) |
| event_hash | VARCHAR(64) | SHA256 хеш для дедупликации |
| event_date | DATE | Дата события |
| event_time | VARCHAR(100) | Время события |
| event_location | VARCHAR(300) | Место проведения |
| event_description | TEXT | Описание |
| summary | TEXT | AI саммари на русском |
| created_at | TIMESTAMP | Дата добавления |
| updated_at | TIMESTAMP | Дата обновления |

---

## 📱 Формат поста в Telegram

```
🎭 Культурное событие в Ларнаке

📌 «Μνήμες και Όνειρα»

📅 Дата: 7 ноября 2025
🕐 Время: 20:30
📍 Место: ΔΗΜΟΤΙΚΟ ΘΕΑΤΡΟ Γ. ΛΥΚΟΥΡΓΟΣ

📝 Описание:
[AI-генерированное саммари на русском языке о событии]

🔗 Подробнее
```

---

## 🎨 Парсинг данных

Scraper автоматически извлекает:

- ✅ **Название события** (очищено от категорий типа "ΘΕΑΤΡΟ", "ΜΟΥΣΙΚΗ")
- ✅ **Дату** (парсит формат "19Jan" → 2025-01-19)
- ✅ **Время** (например, "20:30" или "19:00–21:00")
- ✅ **Локацию** (ΔΗΜΟΤΙΚΟ ΘΕΑΤΡΟ Γ. ΛΥΚΟΥΡΓΟΣ)
- ✅ **Описание** (если доступно)
- ✅ **Категорию** (ΘΕΑΤΡΟ, ΜΟΥΣΙΚΗ, ΚΙΝΗΜΑΤΟΓΡΑΦΟΣ и т.д.)

---

## 🤖 AI Summaries

### Как это работает:

1. Scraper находит новое событие
2. Загружает детали события (название, дата, время, место, описание)
3. Отправляет данные в Claude Code для генерации саммари
4. Claude создаёт краткое описание на русском (2-3 предложения)
5. Саммари сохраняется в БД и отправляется в Telegram

### Без AI:

Если Claude Code недоступен, scraper всё равно работает:
- Использует оригинальное описание события
- Или показывает только базовую информацию (дата, время, место)

---

## 🔧 Настройка и конфигурация

### Интервал проверки

```bash
# В .env
LARNAKA_CHECK_INTERVAL=7200  # секунды (2 часа = 7200 сек)
```

Рекомендуемые значения:
- **7200** (2 часа) - для production
- **3600** (1 час) - если события добавляются часто
- **600** (10 минут) - для тестирования

### Включить/выключить

```bash
# В .env
LARNAKA_ENABLED=true   # Включить
LARNAKA_ENABLED=false  # Выключить
```

---

## 🧪 Тестирование

### 1. Тест scraper (без БД)
```bash
python3 test_larnaka_scraper.py
```

### 2. Проверка базы данных
```bash
# Подключиться к БД
psql -h localhost -U postgres -d fia_documents

# Посмотреть события
SELECT id, event_title, event_date, event_location FROM larnaka_events ORDER BY created_at DESC LIMIT 10;

# Посчитать события
SELECT COUNT(*) FROM larnaka_events;
```

### 3. Ручной запуск одной проверки
Измените `main_larnaka.py`:
```python
# Закомментируйте while loop
# while True:
#     ...

# Оставьте только
check_for_new_events()
```

---

## 📖 Структура проекта

```
fia-documents-scraper/
│
├── scrapers/
│   ├── fia_scraper.py           # FIA documents scraper
│   └── larnaka_scraper.py       # 🆕 Larnaka events scraper
│
├── database/
│   ├── fia_database.py          # FIA database operations
│   └── larnaka_database.py      # 🆕 Larnaka database operations
│
├── formatters/
│   ├── fia_formatter.py         # FIA Telegram post format
│   └── larnaka_formatter.py     # 🆕 Larnaka Telegram post format
│
├── migrations/
│   ├── add_summary_field.sql
│   └── create_larnaka_events_table.sql  # 🆕
│
├── main.py                      # FIA scraper runner
├── main_larnaka.py              # 🆕 Larnaka scraper runner
├── test_larnaka_scraper.py      # 🆕 Test script
│
├── telegram_notifier.py         # Общий для обоих
├── claude_summarizer.py         # Общий для обоих
└── config.py                    # Общая конфигурация
```

---

## 🔍 Дедупликация

События не добавляются повторно если:

1. **URL совпадает** - событие уже добавлено
2. **Hash совпадает** - содержимое идентично

Hash считается от:
- Название события
- URL
- Дата (строка)
- Время

---

## ❓ FAQ

### Почему события на греческом?
Сайт Ларнаки публикует события на греческом. AI саммари переводит суть на русский.

### Как изменить формат поста?
Отредактируйте `formatters/larnaka_formatter.py`

### Можно ли отправлять в несколько каналов?
Да, измените `main_larnaka.py` и добавьте дополнительные вызовы `telegram.send_message()`

### Как удалить старые события?
```sql
DELETE FROM larnaka_events WHERE event_date < CURRENT_DATE - INTERVAL '30 days';
```

---

## 🐛 Troubleshooting

### Events not being parsed
- Проверьте логи: `tail -f larnaka_scraper.log`
- Возможно изменилась структура сайта
- Запустите `test_larnaka_scraper.py` для отладки

### Database errors
```bash
# Проверить подключение
python3 -c "from database.larnaka_database import LarnakaDatabase; from config import Config; db = LarnakaDatabase({'host': Config.DB_HOST, 'port': Config.DB_PORT, 'database': Config.DB_NAME, 'user': Config.DB_USER, 'password': Config.DB_PASSWORD}); print('Connected!' if db.connect() else 'Failed')"
```

### AI summaries not working
- Проверьте что Claude Code установлен: `claude "test"`
- Scraper продолжит работу без AI, используя оригинальные описания

---

## 📝 Примеры событий

Вот типичные события, которые будут найдены:

- **Театр** (ΘΕΑΤΡΟ) - спектакли и представления
- **Музыка** (ΜΟΥΣΙΚΗ) - концерты и музыкальные вечера
- **Кино** (ΚΙΝΗΜΑΤΟΓΡΑΦΟΣ) - показы фильмов
- **Выставки** (ΕΚΘΕΣΗ) - художественные выставки
- **Лекции** (ΔΙΑΛΕΞΗ) - образовательные мероприятия
- **Ремёсла** (ΧΕΙΡΟΤΕΧΝΙΑ) - ярмарки и мастер-классы

---

## 🎉 Готово!

После настройки scraper будет:
1. ✅ Проверять сайт каждые 2 часа
2. ✅ Находить новые события
3. ✅ Генерировать AI саммари
4. ✅ Отправлять в Telegram канал
5. ✅ Сохранять в базу данных

**Наслаждайтесь автоматическими уведомлениями о культурных событиях Ларнаки!** 🎭
