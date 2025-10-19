FROM python:3.11-slim

# Метаданные
LABEL maintainer="FIA Documents Scraper"
LABEL description="Scraper for FIA Formula One documents with PostgreSQL and Telegram notifications"

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для логов
RUN mkdir -p /app/logs

# Здоровье контейнера
HEALTHCHECK --interval=60s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import psycopg2; import os; psycopg2.connect(host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD')).close()" || exit 1

# Точка входа
CMD ["python", "main.py", "continuous"]
