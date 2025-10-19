# Настройка базы данных на сервере

## Быстрая настройка

### Вариант 1: Автоматическое создание таблиц (Рекомендуется)

Если у вас уже есть база данных на сервере, просто укажите параметры подключения в `.env` файле, и скрипт автоматически создаст нужные таблицы при первом запуске.

#### Шаг 1: Настройте файл .env

Откройте файл `.env` и укажите параметры вашего сервера:

```env
# Database Configuration
DB_HOST=your-server-ip-or-hostname    # Например: 192.168.1.100 или db.example.com
DB_PORT=5432                           # Порт PostgreSQL (обычно 5432)
DB_NAME=fia_documents                  # Название базы данных
DB_USER=your_username                  # Ваш пользователь PostgreSQL
DB_PASSWORD=your_password              # Ваш пароль

# Scraper Configuration
FIA_URL=https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071
CHECK_INTERVAL=3600

# Telegram Configuration
TELEGRAM_BOT_TOKEN=8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA
TELEGRAM_CHAT_ID=-1002701939006
```

#### Шаг 2: Запустите скрипт

При первом запуске таблицы создадутся автоматически:

```bash
python main.py once
```

**Готово!** Таблицы созданы и можно работать.

---

### Вариант 2: Ручное создание через SQL скрипт

Если вы хотите создать таблицы вручную или у вас нет прав на автоматическое создание:

#### Шаг 1: Подключитесь к серверу PostgreSQL

```bash
# Локальное подключение к серверу
psql -h your-server-ip -U your_username -d postgres

# Или если вы уже на сервере
psql -U postgres
```

#### Шаг 2: Создайте базу данных (если её еще нет)

```sql
-- Создайте базу данных
CREATE DATABASE fia_documents;

-- Проверьте, что база создана
\l
```

#### Шаг 3: Выполните SQL скрипт

```bash
# Способ 1: Выполнить готовый скрипт
psql -h your-server-ip -U your_username -d fia_documents -f setup_database.sql

# Способ 2: Подключиться и выполнить вручную
psql -h your-server-ip -U your_username -d fia_documents
```

Затем скопируйте и выполните SQL из файла `setup_database.sql`.

---

## Структура таблицы

Будет создана одна таблица `fia_documents`:

```sql
CREATE TABLE fia_documents (
    id SERIAL PRIMARY KEY,                      -- Уникальный ID документа
    document_name VARCHAR(500) NOT NULL,        -- Название документа
    document_url VARCHAR(1000) NOT NULL UNIQUE, -- URL документа (уникальный)
    document_hash VARCHAR(64) NOT NULL,         -- SHA-256 хеш содержимого
    file_size BIGINT,                           -- Размер файла в байтах
    document_type VARCHAR(50),                  -- Тип документа (PDF)
    season VARCHAR(20),                         -- Сезон (2025)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата добавления
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Дата обновления
);
```

### Индексы для быстрого поиска:

```sql
CREATE INDEX idx_document_url ON fia_documents(document_url);
CREATE INDEX idx_document_hash ON fia_documents(document_hash);
CREATE INDEX idx_created_at ON fia_documents(created_at DESC);
CREATE INDEX idx_season ON fia_documents(season);
```

---

## Примеры подключения к разным серверам

### Локальный PostgreSQL

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=your_password
```

### Удаленный сервер

```env
DB_HOST=192.168.1.100
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=fia_user
DB_PASSWORD=secure_password_123
```

### PostgreSQL в Docker

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=postgres
```

### Облачная база (AWS RDS, DigitalOcean, etc.)

```env
DB_HOST=my-postgres-db.c9akciq32.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=admin
DB_PASSWORD=your_cloud_password
```

### Heroku Postgres

```env
# Скопируйте DATABASE_URL из Heroku и разберите на части
DB_HOST=ec2-xxx-xxx-xxx-xxx.compute-1.amazonaws.com
DB_PORT=5432
DB_NAME=d8xxxxxxxxxxxxx
DB_USER=uxxxxxxxxxxxxx
DB_PASSWORD=pxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Проверка подключения

### Способ 1: Через Python скрипт

Создайте файл `test_db.py`:

```python
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

    cursor = connection.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()

    print("✅ Подключение успешно!")
    print(f"PostgreSQL версия: {version[0]}")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
```

Запустите:
```bash
python test_db.py
```

### Способ 2: Через psql

```bash
psql -h your_host -p 5432 -U your_user -d fia_documents -c "SELECT COUNT(*) FROM fia_documents;"
```

### Способ 3: Запустите основной скрипт

```bash
python main.py once
```

Если подключение успешно, вы увидите в логах:
```
Database connection pool created successfully
Database tables created successfully
```

---

## Права доступа

Если вы создаете отдельного пользователя для приложения:

```sql
-- Создайте пользователя
CREATE USER fia_user WITH PASSWORD 'secure_password';

-- Дайте права на базу данных
GRANT ALL PRIVILEGES ON DATABASE fia_documents TO fia_user;

-- Подключитесь к базе
\c fia_documents

-- Дайте права на таблицу
GRANT ALL PRIVILEGES ON TABLE fia_documents TO fia_user;
GRANT USAGE, SELECT ON SEQUENCE fia_documents_id_seq TO fia_user;

-- Дайте права на схему public (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO fia_user;
```

---

## Безопасность

### 1. Настройте фаервол на сервере

```bash
# Разрешите доступ только с определенного IP
sudo ufw allow from YOUR_CLIENT_IP to any port 5432
```

### 2. Настройте pg_hba.conf

Откройте `/etc/postgresql/*/main/pg_hba.conf` и добавьте:

```conf
# Разрешить подключение с определенного IP
host    fia_documents    fia_user    YOUR_CLIENT_IP/32    md5
```

Перезапустите PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 3. Используйте SSL соединение

В `.env` можете добавить:
```python
# В database.py измените подключение:
sslmode='require'
```

### 4. Никогда не публикуйте .env

Добавьте в `.gitignore`:
```
.env
*.log
__pycache__/
```

---

## Резервное копирование

### Создание бэкапа

```bash
# Полный дамп базы данных
pg_dump -h your-server-ip -U your_user -d fia_documents > backup_$(date +%Y%m%d).sql

# Только данные (без схемы)
pg_dump -h your-server-ip -U your_user -d fia_documents --data-only > data_backup.sql

# Только таблица fia_documents
pg_dump -h your-server-ip -U your_user -d fia_documents -t fia_documents > fia_docs_backup.sql
```

### Восстановление из бэкапа

```bash
psql -h your-server-ip -U your_user -d fia_documents < backup_20250101.sql
```

---

## Мониторинг базы данных

### Посмотреть все документы

```sql
SELECT COUNT(*) as total_documents FROM fia_documents;
```

### Последние добавленные документы

```sql
SELECT document_name, created_at
FROM fia_documents
ORDER BY created_at DESC
LIMIT 10;
```

### Статистика по сезонам

```sql
SELECT season, COUNT(*) as count,
       SUM(file_size) as total_size_bytes
FROM fia_documents
GROUP BY season;
```

### Размер таблицы

```sql
SELECT pg_size_pretty(pg_total_relation_size('fia_documents')) as table_size;
```

---

## Устранение проблем

### Ошибка: "connection refused"

**Причина:** PostgreSQL не слушает удаленные подключения

**Решение:**
1. Откройте `postgresql.conf`:
   ```bash
   sudo nano /etc/postgresql/*/main/postgresql.conf
   ```

2. Найдите и измените:
   ```conf
   listen_addresses = '*'  # или ваш конкретный IP
   ```

3. Перезапустите PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```

### Ошибка: "password authentication failed"

**Причина:** Неверный пароль или пользователь

**Решение:**
1. Проверьте `.env` файл
2. Сбросьте пароль:
   ```sql
   ALTER USER your_user WITH PASSWORD 'new_password';
   ```

### Ошибка: "database does not exist"

**Причина:** База данных не создана

**Решение:**
```sql
CREATE DATABASE fia_documents;
```

### Ошибка: "permission denied"

**Причина:** Недостаточно прав

**Решение:**
```sql
GRANT ALL PRIVILEGES ON DATABASE fia_documents TO your_user;
```

---

## Готово!

После настройки базы данных:

1. ✅ Проверьте подключение: `python test_db.py`
2. ✅ Запустите тест Telegram: `python main.py test-telegram`
3. ✅ Запустите однократную проверку: `python main.py once`
4. ✅ Запустите непрерывный мониторинг: `python main.py continuous`

Все документы будут сохраняться на вашем сервере!
