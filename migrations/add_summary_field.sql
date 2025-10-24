-- Migration: Add summary field to fia_documents table
-- Date: 2025-10-24
-- Description: Adds TEXT field to store AI-generated summaries

-- Add summary column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='fia_documents'
        AND column_name='summary'
    ) THEN
        ALTER TABLE fia_documents ADD COLUMN summary TEXT;
        RAISE NOTICE 'Column summary added successfully';
    ELSE
        RAISE NOTICE 'Column summary already exists';
    END IF;
END $$;

-- Verify the change
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'fia_documents'
ORDER BY ordinal_position;
