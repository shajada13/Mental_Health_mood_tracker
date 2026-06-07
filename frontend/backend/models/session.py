# ============================================================
#  MindFlow — Session Model
#  models/session.py  |  Pure Python + PyMySQL
#  Sessions are stored in MySQL (no Flask/Django session obj)
# ============================================================

from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from backend.db import get_db

logger = logging.getLogger(__name__)

SESSION_DURATION_DAYS         = 1    # short-lived default
SESSION_DURATION_REMEMBER_DAYS = 30  # "remember me"


@dataclass
class Session:
    id:           Optional[int]      = None
    user_id:      int                = 0
    token:        str                = ""
    ip_address:   Optional[str]      = None
    user_agent:   Optional[str]      = None
    is_active:    bool               = True
    expires_at:   Optional[datetime] = None
    created_at:   Optional[datetime] = None

    @staticmethod
    def from_row(row: dict) -> "Session":
        return Session(
            id          = row.get("id"),
            user_id     = row.get("user_id", 0),
            token       = row.get("token", ""),
            ip_address  = row.get("ip_address"),
            user_agent  = row.get("user_agent"),
            is_active   = bool(row.get("is_active", True)),
            expires_at  = row.get("expires_at"),
            created_at  = row.get("created_at"),
        )


class SessionRepository:

    @staticmethod
    def create(user_id: int, token: str, remember_me: bool = False,
               ip_address: str = "", user_agent: str = "") -> int:
        days  = SESSION_DURATION_REMEMBER_DAYS if remember_me else SESSION_DURATION_DAYS
        sql   = """
            INSERT INTO sessions
                (user_id, token, ip_address, user_agent, is_active, expires_at)
            VALUES
                (%s, %s, %s, %s, TRUE,
                 DATE_ADD(NOW(), INTERVAL %s DAY))
        """
        with get_db() as (_, cur):
            cur.execute(sql, (user_id, token, ip_address, user_agent, days))
            return cur.lastrowid

    @staticmethod
    def find_by_token(token: str) -> Optional[Session]:
        sql = """
            SELECT * FROM sessions
            WHERE token = %s
              AND is_active = TRUE
              AND expires_at > NOW()
            LIMIT 1
        """
        with get_db() as (_, cur):
            cur.execute(sql, (token,))
            row = cur.fetchone()
        return Session.from_row(row) if row else None

    @staticmethod
    def invalidate(token: str) -> None:
        """Logout: mark session inactive."""
        sql = "UPDATE sessions SET is_active = FALSE WHERE token = %s"
        with get_db() as (_, cur):
            cur.execute(sql, (token,))

    @staticmethod
    def invalidate_all_for_user(user_id: int) -> None:
        """Invalidate every session for a user (e.g., password change)."""
        sql = "UPDATE sessions SET is_active = FALSE WHERE user_id = %s"
        with get_db() as (_, cur):
            cur.execute(sql, (user_id,))

    @staticmethod
    def purge_expired() -> int:
        """Delete expired sessions. Run as a periodic cleanup job."""
        sql = "DELETE FROM sessions WHERE expires_at <= NOW() OR is_active = FALSE"
        with get_db() as (_, cur):
            cur.execute(sql)
            return cur.rowcount
