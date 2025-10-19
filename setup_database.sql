-- Setup script for FIA Documents database
-- Run this script to create the database and tables

-- Create database (run as postgres superuser)
-- CREATE DATABASE fia_documents;

-- Connect to the database
\c fia_documents;

-- Create documents table
CREATE TABLE IF NOT EXISTS fia_documents (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(500) NOT NULL,
    document_url VARCHAR(1000) NOT NULL UNIQUE,
    document_hash VARCHAR(64) NOT NULL,
    file_size BIGINT,
    document_type VARCHAR(50),
    season VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_document_url ON fia_documents(document_url);
CREATE INDEX IF NOT EXISTS idx_document_hash ON fia_documents(document_hash);
CREATE INDEX IF NOT EXISTS idx_created_at ON fia_documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_season ON fia_documents(season);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_fia_documents_updated_at
    BEFORE UPDATE ON fia_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON TABLE fia_documents TO your_username;
-- GRANT USAGE, SELECT ON SEQUENCE fia_documents_id_seq TO your_username;

-- Show table structure
\d fia_documents;
