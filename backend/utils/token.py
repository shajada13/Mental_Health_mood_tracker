# ============================================================
#  MindFlow — Token Utilities
#  utils/token.py  |  Pure Python secrets + HMAC
#  No JWT library dependency — uses signed tokens stored in DB
# ============================================================

import hmac
import hashlib
import secrets
import time
import base64
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Secret pulled from .env — must be set in production
_SECRET = os.getenv("SECRET_KEY", "change-me-in-production").encode("utf-8")

TOKEN_BYTES       = 32   # 256-bit session token
CSRF_TOKEN_BYTES  = 24


def generate_session_token() -> str:
    """
    Generate a cryptographically secure, URL-safe session token.
    Stored in the sessions table and sent to the client as a cookie.
    """
    raw    = secrets.token_bytes(TOKEN_BYTES)
    stamp  = str(int(time.time())).encode()
    sig    = hmac.new(_SECRET, raw + stamp, hashlib.sha256).digest()
    joined = raw + stamp + sig
    return base64.urlsafe_b64encode(joined).decode("utf-8").rstrip("=")


def generate_csrf_token() -> str:
    """Short-lived CSRF token embedded in HTML forms."""
    return secrets.token_urlsafe(CSRF_TOKEN_BYTES)


def generate_verification_token() -> str:
    """Email-verification / password-reset one-time token."""
    return secrets.token_urlsafe(32)


def safe_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    return hmac.compare_digest(
        a.encode("utf-8") if isinstance(a, str) else a,
        b.encode("utf-8") if isinstance(b, str) else b,
    )
