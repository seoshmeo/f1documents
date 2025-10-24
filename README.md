# FIA Documents Scraper with AI Summaries

Автоматический бот для мониторинга новых документов FIA Formula 1 с AI-генерацией саммари на русском языке.

## 🆕 Новая функция: AI Summaries

Бот теперь автоматически генерирует краткие саммари для каждого нового документа:

```
🏎️ Новый документ FIA

📄 Decision - Car 55 - Track Limits Turn 6

📊 Размер: 234.5 KB
🏁 Сезон: 2025

📝 Краткое содержание:
Стюарды рассмотрели нарушение трековых лимитов
автомобилем №55 (Ferrari) на 6-м повороте...

🔗 Открыть документ
```

**[→ Подробнее об AI Summaries](AI_SUMMARY_README.md)**

---

## ✨ Возможности

- 🔍 **Автоматический мониторинг** сайта FIA на предмет новых документов
- 🤖 **AI-генерация саммари** на русском языке (через Claude Code)
- 🗄️ **PostgreSQL** для хранения документов и саммари
- 📱 **Telegram уведомления** с саммари и ссылкой на документ
- 🎮 **Telegram бот команды** для управления (/interval, /status, /check)
- 🔄 **Динамический интервал** проверки через бот
- 🛡️ **Дедупликация** по URL и хешу содержимого
- 📊 **Graceful degradation** - работает даже если AI недоступен

---

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
docker-compose up -d
docker-compose logs -f scraper
```

**Готово!** PostgreSQL, Python и всё остальное уже настроено.

### Вариант 2: Локально

```bash
# 1. Установка
pip install -r requirements.txt

# 2. Настройка .env
cp .env.example .env
# Отредактируйте .env с вашими данными

# 3. База данных
psql -h localhost -U postgres -d fia_documents -f setup_database.sql
psql -h localhost -U postgres -d fia_documents -f migrations/add_summary_field.sql

# 4. Запуск
python3 run_with_bot.py
```

📖 **Подробные инструкции:** [QUICKSTART.md](QUICKSTART.md)

---

## 🤖 AI Summaries Setup

### Требования:
- Claude Code CLI установлен (`claude` команда)
- Подписка Claude Pro/Max/Code

### Установка:

```bash
# 1. Установить зависимости для PDF
pip install -r requirements.txt

# 2. Обновить базу данных
psql -h localhost -U postgres -d fia_documents -f migrations/add_summary_field.sql

# 3. Проверить Claude Code
claude "тест"
```

**Готово!** Саммари будут генерироваться автоматически.

📖 **Полная документация:** [AI_SUMMARY_SETUP.md](AI_SUMMARY_SETUP.md)

---

## 📱 Telegram Bot Команды

- `/status` - Статус бота и последней проверки
- `/interval <seconds>` - Изменить интервал проверки
- `/check` - Принудительная проверка сейчас
- `/enable` / `/disable` - Включить/выключить автопроверку
- `/settings` - Показать все настройки

📖 **Подробнее:** [BOT_COMMANDS.md](BOT_COMMANDS.md)

---

## 🗂️ Структура проекта

```
fia-documents-scraper/
├── main.py                  # Основной сервис
├── run_with_bot.py          # Запуск с Telegram ботом
├── scraper.py               # Скрапинг FIA сайта
├── database.py              # Работа с PostgreSQL
├── telegram_notifier.py     # Telegram уведомления
├── bot_commands.py          # Команды бота
│
├── pdf_processor.py         # 🆕 Обработка PDF файлов
├── claude_summarizer.py     # 🆕 AI генерация саммари
├── test_summary.py          # 🆕 Тестирование саммари
├── get_my_chat_id.py        # 🆕 Узнать Chat ID
│
├── migrations/              # SQL миграции
│   └── add_summary_field.sql
│
├── .env                     # Конфигурация
├── requirements.txt         # Python зависимости
└── docker-compose.yml       # Docker setup
```

---

## ⚙️ Конфигурация (.env)

```bash
# База данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=your_password

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=group_chat_id           # Группа для документов
TELEGRAM_ADMIN_CHAT_ID=your_personal_id  # Ваш ID для команд/тестов

# Scraper
FIA_URL=https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071
CHECK_INTERVAL=3600  # секунды (1 час)
```

---

## 📊 База данных

### Таблица: `fia_documents`

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Primary key |
| document_name | VARCHAR(500) | Название документа |
| document_url | VARCHAR(1000) | URL (уникальный) |
| document_hash | VARCHAR(64) | SHA256 хеш для дедупликации |
| file_size | BIGINT | Размер файла |
| document_type | VARCHAR(50) | Тип (PDF) |
| season | VARCHAR(20) | Сезон |
| **summary** | **TEXT** | **🆕 AI саммари** |
| created_at | TIMESTAMP | Дата добавления |
| updated_at | TIMESTAMP | Дата обновления |

### Таблица: `bot_settings`

Хранит настройки бота (интервал, состояние, и т.д.)

---

## 🧪 Тестирование

### Тест AI Summary (отправка только вам):

```bash
python3 test_summary.py
```

### Тест Telegram подключения:

```bash
python3 main.py test-telegram
```

### Тест базы данных:

```bash
python3 test_db_connection.py
```

📖 **Инструкции по тестированию:** [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)

---

## 🐳 Docker

```bash
# Запуск
docker-compose up -d

# Логи
docker-compose logs -f scraper

# Остановка
docker-compose down

# Перезапуск
docker-compose restart scraper
```

📖 **Подробнее:** [DOCKER_SETUP.md](DOCKER_SETUP.md)

---

## 📖 Документация

### Основная:
- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт
- [LOCAL_SETUP.md](LOCAL_SETUP.md) - Локальная установка
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker setup
- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Настройка БД
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Настройка Telegram

### AI Summaries:
- **[AI_SUMMARY_README.md](AI_SUMMARY_README.md)** - Обзор функции
- **[AI_SUMMARY_SETUP.md](AI_SUMMARY_SETUP.md)** - Полная документация
- **[SUMMARY_QUICKSTART.md](SUMMARY_QUICKSTART.md)** - Быстрый старт
- **[TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)** - Тестирование

### Справочники:
- [BOT_COMMANDS.md](BOT_COMMANDS.md) - Команды бота
- [SQL_COMMANDS.md](SQL_COMMANDS.md) - SQL команды
- [CHEATSHEET.md](CHEATSHEET.md) - Шпаргалка
- [CHANGELOG.md](CHANGELOG.md) - История изменений

---

## 💰 Стоимость AI Summaries

**$0** при использовании подписки Claude Code!

- Использует вашу подписку Pro/Max/Code
- ~10 документов/месяц
- ~15,000 токенов/документ
- Входит в вашу подписку

---

## 🛠️ Технологии

- **Python 3.11+**
- **PostgreSQL 12+**
- **python-telegram-bot** - Telegram бот
- **BeautifulSoup4** - Парсинг HTML
- **requests** - HTTP запросы
- **PyPDF2 / pdfplumber** - Обработка PDF
- **Claude Code** - AI генерация саммари

---

## 🔒 Безопасность

- Временные PDF удаляются после обработки
- Саммари хранятся в защищённой PostgreSQL
- Никакие данные не передаются третьим лицам (кроме Claude Code)
- Поддержка .env для секретов

---

## 🤝 Вклад

Если нашли баг или есть идея:
1. Создайте issue
2. Или сразу pull request

---

## 📝 Лицензия

MIT License - используйте свободно!

---

## 🏎️ О проекте

Мониторит официальный сайт FIA на предмет новых документов (решения стюардов, технические директивы, штрафы и т.д.) и автоматически отправляет их в Telegram с AI-саммари на русском.

**Сделано с ❤️ для фанатов F1**
