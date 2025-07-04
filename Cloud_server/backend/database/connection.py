import psycopg2
from config.settings import Config

def get_db_connection():
    """Get database connection"""
    try:
        connection = psycopg2.connect(Config.DATABASE_URL)
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
