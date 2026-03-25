"""
QR Access Control PRO - Database Connection Pool
Uses mysql.connector.pooling for efficient connection management.
"""
import mysql.connector
from mysql.connector import pooling
from config.settings import config

_pool = None


def get_pool():
    """Get or create the connection pool."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="qr_access_pool",
            pool_size=config.DB_POOL_SIZE,
            pool_reset_session=True,
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
    return _pool


def get_connection():
    """Get a connection from the pool."""
    return get_pool().get_connection()


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a query with automatic connection management.
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        fetch_one: Return single row
        fetch_all: Return all rows
        commit: Commit transaction after execution
    
    Returns:
        Query results or lastrowid for INSERT/UPDATE
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)

        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid

        if commit:
            conn.commit()

        return result
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
