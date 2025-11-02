-- Delete Larnaka events from November 3rd and later
-- This will allow the scraper to rediscover them and send with proper Russian summaries

-- First, let's see what we're about to delete
SELECT
    id,
    title,
    date,
    created_at,
    CASE
        WHEN date >= '2024-11-03' THEN 'WILL BE DELETED'
        ELSE 'KEEP'
    END as action
FROM larnaka_events
ORDER BY date DESC;

-- Uncomment the line below to actually delete the events:
-- DELETE FROM larnaka_events WHERE date >= '2024-11-03';

-- After deleting, verify:
-- SELECT COUNT(*) as remaining_events FROM larnaka_events;
