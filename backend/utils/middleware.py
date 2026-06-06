# ============================================================
#  MindFlow — Auth Middleware / Decorators
#  utils/middleware.py  |  Pure Python (no framework)
# ============================================================

import functools
import logging
from http.cookies import SimpleCookie
from typing import Callable

from backend.services.auth_service import AuthService, SessionExpiredError, AccountInactiveError
from backend.utils.response import unauthorized, forbidden

logger = logging.getLogger(__name__)

SESSION_COOKIE = "mf_session"


def get_token_from_request(headers: dict) -> str | None:
    """
    Extract session token from:
      1. Cookie: mf_session=<token>
      2. Authorization: Bearer <token>  (for API / JS fetch calls)
    """
    # Check Authorization header first (API clients)
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    # Fall back to cookie
    cookie_header = headers.get("Cookie", "")
    if cookie_header:
        cookie = SimpleCookie()
        cookie.load(cookie_header)
        morsel = cookie.get(SESSION_COOKIE)
        if morsel:
            return morsel.value

    return None


def require_auth(handler: Callable) -> Callable:
    """
    Decorator for route handlers that require an authenticated user.

    Injects `current_user` into handler kwargs.

    Usage (with the bare server.py dispatcher):
        @require_auth
        def handle_dashboard(request, current_user):
            ...
    """
    @functools.wraps(handler)
    def wrapper(request, *args, **kwargs):
        token = get_token_from_request(request.get("headers", {}))
        try:
            user = AuthService.get_current_user(token)
        except (SessionExpiredError, AccountInactiveError) as exc:
            return unauthorized(exc.message)
        except Exception as exc:
            logger.error("Auth middleware error: %s", exc)
            return unauthorized("Authentication failed.")

        kwargs["current_user"] = user
        return handler(request, *args, **kwargs)

    return wrapper


def require_admin(handler: Callable) -> Callable:
    """
    Decorator that requires the user to be an admin.
    Stacks on top of require_auth.
    """
    @functools.wraps(handler)
    @require_auth
    def wrapper(request, *args, **kwargs):
        user = kwargs.get("current_user")
        # Check admin flag — simple boolean on users table
        if not getattr(user, "is_admin", False):
            return forbidden("Admin privileges required.")
        return handler(request, *args, **kwargs)

    return wrapper


def set_session_cookie(headers: dict, token: str, days: int = 1, secure: bool = True) -> dict:
    """
    Append a Set-Cookie header for the session token.
    Returns updated headers dict.
    """
    max_age  = days * 86_400
    flags    = f"Max-Age={max_age}; Path=/; HttpOnly; SameSite=Strict"
    if secure:
        flags += "; Secure"
    headers["Set-Cookie"] = f"{SESSION_COOKIE}={token}; {flags}"
    return headers


def clear_session_cookie(headers: dict) -> dict:
    """Expire the session cookie immediately (for logout)."""
    headers["Set-Cookie"] = (
        f"{SESSION_COOKIE}=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict"
    )
    return headers
