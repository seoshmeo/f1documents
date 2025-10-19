# Шпаргалка команд

## Основные команды

```bash
# Запуск
python main.py once          # Однократная проверка
python main.py continuous    # Непрерывный мониторинг
python main.py list          # Показать все документы
python main.py test-telegram # Проверить Telegram

# Тестирование
python test_db_connection.py # Проверить подключение к БД

# Логи
tail -f fia_scraper.log      # Смотреть логи в реальном времени
tail -100 fia_scraper.log    # Последние 100 строк
grep ERROR fia_scraper.log   # Только ошибки
```

## SQL команды (для psql)

```bash
# Подключение
psql -h YOUR_HOST -U YOUR_USER -d fia_documents

# В psql:
SELECT COUNT(*) FROM fia_documents;           # Количество документов
SELECT * FROM fia_documents ORDER BY created_at DESC LIMIT 10;  # Последние 10
\d fia_documents                              # Структура таблицы
\q                                            # Выход
```

## Настройка .env

```env
# База данных
DB_HOST=192.168.1.100
DB_PORT=5432
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=your_password

# Telegram
TELEGRAM_BOT_TOKEN=8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA
TELEGRAM_CHAT_ID=-1002701939006

# Настройки
FIA_URL=https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071
CHECK_INTERVAL=3600
```

## Systemd сервис

```bash
# Создать файл /etc/systemd/system/fia-scraper.service
sudo systemctl enable fia-scraper   # Включить автозапуск
sudo systemctl start fia-scraper    # Запустить
sudo systemctl stop fia-scraper     # Остановить
sudo systemctl restart fia-scraper  # Перезапустить
sudo systemctl status fia-scraper   # Статус
journalctl -u fia-scraper -f        # Логи в реальном времени
```

## Screen (фоновый запуск)

```bash
screen -S fia                       # Создать сессию
python main.py continuous           # Запустить скрипт
# Ctrl+A затем D                    # Отключиться
screen -r fia                       # Вернуться к сессии
screen -ls                          # Список сессий
```

## Docker

```bash
docker-compose up -d                # Запустить
docker-compose down                 # Остановить
docker-compose logs -f scraper      # Логи
docker-compose restart scraper      # Перезапустить
```

## Бэкап базы данных

```bash
# Создать бэкап
pg_dump -h localhost -U postgres -d fia_documents > backup_$(date +%Y%m%d).sql

# Восстановить
psql -h localhost -U postgres -d fia_documents < backup_20251018.sql
```

## Очистка логов

```bash
# Очистить старые логи
> fia_scraper.log

# Или оставить последние 1000 строк
tail -1000 fia_scraper.log > temp.log && mv temp.log fia_scraper.log
```

## Установка на новом сервере

```bash
# 1. Клонировать/скопировать проект
cd /opt/fia-documents-scraper

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить .env
nano .env

# 5. Проверить подключение
python test_db_connection.py
python main.py test-telegram

# 6. Запустить
python main.py once
```

## Мониторинг

```bash
# Проверить, работает ли процесс
ps aux | grep main.py

# Убить процесс
pkill -f "python main.py"

# Проверить подключение к БД
netstat -an | grep 5432

# Использование диска
du -sh .
du -sh fia_scraper.log
```

## Полезные SQL запросы

```sql
-- Последний добавленный документ
SELECT document_name, created_at FROM fia_documents ORDER BY created_at DESC LIMIT 1;

-- Документы за сегодня
SELECT * FROM fia_documents WHERE DATE(created_at) = CURRENT_DATE;

-- Статистика по сезонам
SELECT season, COUNT(*) FROM fia_documents GROUP BY season;

-- Размер всех документов
SELECT pg_size_pretty(SUM(file_size)::bigint) FROM fia_documents;
```

## Переменные окружения

```bash
# Посмотреть текущие значения
cat .env

# Временно изменить интервал проверки
export CHECK_INTERVAL=1800  # 30 минут
python main.py continuous
```

## Troubleshooting

```bash
# База не подключается
python test_db_connection.py  # Покажет ошибку

# Telegram не работает
python main.py test-telegram   # Покажет ошибку

# Скрипт падает
tail -100 fia_scraper.log      # Смотреть последние ошибки

# Порт 5432 закрыт
sudo ufw allow 5432            # Открыть порт (осторожно!)
```

## Автообновление

```bash
# Crontab для автоматической проверки каждый час
crontab -e
# Добавить:
0 * * * * cd /opt/fia-documents-scraper && /opt/fia-documents-scraper/venv/bin/python main.py once >> /var/log/fia_scraper_cron.log 2>&1
```

## Права доступа

```bash
# Сделать скрипты исполняемыми
chmod +x main.py
chmod +x test_db_connection.py

# Владелец файлов
chown -R user:user /opt/fia-documents-scraper

# Права на .env (только владелец читает)
chmod 600 .env
```

---

**Документация:**
- [README.md](README.md) - Полная документация
- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт
- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Настройка БД
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Настройка Telegram
- [SQL_COMMANDS.md](SQL_COMMANDS.md) - SQL команды
