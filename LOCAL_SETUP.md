# Запуск локально на вашем компьютере

## Вариант 1: С локальной PostgreSQL (Полная установка)

### Шаг 1: Установите PostgreSQL

#### macOS:
```bash
# Через Homebrew
brew install postgresql@15
brew services start postgresql@15

# Или скачайте Postgres.app
# https://postgresapp.com/
```

#### Windows:
```bash
# Скачайте установщик
# https://www.postgresql.org/download/windows/
# Запустите установщик и следуйте инструкциям
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Шаг 2: Создайте базу данных

```bash
# Войдите в PostgreSQL
psql -U postgres

# В psql выполните:
CREATE DATABASE fia_documents;
\q
```

### Шаг 3: Настройте .env для локальной БД

Отредактируйте `.env`:

```env
# Локальная база данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=postgres    # или ваш пароль, установленный при установке

# Telegram (уже настроен)
TELEGRAM_BOT_TOKEN=8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA
TELEGRAM_CHAT_ID=-1002701939006

# Настройки
FIA_URL=https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071
CHECK_INTERVAL=3600
```

### Шаг 4: Установите Python зависимости

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 5: Проверьте подключение

```bash
# Проверка базы данных
python test_db_connection.py

# Проверка Telegram
python main.py test-telegram
```

### Шаг 6: Запустите скрипт

```bash
# Однократный запуск
python main.py once

# Непрерывный мониторинг
python main.py continuous

# Просмотр документов
python main.py list
```

---

## Вариант 2: С Docker (Рекомендуется - проще!)

Если у вас установлен Docker, это самый простой способ.

### Шаг 1: Создайте docker-compose.yml

Файл уже может существовать, но вот содержимое:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: fia_documents
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./setup_database.sql:/docker-entrypoint-initdb.d/setup.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-PING", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  scraper:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: fia_documents
      DB_USER: postgres
      DB_PASSWORD: postgres
      TELEGRAM_BOT_TOKEN: 8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA
      TELEGRAM_CHAT_ID: -1002701939006
      FIA_URL: https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071
      CHECK_INTERVAL: 3600
    command: python main.py continuous
    restart: unless-stopped

volumes:
  postgres_data:
```

### Шаг 2: Создайте Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установите зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте код
COPY . .

# Запуск
CMD ["python", "main.py", "continuous"]
```

### Шаг 3: Запустите Docker

```bash
# Запустить всё (БД + скрипт)
docker-compose up -d

# Посмотреть логи
docker-compose logs -f scraper

# Остановить
docker-compose down
```

### Шаг 4: Однократный запуск через Docker

```bash
# Запустить только базу данных
docker-compose up -d postgres

# Подождать несколько секунд для запуска БД
sleep 5

# Запустить скрипт локально (не в Docker)
# Настройте .env:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=postgres

# И запустите
python main.py once
```

---

## Вариант 3: Без PostgreSQL (Только SQLite - для тестирования)

Если вы хотите просто протестировать без установки PostgreSQL, можно использовать SQLite.

### ⚠️ Внимание: Требуется модификация кода

Создайте файл `database_sqlite.py`:

```python
import sqlite3
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = 'fia_documents.db'
        self.connection = None

    def get_connection(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fia_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT NOT NULL,
                document_url TEXT NOT NULL UNIQUE,
                document_hash TEXT NOT NULL,
                file_size INTEGER,
                document_type TEXT,
                season TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_url ON fia_documents(document_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_hash ON fia_documents(document_hash)")

        conn.commit()
        logger.info("SQLite database initialized")

    # ... остальные методы аналогично PostgreSQL версии
```

Затем в `main.py` измените импорт:
```python
# Вместо:
from database import Database
# Используйте:
from database_sqlite import Database
```

**Примечание:** SQLite подходит только для локального тестирования, не для продакшена!

---

## Быстрая проверка локального запуска

### 1. Проверьте, что PostgreSQL запущен:

```bash
# macOS/Linux
pg_isready

# Или проверьте процесс
ps aux | grep postgres

# Windows
# Откройте Services и найдите PostgreSQL
```

### 2. Проверьте подключение к БД:

```bash
python test_db_connection.py
```

Должно показать: ✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!

### 3. Проверьте Telegram:

```bash
python main.py test-telegram
```

Должно прийти сообщение в Telegram.

### 4. Запустите скрипт:

```bash
python main.py once
```

---

## Типичные проблемы при локальном запуске

### PostgreSQL не запускается

**macOS:**
```bash
brew services restart postgresql@15
# или
pg_ctl -D /usr/local/var/postgres start
```

**Linux:**
```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

**Windows:**
- Откройте Services (Win+R → services.msc)
- Найдите PostgreSQL
- Правый клик → Start

### Ошибка "password authentication failed"

Сбросьте пароль:
```bash
# macOS/Linux
sudo -u postgres psql
ALTER USER postgres PASSWORD 'postgres';
\q

# Или создайте нового пользователя
CREATE USER fia_user WITH PASSWORD 'fia_password';
GRANT ALL PRIVILEGES ON DATABASE fia_documents TO fia_user;
```

### Порт 5432 занят

Проверьте, какой процесс использует порт:
```bash
# macOS/Linux
lsof -i :5432

# Windows
netstat -ano | findstr :5432
```

Измените порт в `.env`:
```env
DB_PORT=5433
```

И запустите PostgreSQL на другом порту.

### Ошибка импорта модулей Python

```bash
# Убедитесь, что виртуальное окружение активировано
which python  # должен показать путь в venv/

# Переустановите зависимости
pip install --force-reinstall -r requirements.txt
```

---

## Просмотр данных локально

### Через psql (командная строка):

```bash
psql -U postgres -d fia_documents

# В psql:
SELECT * FROM fia_documents;
\q
```

### Через GUI (графический интерфейс):

**Бесплатные инструменты:**
- **pgAdmin 4** - https://www.pgadmin.org/
- **DBeaver** - https://dbeaver.io/
- **TablePlus** - https://tableplus.com/ (macOS)
- **HeidiSQL** - https://www.heidisql.com/ (Windows)

**Параметры подключения:**
- Host: localhost
- Port: 5432
- Database: fia_documents
- User: postgres
- Password: postgres (или ваш)

---

## Автозапуск при включении компьютера

### macOS (через launchd):

Создайте файл `~/Library/LaunchAgents/com.fia.scraper.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fia.scraper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/main.py</string>
        <string>continuous</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.fia.scraper.plist
```

### Windows (через Task Scheduler):

1. Откройте Task Scheduler
2. Create Basic Task
3. Trigger: "When I log on"
4. Action: "Start a program"
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `C:\path\to\main.py continuous`

### Linux (через systemd):

См. [README.md](README.md#пример-2-запуск-как-systemd-сервис)

---

## Остановка скрипта

```bash
# Если запущен в терминале
Ctrl+C

# Если запущен в фоне
ps aux | grep main.py
kill -9 [PID]

# Docker
docker-compose down
```

---

## Чеклист локального запуска ✅

- [ ] PostgreSQL установлен и запущен
- [ ] База данных `fia_documents` создана
- [ ] Python 3.8+ установлен
- [ ] Виртуальное окружение создано и активировано
- [ ] Зависимости установлены (`pip install -r requirements.txt`)
- [ ] Файл `.env` настроен с локальными параметрами
- [ ] `python test_db_connection.py` показывает ✅
- [ ] `python main.py test-telegram` отправляет сообщение
- [ ] `python main.py once` работает без ошибок

**Готово! Скрипт работает локально! 🎉**

---

## Дополнительные команды

```bash
# Посмотреть все документы
python main.py list

# Очистить логи
> fia_scraper.log

# Очистить базу данных (осторожно!)
psql -U postgres -d fia_documents -c "TRUNCATE TABLE fia_documents RESTART IDENTITY;"

# Создать бэкап
pg_dump -U postgres -d fia_documents > backup_local.sql

# Восстановить из бэкапа
psql -U postgres -d fia_documents < backup_local.sql
```

---

**Нужна помощь?** Проверьте логи: `tail -f fia_scraper.log`
