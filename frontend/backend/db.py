# ============================================================
#  MindFlow — Database Connection Manager
#  db.py  |  Pure Python + PyMySQL (no framework)
# ============================================================

import pymysql
import pymysql.cursors
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Connection config pulled from .env ──────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME",     "mindflow_db"),
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False,
    "connect_timeout": 10,
}


def get_connection() -> pymysql.connections.Connection:
    """Open and return a raw PyMySQL connection."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.MySQLError as exc:
        logger.error("DB connection failed: %s", exc)
        raise


@contextmanager
def get_db():
    """
    Context manager: yields a (connection, cursor) pair.
    Commits on clean exit, rolls back on exception, always closes.

    Usage:
        with get_db() as (conn, cur):
            cur.execute("SELECT ...")
            rows = cur.fetchall()
    """
    conn = get_connection()
    cur  = conn.cursor()
    try:
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
