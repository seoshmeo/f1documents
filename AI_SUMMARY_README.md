# 🤖 AI Summary Feature - Готово к использованию!

## ✨ Что добавлено

Ваш FIA бот теперь **автоматически генерирует саммари** для каждого нового документа на русском языке, используя Claude Code из вашей подписки.

### Пример сообщения в Telegram:

```
🏎️ Новый документ FIA

📄 Decision - Car 55 - Track Limits Turn 6

📊 Размер: 234.5 KB
🏁 Сезон: 2025

📝 Краткое содержание:
Стюарды рассмотрели нарушение трековых лимитов
автомобилем №55 (Ferrari) на 6-м повороте во время
квалификации. Время круга аннулировано, пилот
стартует с позиции, показанной до удалённого круга.

🔗 Открыть документ
```

---

## 🚀 Быстрый старт для теста

### 1. Узнайте ваш Chat ID:

```bash
python3 get_my_chat_id.py
```

Напишите боту сообщение → получите Chat ID

### 2. Добавьте в `.env`:

```bash
TELEGRAM_ADMIN_CHAT_ID=ваш_chat_id
```

### 3. Запустите тест:

```bash
python3 test_summary.py
```

Саммари придёт **только вам** в личный Telegram!

---

## 📁 Что было создано

### Новые модули:
- **`pdf_processor.py`** - Обработка PDF файлов
- **`claude_summarizer.py`** - Генерация саммари через Claude Code
- **`test_summary.py`** - Тестовый скрипт
- **`get_my_chat_id.py`** - Узнать свой Chat ID

### Обновлённые файлы:
- **`main.py`** - Интеграция саммари в основной flow
- **`database.py`** - Поле `summary` в БД
- **`telegram_notifier.py`** - Показ саммари в сообщениях
- **`requirements.txt`** - PyPDF2, pdfplumber

### Документация:
- **`AI_SUMMARY_SETUP.md`** - Полная документация
- **`SUMMARY_QUICKSTART.md`** - Быстрый старт
- **`TEST_INSTRUCTIONS.md`** - Инструкции по тестированию
- **`migrations/add_summary_field.sql`** - SQL миграция

---

## 💡 Как это работает

1. Бот находит новый документ FIA
2. Скачивает PDF и извлекает текст
3. Claude Code анализирует и создаёт саммари (5-7 предложений на русском)
4. Сохраняет в БД и отправляет в Telegram

**Важно:** Если Claude Code недоступен/нет квоты → документ всё равно отправится (просто без саммари).

---

## 🎯 Следующие шаги

### Для продакшена:

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Обновите БД:**
   ```bash
   psql -h localhost -U postgres -d fia_documents -f migrations/add_summary_field.sql
   ```

3. **Настройте .env:**
   ```bash
   TELEGRAM_CHAT_ID=-1002701939006      # группа для документов
   TELEGRAM_ADMIN_CHAT_ID=123456789     # ваш личный для тестов/команд
   ```

4. **Запустите:**
   ```bash
   python3 run_with_bot.py
   ```

---

## 📊 Стоимость

**$0** - использует вашу подписку Claude Code!

Примерные расходы:
- ~10 документов/месяц
- ~15,000 токенов/документ
- Входит в вашу подписку Pro/Max/Code

---

## 📖 Документация

- **[AI_SUMMARY_SETUP.md](AI_SUMMARY_SETUP.md)** - Полная документация со всеми деталями
- **[SUMMARY_QUICKSTART.md](SUMMARY_QUICKSTART.md)** - Быстрый старт за 3 шага
- **[TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)** - Как тестировать

---

## 🐛 Troubleshooting

### Claude Code не найден?
```bash
which claude
```
Установите: https://docs.claude.com/en/docs/claude-code

### Quota exceeded?
Бот продолжит работать без саммари, когда квота обновится - саммари вернутся.

### PDF text extraction failed?
Некоторые PDF (сканы) не содержат текста - это нормально, документ отправится без саммари.

---

**Готовы протестировать?** → Смотрите [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)
