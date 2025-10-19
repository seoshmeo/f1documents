# SQL команды для работы с базой данных

## Быстрые команды для копирования

### 1. Создание базы данных (если её нет)

```sql
-- Создать базу данных
CREATE DATABASE fia_documents;

-- Подключиться к базе
\c fia_documents
```

### 2. Создание таблицы

```sql
-- Создать таблицу документов
CREATE TABLE IF NOT EXISTS fia_documents (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(500) NOT NULL,
    document_url VARCHAR(1000) NOT NULL UNIQUE,
    document_hash VARCHAR(64) NOT NULL,
    file_size BIGINT,
    document_type VARCHAR(50),
    season VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Создание индексов

```sql
-- Создать индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_document_url ON fia_documents(document_url);
CREATE INDEX IF NOT EXISTS idx_document_hash ON fia_documents(document_hash);
CREATE INDEX IF NOT EXISTS idx_created_at ON fia_documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_season ON fia_documents(season);
```

### 4. Создание триггера для автообновления

```sql
-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер
CREATE TRIGGER update_fia_documents_updated_at
    BEFORE UPDATE ON fia_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Полезные запросы

### Просмотр данных

```sql
-- Показать все документы
SELECT * FROM fia_documents ORDER BY created_at DESC;

-- Показать только последние 10
SELECT * FROM fia_documents ORDER BY created_at DESC LIMIT 10;

-- Подсчитать количество документов
SELECT COUNT(*) as total FROM fia_documents;

-- Последний добавленный документ
SELECT document_name, created_at
FROM fia_documents
ORDER BY created_at DESC
LIMIT 1;
```

### Статистика

```sql
-- Количество документов по сезонам
SELECT season, COUNT(*) as count
FROM fia_documents
GROUP BY season
ORDER BY season;

-- Общий размер всех документов
SELECT
    COUNT(*) as total_documents,
    SUM(file_size) as total_bytes,
    pg_size_pretty(SUM(file_size)::bigint) as total_size
FROM fia_documents;

-- Средний размер документа
SELECT
    pg_size_pretty(AVG(file_size)::bigint) as avg_size
FROM fia_documents
WHERE file_size IS NOT NULL;
```

### Поиск документов

```sql
-- Найти документ по названию
SELECT * FROM fia_documents
WHERE document_name ILIKE '%qualifying%';

-- Найти документы за определенный период
SELECT * FROM fia_documents
WHERE created_at >= '2025-01-01'
ORDER BY created_at DESC;

-- Найти дубликаты по хешу
SELECT document_hash, COUNT(*) as count
FROM fia_documents
GROUP BY document_hash
HAVING COUNT(*) > 1;
```

---

## Управление данными

### Добавление данных

```sql
-- Добавить документ вручную
INSERT INTO fia_documents (document_name, document_url, document_hash, file_size, document_type, season)
VALUES (
    'Test Document',
    'https://example.com/test.pdf',
    'abc123hash',
    1024000,
    'PDF',
    '2025'
);
```

### Обновление данных

```sql
-- Обновить название документа
UPDATE fia_documents
SET document_name = 'New Name'
WHERE id = 1;

-- Обновить сезон для всех документов
UPDATE fia_documents
SET season = '2025'
WHERE season IS NULL;
```

### Удаление данных

```sql
-- Удалить документ по ID
DELETE FROM fia_documents WHERE id = 1;

-- Удалить все документы старше 30 дней
DELETE FROM fia_documents
WHERE created_at < NOW() - INTERVAL '30 days';

-- Очистить всю таблицу (осторожно!)
TRUNCATE TABLE fia_documents RESTART IDENTITY;
```

---

## Техническое обслуживание

### Информация о таблице

```sql
-- Структура таблицы
\d fia_documents

-- Размер таблицы на диске
SELECT pg_size_pretty(pg_total_relation_size('fia_documents')) as table_size;

-- Информация об индексах
\di

-- Количество строк и размер
SELECT
    relname as table_name,
    n_live_tup as row_count,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_stat_user_tables
WHERE relname = 'fia_documents';
```

### Оптимизация

```sql
-- Обновить статистику
ANALYZE fia_documents;

-- Очистить мертвые строки
VACUUM fia_documents;

-- Полная очистка с пересборкой
VACUUM FULL fia_documents;

-- Пересоздать индексы
REINDEX TABLE fia_documents;
```

---

## Права доступа

### Создание пользователя

```sql
-- Создать нового пользователя
CREATE USER fia_user WITH PASSWORD 'secure_password';

-- Дать права на базу данных
GRANT CONNECT ON DATABASE fia_documents TO fia_user;

-- Переключиться на базу
\c fia_documents

-- Дать права на схему
GRANT USAGE ON SCHEMA public TO fia_user;

-- Дать права на таблицу
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE fia_documents TO fia_user;

-- Дать права на sequence (для SERIAL)
GRANT USAGE, SELECT ON SEQUENCE fia_documents_id_seq TO fia_user;

-- PostgreSQL 15+: дополнительные права
GRANT CREATE ON SCHEMA public TO fia_user;
```

### Просмотр прав

```sql
-- Показать права пользователя на таблицу
\dp fia_documents

-- Показать всех пользователей
\du

-- Показать права текущего пользователя
SELECT current_user;
```

---

## Резервное копирование

### Создание бэкапа (через терминал)

```bash
# Полный дамп базы
pg_dump -h localhost -U postgres -d fia_documents -F c -f fia_backup.dump

# Только SQL
pg_dump -h localhost -U postgres -d fia_documents > fia_backup.sql

# Только данные
pg_dump -h localhost -U postgres -d fia_documents --data-only > data_only.sql

# Только схема
pg_dump -h localhost -U postgres -d fia_documents --schema-only > schema_only.sql
```

### Восстановление (через терминал)

```bash
# Из .dump файла
pg_restore -h localhost -U postgres -d fia_documents fia_backup.dump

# Из .sql файла
psql -h localhost -U postgres -d fia_documents < fia_backup.sql
```

### Экспорт в CSV (через psql)

```sql
-- Экспортировать все документы в CSV
\copy (SELECT * FROM fia_documents) TO '/tmp/documents.csv' WITH CSV HEADER;

-- Экспортировать выборку
\copy (SELECT document_name, document_url, created_at FROM fia_documents ORDER BY created_at DESC) TO '/tmp/recent_docs.csv' WITH CSV HEADER;
```

---

## Мониторинг

### Активные подключения

```sql
-- Показать все активные подключения
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'fia_documents';

-- Количество активных подключений
SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'fia_documents';
```

### Производительность

```sql
-- Самые медленные запросы
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%fia_documents%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Статистика по индексам
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'fia_documents';
```

---

## Полезные команды psql

```bash
# Подключиться к базе
psql -h hostname -U username -d database_name

# Команды внутри psql:
\l                    # Список баз данных
\c dbname            # Подключиться к базе
\dt                  # Список таблиц
\d table_name        # Структура таблицы
\di                  # Список индексов
\du                  # Список пользователей
\df                  # Список функций
\dx                  # Список расширений
\q                   # Выход

# Выполнить SQL из файла
\i /path/to/file.sql

# Настройки отображения
\x                   # Переключить расширенный вывод
\timing              # Показывать время выполнения
```

---

## Быстрая настройка (скопировать всё сразу)

```sql
-- 1. Создать базу и подключиться
CREATE DATABASE fia_documents;
\c fia_documents

-- 2. Создать таблицу
CREATE TABLE IF NOT EXISTS fia_documents (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(500) NOT NULL,
    document_url VARCHAR(1000) NOT NULL UNIQUE,
    document_hash VARCHAR(64) NOT NULL,
    file_size BIGINT,
    document_type VARCHAR(50),
    season VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Создать индексы
CREATE INDEX idx_document_url ON fia_documents(document_url);
CREATE INDEX idx_document_hash ON fia_documents(document_hash);
CREATE INDEX idx_created_at ON fia_documents(created_at DESC);
CREATE INDEX idx_season ON fia_documents(season);

-- 4. Создать функцию и триггер
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_fia_documents_updated_at
    BEFORE UPDATE ON fia_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Проверить
\d fia_documents
SELECT COUNT(*) FROM fia_documents;
```

**Готово!** База данных настроена и готова к работе.
