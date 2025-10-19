#!/bin/bash

###############################################################################
# FIA Documents Scraper - Локальный запуск
# Скрипт для быстрого запуска проекта локально
###############################################################################

set -e  # Остановить при ошибке

echo "=========================================="
echo "  FIA Documents Scraper - Локальный запуск"
echo "=========================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка Python
echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 не установлен!"
    exit 1
fi
success "Python $(python3 --version) найден"

# Проверка PostgreSQL
echo "Проверка PostgreSQL..."
if command -v psql &> /dev/null; then
    success "PostgreSQL найден"
else
    warning "PostgreSQL не найден в PATH"
    echo "Если у вас установлен PostgreSQL, убедитесь что он запущен"
fi

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo ""
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    success "Виртуальное окружение создано"
else
    success "Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
echo ""
echo "Активация виртуального окружения..."
source venv/bin/activate
success "Виртуальное окружение активировано"

# Установка зависимостей
echo ""
echo "Установка зависимостей..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
success "Зависимости установлены"

# Проверка .env файла
echo ""
if [ ! -f ".env" ]; then
    warning ".env файл не найден"
    echo "Создание .env из .env.example..."
    cp .env.example .env
    echo ""
    error "ВАЖНО: Отредактируйте файл .env с вашими настройками!"
    echo "Особенно проверьте:"
    echo "  - DB_HOST (localhost для локального запуска)"
    echo "  - DB_PASSWORD"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHAT_ID"
    echo ""
    read -p "Нажмите Enter когда отредактируете .env..."
else
    success ".env файл найден"
fi

# Проверка подключения к базе данных
echo ""
echo "Проверка подключения к базе данных..."
if python test_db_connection.py; then
    success "Подключение к базе данных успешно"
else
    error "Не удалось подключиться к базе данных"
    echo ""
    echo "Возможные решения:"
    echo "1. Убедитесь что PostgreSQL запущен"
    echo "2. Проверьте настройки в .env файле"
    echo "3. Создайте базу данных: createdb -U postgres fia_documents"
    echo ""
    read -p "Исправить и попробовать снова? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    python test_db_connection.py || exit 1
fi

# Проверка Telegram (опционально)
echo ""
read -p "Проверить подключение к Telegram? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Проверка Telegram..."
    if python main.py test-telegram; then
        success "Telegram работает!"
    else
        warning "Telegram не настроен или есть ошибка"
        echo "Продолжаем без Telegram..."
    fi
fi

# Меню выбора режима
echo ""
echo "=========================================="
echo "  Выберите режим запуска:"
echo "=========================================="
echo "1) Однократная проверка (once)"
echo "2) Непрерывный мониторинг (continuous)"
echo "3) Показать все документы (list)"
echo "4) Выход"
echo ""
read -p "Ваш выбор (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Запуск однократной проверки..."
        python main.py once
        ;;
    2)
        echo ""
        echo "Запуск непрерывного мониторинга..."
        echo "Для остановки нажмите Ctrl+C"
        python main.py continuous
        ;;
    3)
        echo ""
        python main.py list
        ;;
    4)
        echo "Выход..."
        exit 0
        ;;
    *)
        error "Неверный выбор"
        exit 1
        ;;
esac

echo ""
success "Готово!"
