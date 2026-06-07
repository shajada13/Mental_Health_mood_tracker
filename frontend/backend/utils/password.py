# ============================================================
#  MindFlow — Password Hashing Utilities
#  utils/password.py  |  bcrypt (no framework)
# ============================================================

import re
import bcrypt
import logging

logger = logging.getLogger(__name__)

# bcrypt work factor — 12 gives ~250ms on modern hardware
BCRYPT_ROUNDS = 12

# ── Minimum password requirements ───────────────────────────
MIN_LENGTH      = 8
REQUIRE_UPPER   = True
REQUIRE_DIGIT   = True
REQUIRE_SPECIAL = True
SPECIAL_CHARS   = r"[!@#$%^&*(),.?\":{}|<>_\-\+\=\/\\]"


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password with bcrypt.
    Returns a UTF-8 string suitable for VARCHAR(255) storage.
    """
    encoded = plain.encode("utf-8")
    hashed  = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Constant-time compare of a plain password against a stored hash.
    Returns True if they match, False otherwise.
    Never raises — wrong-type inputs return False.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception as exc:
        logger.warning("Password verification error: %s", exc)
        return False


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Check password against policy rules.
    Returns (is_valid: bool, errors: list[str]).
    """
    errors = []

    if len(password) < MIN_LENGTH:
        errors.append(f"Password must be at least {MIN_LENGTH} characters long.")

    if REQUIRE_UPPER and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")

    if REQUIRE_DIGIT and not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number.")

    if REQUIRE_SPECIAL and not re.search(SPECIAL_CHARS, password):
        errors.append("Password must contain at least one special character (!@#$ etc.).")

    return len(errors) == 0, errors


def needs_rehash(hashed: str) -> bool:
    """
    Check whether a stored hash was created with an older work factor
    and should be upgraded on the next successful login.
    """
    try:
        return bcrypt.checkpw(b"", hashed.encode("utf-8"))
    except Exception:
        # checkpw raises if the rounds differ — that's fine, check manually
        try:
            current_rounds = int(hashed.split("$")[2])
            return current_rounds < BCRYPT_ROUNDS
        except Exception:
            return False
