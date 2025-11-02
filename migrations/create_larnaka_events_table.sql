-- Migration: Create larnaka_events table
-- Purpose: Store events from Larnaka cultural activities page
-- Date: 2025-11-02

CREATE TABLE IF NOT EXISTS larnaka_events (
    id SERIAL PRIMARY KEY,

    -- Event basic info
    event_title VARCHAR(500) NOT NULL,
    event_url VARCHAR(1000) UNIQUE NOT NULL,
    event_hash VARCHAR(64) UNIQUE NOT NULL,

    -- Event details
    event_date DATE,
    event_time VARCHAR(100),
    event_location VARCHAR(300),
    event_description TEXT,

    -- AI summary
    summary TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_larnaka_events_url ON larnaka_events(event_url);
CREATE INDEX IF NOT EXISTS idx_larnaka_events_hash ON larnaka_events(event_hash);
CREATE INDEX IF NOT EXISTS idx_larnaka_events_date ON larnaka_events(event_date);
CREATE INDEX IF NOT EXISTS idx_larnaka_events_created_at ON larnaka_events(created_at DESC);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_larnaka_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_larnaka_events_updated_at
    BEFORE UPDATE ON larnaka_events
    FOR EACH ROW
    EXECUTE FUNCTION update_larnaka_events_updated_at();

-- Add comment to table
COMMENT ON TABLE larnaka_events IS 'Stores cultural events from Larnaka website';
COMMENT ON COLUMN larnaka_events.event_hash IS 'SHA256 hash of event content for deduplication';
COMMENT ON COLUMN larnaka_events.summary IS 'AI-generated summary in Russian';
