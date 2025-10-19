# Запуск через Docker

Docker - это самый простой способ запустить проект локально без необходимости устанавливать PostgreSQL и Python зависимости вручную.

## Быстрый старт (3 команды)

```bash
# 1. Соберите и запустите контейнеры
docker-compose up -d

# 2. Посмотрите логи
docker-compose logs -f scraper

# 3. Готово! Скрипт работает
```

---

## Что нужно установить

### Только Docker Desktop:

- **Windows/macOS**: Скачайте [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Установите Docker и Docker Compose:
  ```bash
  sudo apt install docker.io docker-compose
  sudo systemctl start docker
  sudo usermod -aG docker $USER
  ```

Больше ничего не нужно! Ни PostgreSQL, ни Python, ни зависимости.

---

## Структура Docker

Проект запускает 2 контейнера:

1. **postgres** - База данных PostgreSQL 15
2. **scraper** - Python скрипт с нашим кодом

Они автоматически соединены и работают вместе.

---

## Основные команды

### Запуск

```bash
# Запустить в фоновом режиме
docker-compose up -d

# Запустить и смотреть логи
docker-compose up

# Только база данных (без скрипта)
docker-compose up -d postgres
```

### Просмотр логов

```bash
# Все логи
docker-compose logs

# Только скрипта
docker-compose logs scraper

# Только базы данных
docker-compose logs postgres

# В реальном времени (follow)
docker-compose logs -f scraper

# Последние 100 строк
docker-compose logs --tail=100 scraper
```

### Остановка

```bash
# Остановить контейнеры (данные сохраняются)
docker-compose stop

# Остановить и удалить контейнеры (данные в БД сохраняются)
docker-compose down

# Остановить и удалить ВСЁ включая базу данных
docker-compose down -v
```

### Перезапуск

```bash
# Перезапустить всё
docker-compose restart

# Перезапустить только скрипт
docker-compose restart scraper
```

### Статус

```bash
# Показать запущенные контейнеры
docker-compose ps

# Детальная информация
docker ps
```

---

## Настройка переменных окружения

### Вариант 1: Через .env файл (рекомендуется)

Создайте или отредактируйте `.env` в корне проекта:

```env
# Telegram настройки
TELEGRAM_BOT_TOKEN=8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA
TELEGRAM_CHAT_ID=-1002701939006

# Интервал проверки (в секундах)
CHECK_INTERVAL=3600
```

Docker Compose автоматически прочитает эти переменные.

### Вариант 2: Изменить docker-compose.yml

Отредактируйте раздел `environment` в `docker-compose.yml`:

```yaml
environment:
  TELEGRAM_BOT_TOKEN: your_new_token
  TELEGRAM_CHAT_ID: your_new_chat_id
  CHECK_INTERVAL: 1800  # 30 минут
```

---

## Изменение режима работы

По умолчанию запускается режим `continuous` (непрерывный мониторинг).

### Однократный запуск

Измените в `docker-compose.yml`:

```yaml
command: python main.py once
```

Затем:
```bash
docker-compose up scraper
```

### Только показать документы

```yaml
command: python main.py list
```

### Тест Telegram

```yaml
command: python main.py test-telegram
```

---

## Работа с базой данных в Docker

### Подключиться к PostgreSQL из контейнера

```bash
docker-compose exec postgres psql -U postgres -d fia_documents
```

### Подключиться из локального psql

```bash
psql -h localhost -p 5432 -U postgres -d fia_documents
# Пароль: postgres
```

### Выполнить SQL запрос

```bash
docker-compose exec postgres psql -U postgres -d fia_documents -c "SELECT COUNT(*) FROM fia_documents;"
```

### Бэкап базы данных

```bash
# Создать бэкап
docker-compose exec postgres pg_dump -U postgres fia_documents > backup.sql

# Восстановить из бэкапа
docker-compose exec -T postgres psql -U postgres -d fia_documents < backup.sql
```

---

## Просмотр данных через GUI

### Используя TablePlus / DBeaver / pgAdmin

**Параметры подключения:**
- Host: `localhost`
- Port: `5432`
- Database: `fia_documents`
- User: `postgres`
- Password: `postgres`

### Используя Adminer (веб-интерфейс)

Добавьте в `docker-compose.yml`:

```yaml
  adminer:
    image: adminer
    ports:
      - 8080:8080
    networks:
      - fia_network
```

Затем откройте http://localhost:8080 в браузере.

---

## Продвинутое использование

### Сборка без кэша

```bash
docker-compose build --no-cache
```

### Пересоздать контейнеры

```bash
docker-compose up -d --force-recreate
```

### Масштабирование

```bash
# Запустить 3 экземпляра скрипта (не рекомендуется для этого проекта)
docker-compose up -d --scale scraper=3
```

### Посмотреть использование ресурсов

```bash
docker stats
```

### Очистить всё

```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить всё неиспользуемое
docker system prune -a --volumes
```

---

## Отладка

### Зайти в контейнер

```bash
# В скрипт
docker-compose exec scraper bash

# В базу данных
docker-compose exec postgres bash
```

### Запустить команду в контейнере

```bash
# Проверить Python версию
docker-compose exec scraper python --version

# Проверить установленные пакеты
docker-compose exec scraper pip list

# Запустить тест БД
docker-compose exec scraper python test_db_connection.py
```

### Посмотреть логи конкретного файла

```bash
docker-compose exec scraper tail -f fia_scraper.log
```

### Проверить сеть

```bash
docker network ls
docker network inspect fia-documents-scraper_fia_network
```

---

## Обновление кода

После изменения кода Python файлов:

```bash
# Пересобрать образ
docker-compose build scraper

# Перезапустить контейнер
docker-compose up -d --force-recreate scraper
```

---

## Docker на производстве

### Использование с внешней базой данных

Если у вас уже есть PostgreSQL сервер, удалите сервис `postgres` из `docker-compose.yml` и измените настройки:

```yaml
services:
  scraper:
    # ... остальные настройки
    environment:
      DB_HOST: your-external-db-host.com
      DB_PORT: 5432
      DB_NAME: fia_documents
      DB_USER: your_user
      DB_PASSWORD: your_password
```

### Автоматический перезапуск

Уже настроено: `restart: unless-stopped`

Это означает, что контейнеры будут автоматически перезапускаться:
- При сбое
- После перезагрузки сервера
- При любых ошибках

### Логи в файл

```bash
docker-compose logs -f scraper > logs/docker_scraper.log &
```

---

## Мониторинг

### Healthcheck

Контейнер scraper имеет встроенный healthcheck. Проверить статус:

```bash
docker inspect fia_scraper | grep -A 10 Health
```

### Автоматический мониторинг с Watchtower

Добавьте в `docker-compose.yml`:

```yaml
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 300  # Проверка каждые 5 минут
```

---

## Типичные проблемы

### Порт 5432 уже занят

Если у вас уже запущен PostgreSQL локально:

**Решение 1:** Остановите локальный PostgreSQL
```bash
# macOS
brew services stop postgresql

# Linux
sudo systemctl stop postgresql
```

**Решение 2:** Измените порт в `docker-compose.yml`
```yaml
ports:
  - "5433:5432"  # Используем порт 5433 вместо 5432
```

### Контейнер постоянно перезапускается

Посмотрите логи:
```bash
docker-compose logs --tail=50 scraper
```

Скорее всего проблема с подключением к БД или ошибка в коде.

### База данных не создаётся

```bash
# Пересоздать том базы данных
docker-compose down -v
docker-compose up -d
```

### Нет места на диске

Очистите Docker:
```bash
docker system prune -a --volumes
```

---

## Полезные ссылки

- [Docker документация](https://docs.docker.com/)
- [Docker Compose документация](https://docs.docker.com/compose/)
- [PostgreSQL Docker образ](https://hub.docker.com/_/postgres)

---

## Шпаргалка команд

```bash
# Основные
docker-compose up -d              # Запустить в фоне
docker-compose down               # Остановить
docker-compose logs -f scraper    # Смотреть логи
docker-compose restart scraper    # Перезапустить

# Управление
docker-compose ps                 # Статус контейнеров
docker-compose exec scraper bash  # Зайти в контейнер
docker-compose build --no-cache   # Пересобрать

# База данных
docker-compose exec postgres psql -U postgres -d fia_documents
docker-compose exec postgres pg_dump -U postgres fia_documents > backup.sql

# Отладка
docker-compose logs --tail=100 scraper
docker stats
docker system df                  # Использование места
```

**Готово! Docker настроен и работает! 🐳**
