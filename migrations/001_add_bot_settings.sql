-- Migration: Add bot_settings table for dynamic configuration
-- Created: 2025-10-23

-- Create bot_settings table
CREATE TABLE IF NOT EXISTS bot_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Create index on setting_key
CREATE INDEX IF NOT EXISTS idx_setting_key ON bot_settings(setting_key);

-- Insert default settings
INSERT INTO bot_settings (setting_key, setting_value, description, updated_by)
VALUES
    ('check_interval', '3600', 'Interval between checks in seconds', 'system'),
    ('scraper_enabled', 'true', 'Enable/disable automatic scraping', 'system'),
    ('last_check_time', '0', 'Unix timestamp of last check', 'system')
ON CONFLICT (setting_key) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_bot_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger
CREATE TRIGGER update_bot_settings_timestamp
    BEFORE UPDATE ON bot_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_bot_settings_updated_at();
