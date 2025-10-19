import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations handler"""

    def __init__(self):
        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'fia_documents'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()

    def return_connection(self, connection):
        """Return connection to pool"""
        self.connection_pool.putconn(connection)

    def create_tables(self):
        """Create necessary database tables"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            # Create documents table
            cursor.execute("""
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
            """)

            # Create index on document_url for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_url
                ON fia_documents(document_url);
            """)

            # Create index on document_hash
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_hash
                ON fia_documents(document_hash);
            """)

            connection.commit()
            logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                cursor.close()
                self.return_connection(connection)

    def document_exists(self, document_url):
        """Check if document already exists in database"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM fia_documents WHERE document_url = %s",
                (document_url,)
            )

            result = cursor.fetchone()
            exists = result is not None

            if exists:
                logger.info(f"Document already exists: {document_url}")

            return exists

        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            raise
        finally:
            if connection:
                cursor.close()
                self.return_connection(connection)

    def document_exists_by_hash(self, document_hash):
        """Check if document with same hash already exists"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id, document_url FROM fia_documents WHERE document_hash = %s",
                (document_hash,)
            )

            result = cursor.fetchone()

            if result:
                logger.info(f"Document with same hash exists: {result[1]}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking document hash: {e}")
            raise
        finally:
            if connection:
                cursor.close()
                self.return_connection(connection)

    def insert_document(self, document_data):
        """Insert new document into database"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO fia_documents
                (document_name, document_url, document_hash, file_size, document_type, season)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                document_data['name'],
                document_data['url'],
                document_data['hash'],
                document_data.get('size'),
                document_data.get('type', 'PDF'),
                document_data.get('season', '2025')
            ))

            document_id = cursor.fetchone()[0]
            connection.commit()

            logger.info(f"Document inserted successfully: {document_data['name']} (ID: {document_id})")
            return document_id

        except psycopg2.IntegrityError as e:
            logger.warning(f"Document already exists (integrity error): {document_data['url']}")
            if connection:
                connection.rollback()
            return None
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                cursor.close()
                self.return_connection(connection)

    def get_all_documents(self):
        """Retrieve all documents from database"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM fia_documents
                ORDER BY created_at DESC
            """)

            documents = cursor.fetchall()
            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise
        finally:
            if connection:
                cursor.close()
                self.return_connection(connection)

    def close_all_connections(self):
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All database connections closed")
