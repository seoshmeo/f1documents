# Быстрый старт

## 🐳 Вариант 1: Docker (1 минута - САМЫЙ ПРОСТОЙ!)

```bash
# Всего 2 команды - и всё работает!
docker-compose up -d
docker-compose logs -f scraper
```

**Готово!** PostgreSQL, Python и всё остальное уже настроено и работает.

📖 Подробнее: [DOCKER_SETUP.md](DOCKER_SETUP.md)

---

## 🚀 Вариант 2: Быстрый скрипт (2 минуты)

```bash
# macOS/Linux
./run_local.sh

# Windows
run_local.bat
```

Скрипт сам:
- Создаст виртуальное окружение
- Установит зависимости
- Проверит подключение к БД
- Запустит программу

📖 Подробнее: [LOCAL_SETUP.md](LOCAL_SETUP.md)

---

## ⚙️ Вариант 3: Ручная настройка (5 минут)

### Шаг 1: Установка зависимостей (1 минута)

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установите библиотеки
pip install -r requirements.txt
```

## Шаг 2: Настройка базы данных (2 минуты)

### Отредактируйте файл `.env`:

```env
# Ваш сервер PostgreSQL
DB_HOST=192.168.1.100        # ← Замените на ваш IP
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres             # ← Ваш пользователь
DB_PASSWORD=your_password    # ← Ваш пароль

# Telegram (уже настроен)
TELEGRAM_BOT_TOKEN=8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA
TELEGRAM_CHAT_ID=-1002701939006

# Настройки скрапера
FIA_URL=https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071
CHECK_INTERVAL=3600
```

### Проверьте подключение:

```bash
python test_db_connection.py
```

**Должно вывести:** ✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!

## Шаг 3: Проверка Telegram (1 минута)

```bash
python main.py test-telegram
```

**Должно прийти сообщение в Telegram канал.**

## Шаг 4: Запуск (1 минута)

### Вариант А: Однократная проверка

```bash
python main.py once
```

### Вариант Б: Непрерывный мониторинг

```bash
python main.py continuous
```

## Готово! 🎉

Теперь при появлении новых документов FIA:
- Они автоматически сохраняются в вашу базу данных
- Вам приходит уведомление в Telegram

---

## Полезные команды

```bash
# Посмотреть все документы в базе
python main.py list

# Проверить логи
tail -f fia_scraper.log

# Остановить непрерывный мониторинг
Ctrl+C
```

---

## Если что-то не работает

### База данных не подключается?

1. Проверьте `.env` - правильные ли данные?
2. Запущен ли PostgreSQL на сервере?
3. Открыт ли порт 5432 в фаерволе?

**Решение:**
```bash
python test_db_connection.py  # Покажет детали ошибки
```

### Telegram не отправляет?

1. Правильный ли токен бота?
2. Добавлен ли бот в канал как администратор?
3. Правильный ли Chat ID?

**Решение:**
```bash
python main.py test-telegram  # Покажет ошибку
```

### Таблица не создается?

```bash
# Создайте вручную через psql:
psql -h your-server -U postgres -d fia_documents -f setup_database.sql
```

---

## Запуск на сервере 24/7

### Вариант 1: Screen (простой)

```bash
# Создайте screen сессию
screen -S fia-scraper

# Запустите скрипт
python main.py continuous

# Отключитесь: Ctrl+A затем D
# Вернуться: screen -r fia-scraper
```

### Вариант 2: Systemd (профессиональный)

См. [README.md](README.md#пример-2-запуск-как-systemd-сервис) для инструкций.

---

## Документация

- 📖 [README.md](README.md) - Полная документация
- 🗄️ [DATABASE_SETUP.md](DATABASE_SETUP.md) - Настройка базы данных
- 📱 [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Настройка Telegram
- 💾 [SQL_COMMANDS.md](SQL_COMMANDS.md) - Полезные SQL команды

---

**Вопросы?** Проверьте логи: `tail -f fia_scraper.log`
