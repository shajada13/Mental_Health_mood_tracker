# ============================================================
#  MindFlow — Input Validators
#  utils/validators.py
# ============================================================

import re
from typing import Optional


EMAIL_RE    = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
NAME_RE     = re.compile(r"^[a-zA-Z\s'\-]{2,100}$")


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    if not email or not email.strip():
        return False, "Email is required."
    if not EMAIL_RE.match(email.strip()):
        return False, "Invalid email address format."
    if len(email) > 150:
        return False, "Email address is too long (max 150 chars)."
    return True, None


def validate_full_name(name: str) -> tuple[bool, Optional[str]]:
    if not name or not name.strip():
        return False, "Full name is required."
    if not NAME_RE.match(name.strip()):
        return False, "Name must be 2–100 characters and contain only letters, spaces, hyphens or apostrophes."
    return True, None


def validate_required(value: str, field: str) -> tuple[bool, Optional[str]]:
    if not value or not str(value).strip():
        return False, f"{field} is required."
    return True, None


def sanitise_string(value: str, max_len: int = 255) -> str:
    """Strip whitespace and truncate to max_len."""
    return str(value).strip()[:max_len]
