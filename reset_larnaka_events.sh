#!/bin/bash
# Script to reset Larnaka events from November 3rd and later
# This allows the scraper to rediscover them with proper Russian summaries

set -e

echo "=============================================="
echo "Larnaka Events Reset Script"
echo "=============================================="
echo ""

# Database connection details
DB_CONTAINER="fia_postgres"
DB_USER="postgres"
DB_NAME="fia_documents"

# Check if container exists
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo "❌ Error: Container $DB_CONTAINER is not running"
    exit 1
fi

echo "📊 Step 1: Showing current events (date >= 2024-11-03)"
echo "----------------------------------------------"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    id,
    LEFT(title, 50) as title,
    date,
    created_at
FROM larnaka_events
WHERE date >= '2024-11-03'
ORDER BY date DESC;
"

echo ""
echo "📊 Step 2: Count of events to be deleted"
echo "----------------------------------------------"
COUNT=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "
SELECT COUNT(*) FROM larnaka_events WHERE date >= '2024-11-03';
")
echo "Events to delete: $COUNT"

echo ""
read -p "⚠️  Delete these $COUNT events? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled. No events were deleted."
    exit 0
fi

echo ""
echo "🗑️  Step 3: Deleting events..."
echo "----------------------------------------------"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
DELETE FROM larnaka_events WHERE date >= '2024-11-03';
"

echo ""
echo "✅ Step 4: Verification"
echo "----------------------------------------------"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    COUNT(*) as remaining_events,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM larnaka_events;
"

echo ""
echo "=============================================="
echo "✅ Done! Events deleted successfully."
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Make sure ANTHROPIC_API_KEY is set in .env"
echo "2. Restart scraper: sudo systemctl restart larnaka-scraper"
echo "3. Monitor logs: sudo journalctl -u larnaka-scraper -f"
echo "4. The scraper will rediscover events and send with Russian summaries"
echo ""
