"""
Database operations for Larnaka events
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LarnakaDatabase:
    """Database operations for Larnaka cultural events"""

    def __init__(self, db_config):
        """
        Initialize database connection

        Args:
            db_config: dict with keys: host, port, database, user, password
        """
        self.db_config = db_config
        self.conn = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            logger.info("Connected to PostgreSQL database (Larnaka)")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database (Larnaka)")

    def event_exists_by_url(self, event_url):
        """Check if event exists by URL"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id FROM larnaka_events WHERE event_url = %s",
                (event_url,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking event existence by URL: {e}")
            return False

    def event_exists_by_hash(self, event_hash):
        """Check if event exists by content hash"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id FROM larnaka_events WHERE event_hash = %s",
                (event_hash,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking event existence by hash: {e}")
            return False

    def insert_event(self, event_data):
        """
        Insert new event into database

        Args:
            event_data: dict with keys: title, url, hash, date, time, location, description, summary

        Returns:
            int: ID of inserted event, or None on failure
        """
        try:
            cursor = self.conn.cursor()

            query = """
                INSERT INTO larnaka_events
                (event_title, event_url, event_hash, event_date, event_time,
                 event_location, event_description, summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            cursor.execute(query, (
                event_data.get('title', ''),
                event_data.get('url', ''),
                event_data.get('hash', ''),
                event_data.get('date'),
                event_data.get('time', ''),
                event_data.get('location', ''),
                event_data.get('description', ''),
                event_data.get('summary', '')
            ))

            event_id = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()

            logger.info(f"Inserted new event: {event_data.get('title', '')} (ID: {event_id})")
            return event_id

        except Exception as e:
            logger.error(f"Error inserting event: {e}")
            self.conn.rollback()
            return None

    def update_event_summary(self, event_id, summary):
        """Update event summary"""
        try:
            cursor = self.conn.cursor()

            query = """
                UPDATE larnaka_events
                SET summary = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            cursor.execute(query, (summary, event_id))
            self.conn.commit()
            cursor.close()

            logger.info(f"Updated summary for event ID: {event_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating event summary: {e}")
            self.conn.rollback()
            return False

    def get_event_by_id(self, event_id):
        """Get event by ID"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM larnaka_events WHERE id = %s",
                (event_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching event by ID: {e}")
            return None

    def get_all_events(self, limit=100):
        """Get all events (most recent first)"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT * FROM larnaka_events
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching all events: {e}")
            return []

    def get_events_by_date_range(self, start_date, end_date):
        """Get events within a date range"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT * FROM larnaka_events
                WHERE event_date BETWEEN %s AND %s
                ORDER BY event_date ASC
                """,
                (start_date, end_date)
            )
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching events by date range: {e}")
            return []

    def delete_event(self, event_id):
        """Delete event by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM larnaka_events WHERE id = %s",
                (event_id,)
            )
            self.conn.commit()
            cursor.close()
            logger.info(f"Deleted event ID: {event_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            self.conn.rollback()
            return False

    def get_events_count(self):
        """Get total count of events"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM larnaka_events")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"Error getting events count: {e}")
            return 0

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
