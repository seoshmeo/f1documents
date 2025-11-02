"""
Configuration settings for FIA Documents Scraper
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'fia_documents')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # FIA Scraper settings
    FIA_URL = os.getenv(
        'FIA_URL',
        'https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071'
    )
    FIA_CHECK_INTERVAL = int(os.getenv('FIA_CHECK_INTERVAL', 3600))  # 1 hour
    FIA_ENABLED = os.getenv('FIA_ENABLED', 'true').lower() == 'true'

    # Larnaka Scraper settings
    LARNAKA_URL = os.getenv(
        'LARNAKA_URL',
        'https://www.larnaka.org.cy/en/information/cultural-activities-initiatives/events-calendar/'
    )
    LARNAKA_CHECK_INTERVAL = int(os.getenv('LARNAKA_CHECK_INTERVAL', 7200))  # 2 hours
    LARNAKA_ENABLED = os.getenv('LARNAKA_ENABLED', 'true').lower() == 'true'

    # Legacy (for backward compatibility)
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 3600))

    # Request timeout in seconds
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))

    # User agent for HTTP requests
    USER_AGENT = os.getenv(
        'USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'scraper.log')

    @classmethod
    def get_database_url(cls):
        """Get database connection URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def validate(cls):
        """Validate configuration"""
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = []

        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required configuration: {', '.join(missing_vars)}")

        return True
