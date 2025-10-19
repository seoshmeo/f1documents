@echo off
REM ###############################################################################
REM FIA Documents Scraper - Локальный запуск (Windows)
REM Скрипт для быстрого запуска проекта локально
REM ###############################################################################

setlocal EnableDelayedExpansion

echo ==========================================
echo   FIA Documents Scraper - Локальный запуск
echo ==========================================
echo.

REM Проверка Python
echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [31mX Python не установлен![0m
    pause
    exit /b 1
)
echo [32m✓ Python найден[0m

REM Создание виртуального окружения
if not exist "venv\" (
    echo.
    echo Создание виртуального окружения...
    python -m venv venv
    echo [32m✓ Виртуальное окружение создано[0m
) else (
    echo [32m✓ Виртуальное окружение уже существует[0m
)

REM Активация виртуального окружения
echo.
echo Активация виртуального окружения...
call venv\Scripts\activate.bat
echo [32m✓ Виртуальное окружение активировано[0m

REM Установка зависимостей
echo.
echo Установка зависимостей...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo [32m✓ Зависимости установлены[0m

REM Проверка .env файла
echo.
if not exist ".env" (
    echo [33m! .env файл не найден[0m
    echo Создание .env из .env.example...
    copy .env.example .env
    echo.
    echo [31mВАЖНО: Отредактируйте файл .env с вашими настройками![0m
    echo Особенно проверьте:
    echo   - DB_HOST (localhost для локального запуска)
    echo   - DB_PASSWORD
    echo   - TELEGRAM_BOT_TOKEN
    echo   - TELEGRAM_CHAT_ID
    echo.
    pause
) else (
    echo [32m✓ .env файл найден[0m
)

REM Проверка подключения к базе данных
echo.
echo Проверка подключения к базе данных...
python test_db_connection.py
if errorlevel 1 (
    echo [31mX Не удалось подключиться к базе данных[0m
    echo.
    echo Возможные решения:
    echo 1. Убедитесь что PostgreSQL запущен
    echo 2. Проверьте настройки в .env файле
    echo 3. Создайте базу данных через pgAdmin или psql
    echo.
    pause
    exit /b 1
)
echo [32m✓ Подключение к базе данных успешно[0m

REM Проверка Telegram
echo.
set /p check_telegram="Проверить подключение к Telegram? (y/n): "
if /i "!check_telegram!"=="y" (
    echo Проверка Telegram...
    python main.py test-telegram
    if errorlevel 1 (
        echo [33m! Telegram не настроен или есть ошибка[0m
        echo Продолжаем без Telegram...
    ) else (
        echo [32m✓ Telegram работает![0m
    )
)

REM Меню выбора режима
:menu
echo.
echo ==========================================
echo   Выберите режим запуска:
echo ==========================================
echo 1) Однократная проверка (once)
echo 2) Непрерывный мониторинг (continuous)
echo 3) Показать все документы (list)
echo 4) Выход
echo.
set /p choice="Ваш выбор (1-4): "

if "%choice%"=="1" (
    echo.
    echo Запуск однократной проверки...
    python main.py once
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Запуск непрерывного мониторинга...
    echo Для остановки нажмите Ctrl+C
    python main.py continuous
    goto end
)

if "%choice%"=="3" (
    echo.
    python main.py list
    goto end
)

if "%choice%"=="4" (
    echo Выход...
    goto end
)

echo [31mНеверный выбор[0m
goto menu

:end
echo.
echo [32m✓ Готово![0m
pause
