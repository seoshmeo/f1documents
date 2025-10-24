# AI Summary - Быстрый старт

## 3 шага до запуска

### 1️⃣ Установите зависимости

```bash
pip install -r requirements.txt
```

Это установит:
- `PyPDF2` - для чтения PDF
- `pdfplumber` - для сложных PDF

### 2️⃣ Обновите базу данных

```bash
psql -h localhost -U postgres -d fia_documents -f migrations/add_summary_field.sql
```

Или вручную:
```sql
ALTER TABLE fia_documents ADD COLUMN summary TEXT;
```

### 3️⃣ Убедитесь что Claude Code работает

```bash
claude "тест"
```

Если видите ответ - всё готово!

---

## Запуск

```bash
python3 run_with_bot.py
```

Или через Docker:
```bash
docker-compose up -d
```

---

## Что произойдёт?

Когда появится новый документ FIA:

1. 📥 Скачается PDF
2. 📄 Извлечётся текст
3. 🤖 Claude Code создаст саммари на русском
4. 📱 Telegram получит саммари + ссылку на документ

**Если Claude Code недоступен** - документ всё равно отправится (просто без саммари).

---

## Проверка работы

Посмотрите логи:

```bash
tail -f fia_scraper.log
```

Успешная работа:
```
✓ Summary generated successfully
  Summary: ✓ Generated
Telegram notification sent
```

---

## Готово!

Полная документация: [AI_SUMMARY_SETUP.md](AI_SUMMARY_SETUP.md)
