# Security Configuration

## PostgreSQL Security

### Problem
PostgreSQL порт был открыт для всего интернета, что привело к заражению crypto-майнером `kdevtmpfsi`.

### Solution
Порт PostgreSQL теперь доступен **только с localhost**:

```yaml
ports:
  - "127.0.0.1:5433:5432"  # Только localhost
```

### Checking for Malware

Если сервер снова заражен майнером, выполните:

```bash
# 1. Проверить процессы
ps aux | grep -i "mine\|kdev\|xmr"
top -bn1 | head -10

# 2. Убить майнер
killall kdevtmpfsi
kill -9 <PID>

# 3. Найти и удалить файлы
find / -name "kdevtmp*" 2>/dev/null
rm -f /tmp/kdevtmpfsi

# 4. Проверить Docker контейнеры
docker ps --format "{{.ID}} {{.Names}}" | while read id name; do
  echo "Checking $name..."
  docker exec $id ps aux 2>/dev/null | grep kdev
done

# 5. Пересоздать зараженный контейнер
docker stop <container_name>
docker rm <container_name>
docker-compose up -d
```

## Firewall Configuration

### Рекомендуется настроить UFW:

```bash
# Включить firewall
ufw enable

# Разрешить SSH
ufw allow 22/tcp

# Разрешить HTTP/HTTPS (если нужно)
ufw allow 80/tcp
ufw allow 443/tcp

# Заблокировать все остальное
ufw default deny incoming
ufw default allow outgoing

# Проверить статус
ufw status
```

## Environment Variables Security

Чувствительные данные хранятся в `.env`:

```bash
# НЕ коммитить в git!
ANTHROPIC_API_KEY=sk-ant-api03-...
TELEGRAM_BOT_TOKEN=...
```

Убедитесь что `.env` добавлен в `.gitignore`.

## Regular Maintenance

### Еженедельно проверяйте:

```bash
# CPU usage
top -bn1 | head -5

# Подозрительные процессы
ps aux | sort -rk 3 | head -10

# Открытые порты
netstat -tuln | grep LISTEN

# Docker контейнеры
docker ps
docker stats --no-stream
```

### Ежемесячно обновляйте:

```bash
# Обновить систему
apt update && apt upgrade -y

# Обновить Docker образы
cd /opt/f1documents
docker-compose pull
docker-compose up -d
```

## Backup

### Регулярный backup базы данных:

```bash
# Создать backup
docker exec fia_postgres pg_dump -U postgres fia_documents > backup_$(date +%Y%m%d).sql

# Восстановить из backup
docker exec -i fia_postgres psql -U postgres fia_documents < backup_20251024.sql
```

## Monitoring

Следите за:
- CPU usage > 50% без причины
- Процессы с именами: kdevtmp, xmr, mine, cryptonight
- Неизвестные соединения на порту 5432/5433
- Высокое потребление сетевого трафика

## Incident Response

Если обнаружен майнер:

1. **Немедленно** остановить зараженный контейнер
2. Убить все подозрительные процессы
3. Пересоздать контейнер из чистого образа
4. Проверить все другие контейнеры
5. Изменить все пароли
6. Проверить SSH ключи в `~/.ssh/authorized_keys`
7. Проверить crontab: `crontab -l`
