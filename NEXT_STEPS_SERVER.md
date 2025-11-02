# Next Steps: Fixing Larnaka Telegram "Chat not found" Error

## Problem Summary

Larnaka scraper is running successfully and finding events, but fails to send Telegram notifications with error:
```
Chat not found
```

Current (incorrect) chat ID: `1001974716718` or `-1001974716718`

## Solution Steps (On Server)

### Step 1: Pull Latest Code

```bash
cd /opt/f1documents
git pull origin main
```

This will add:
- `test_telegram_bot.py` - diagnostic script
- Updated `TELEGRAM_SETUP.md` - troubleshooting guide

### Step 2: Run Diagnostic Script

```bash
cd /opt/f1documents
/opt/f1documents/venv/bin/python test_telegram_bot.py
```

**Expected output:**
- Bot info (name, username, ID)
- List of recent updates showing all chats where bot received messages
- Chat IDs with their types (private, group, supergroup)

**If no groups appear:**
The bot either:
1. Not added to the group
2. Privacy Mode is enabled (bot can't see group messages)

### Step 3: Fix Bot Permissions (If Needed)

#### A. Add Bot to Group as Administrator

1. Open your Larnaka Telegram group
2. Tap group name → Administrators → Add Administrator
3. Find your bot (should be something like @YourBotName)
4. Add with these permissions:
   - ✅ Post Messages
   - ✅ Edit Messages (optional)
   - ✅ Delete Messages (optional)

#### B. Disable Privacy Mode

1. Open @BotFather in Telegram
2. Send: `/setprivacy`
3. Select your bot
4. Select: **Disable**

This allows the bot to see all messages in groups (needed to register the group).

#### C. Send Message in Group

After disabling Privacy Mode, send a message in your Larnaka group:
```
/start
```

Or just:
```
Test message
```

### Step 4: Get Correct Chat ID

Run diagnostic script again:

```bash
/opt/f1documents/venv/bin/python test_telegram_bot.py
```

Now you should see your group listed with its chat ID.

**For supergroups, the ID looks like:** `-1001234567890`
(Note the `-100` prefix!)

### Step 5: Update .env File

Edit the .env file on the server:

```bash
nano /opt/f1documents/.env
```

Update the chat ID:
```bash
# Old (incorrect)
LARNAKA_TELEGRAM_CHAT_ID=1001974716718

# New (correct - example, use your actual ID from diagnostic script)
LARNAKA_TELEGRAM_CHAT_ID=-1001234567890
```

**Important:** Make sure there's a minus sign at the beginning!

Save and exit (Ctrl+X, Y, Enter)

### Step 6: Restart Larnaka Scraper

```bash
sudo systemctl restart larnaka-scraper
```

### Step 7: Monitor Logs

Watch the logs in real-time:

```bash
sudo journalctl -u larnaka-scraper -f
```

Or:

```bash
tail -f /opt/f1documents/larnaka_scraper.log
```

Look for:
- ✅ "Successfully sent event to Telegram"
- ❌ Any error messages

### Step 8: Test with Manual Event

If you want to test immediately, delete one event from the database and let the scraper rediscover it:

```bash
# Connect to database
docker exec -it fia_postgres psql -U postgres -d fia_documents

# List recent Larnaka events
SELECT id, title FROM larnaka_events ORDER BY created_at DESC LIMIT 5;

# Delete one event (replace 21 with an actual ID)
DELETE FROM larnaka_events WHERE id = 21;

# Exit
\q
```

The scraper will rediscover this event on the next check and try to send it to Telegram.

## Alternative: Using curl for Chat ID

If Python script doesn't work, use curl:

```bash
BOT_TOKEN="8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA"

curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates" | python3 -m json.tool
```

Look for your group in the output:
```json
{
  "chat": {
    "id": -1001234567890,
    "title": "Larnaka Events",
    "type": "supergroup"
  }
}
```

## Verification Checklist

- [ ] Bot is added to Larnaka group as administrator
- [ ] Bot has "Post Messages" permission
- [ ] Privacy Mode is disabled in @BotFather
- [ ] Message sent in group after disabling Privacy Mode
- [ ] Diagnostic script shows the group with correct chat ID
- [ ] .env updated with correct chat ID (with minus sign!)
- [ ] Larnaka scraper service restarted
- [ ] Logs show successful message sending

## Current Configuration

On server at `/opt/f1documents/.env`:

```bash
# Database
DB_HOST=localhost
DB_PORT=5433
DB_NAME=fia_documents
DB_USER=postgres
DB_PASSWORD=your_password

# Bot Token (shared by FIA and Larnaka)
TELEGRAM_BOT_TOKEN=8277919288:AAGC17pTImhRuUpGajaG3eW8BYyPoC_kzcA

# FIA Channel (working)
FIA_TELEGRAM_CHAT_ID=<your_fia_channel_id>

# Larnaka Channel (needs to be fixed)
LARNAKA_TELEGRAM_CHAT_ID=<get_from_diagnostic_script>

# Admin Chat (personal chat for commands)
TELEGRAM_ADMIN_CHAT_ID=<your_personal_chat_id>
```

## Common Errors and Solutions

### "Forbidden: bot is not a member of the supergroup chat"
→ Add bot to the group

### "Forbidden: bot was kicked from the supergroup chat"
→ Bot was removed, add it back

### "Bad Request: chat not found"
→ Wrong chat ID or bot never added to group

### "Unauthorized"
→ Wrong bot token in .env

## Need Help?

1. Check [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for detailed guide
2. Check [SERVER_SETUP.md](SERVER_SETUP.md) for server configuration
3. Run diagnostic script: `test_telegram_bot.py`
4. Check logs: `sudo journalctl -u larnaka-scraper -f`

## Architecture Note

The Larnaka scraper uses a simple loop without bot command listener (unlike FIA scraper which has `run_with_bot.py`). If you need bot commands for Larnaka (like `/status`, `/check`, etc.), you can create a similar setup using the FIA scraper as a reference.
