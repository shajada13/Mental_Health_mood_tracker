# ============================================================
#  MindFlow — User Model
#  models/user.py  |  Pure Python + PyMySQL
# ============================================================

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from backend.db import get_db

logger = logging.getLogger(__name__)


# ── Data class (plain Python, no ORM) ───────────────────────
@dataclass
class User:
    id:                   Optional[int]      = None
    full_name:            str                = ""
    email:                str                = ""
    password_hash:        str                = ""
    date_of_birth:        Optional[str]      = None
    gender:               str                = "prefer_not_to_say"
    avatar_url:           Optional[str]      = None
    primary_goal:         str                = "improve_mood"
    stress_baseline:      int                = 5
    onboarding_complete:  bool               = False
    is_active:            bool               = True
    is_verified:          bool               = False
    last_login_at:        Optional[datetime] = None
    created_at:           Optional[datetime] = None
    updated_at:           Optional[datetime] = None

    # Never serialise the hash to JSON output
    def to_dict(self) -> dict:
        return {
            "id":                  self.id,
            "full_name":           self.full_name,
            "email":               self.email,
            "date_of_birth":       str(self.date_of_birth) if self.date_of_birth else None,
            "gender":              self.gender,
            "avatar_url":          self.avatar_url,
            "primary_goal":        self.primary_goal,
            "stress_baseline":     self.stress_baseline,
            "onboarding_complete": self.onboarding_complete,
            "is_active":           self.is_active,
            "is_verified":         self.is_verified,
            "last_login_at":       str(self.last_login_at)  if self.last_login_at  else None,
            "created_at":          str(self.created_at)     if self.created_at     else None,
        }

    @staticmethod
    def from_row(row: dict) -> "User":
        """Build a User from a DB dict-cursor row."""
        return User(
            id                  = row.get("id"),
            full_name           = row.get("full_name", ""),
            email               = row.get("email", ""),
            password_hash       = row.get("password_hash", ""),
            date_of_birth       = row.get("date_of_birth"),
            gender              = row.get("gender", "prefer_not_to_say"),
            avatar_url          = row.get("avatar_url"),
            primary_goal        = row.get("primary_goal", "improve_mood"),
            stress_baseline     = row.get("stress_baseline", 5),
            onboarding_complete = bool(row.get("onboarding_complete", False)),
            is_active           = bool(row.get("is_active", True)),
            is_verified         = bool(row.get("is_verified", False)),
            last_login_at       = row.get("last_login_at"),
            created_at          = row.get("created_at"),
            updated_at          = row.get("updated_at"),
        )


# ── Repository helpers (all DB queries live here) ───────────

class UserRepository:

    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        sql = "SELECT * FROM users WHERE id = %s AND is_active = TRUE LIMIT 1"
        with get_db() as (_, cur):
            cur.execute(sql, (user_id,))
            row = cur.fetchone()
        return User.from_row(row) if row else None

    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        sql = "SELECT * FROM users WHERE email = %s LIMIT 1"
        with get_db() as (_, cur):
            cur.execute(sql, (email.lower().strip(),))
            row = cur.fetchone()
        return User.from_row(row) if row else None

    @staticmethod
    def email_exists(email: str) -> bool:
        sql = "SELECT id FROM users WHERE email = %s LIMIT 1"
        with get_db() as (_, cur):
            cur.execute(sql, (email.lower().strip(),))
            return cur.fetchone() is not None

    @staticmethod
    def create(full_name: str, email: str, password_hash: str,
               date_of_birth: Optional[str] = None,
               gender: str = "prefer_not_to_say",
               primary_goal: str = "improve_mood") -> int:
        """Insert a new user row and return the new primary-key id."""
        sql = """
            INSERT INTO users
                (full_name, email, password_hash, date_of_birth,
                 gender, primary_goal, is_active, is_verified, onboarding_complete)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE, FALSE, FALSE)
        """
        with get_db() as (conn, cur):
            cur.execute(sql, (
                full_name.strip(),
                email.lower().strip(),
                password_hash,
                date_of_birth,
                gender,
                primary_goal,
            ))
            return cur.lastrowid

    @staticmethod
    def update_last_login(user_id: int) -> None:
        sql = "UPDATE users SET last_login_at = NOW() WHERE id = %s"
        with get_db() as (_, cur):
            cur.execute(sql, (user_id,))

    @staticmethod
    def update_password(user_id: int, new_hash: str) -> None:
        sql = "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s"
        with get_db() as (_, cur):
            cur.execute(sql, (new_hash, user_id))

    @staticmethod
    def verify_email(user_id: int) -> None:
        sql = "UPDATE users SET is_verified = TRUE, updated_at = NOW() WHERE id = %s"
        with get_db() as (_, cur):
            cur.execute(sql, (user_id,))

    @staticmethod
    def deactivate(user_id: int) -> None:
        sql = "UPDATE users SET is_active = FALSE, updated_at = NOW() WHERE id = %s"
        with get_db() as (_, cur):
            cur.execute(sql, (user_id,))
