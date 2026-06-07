# ============================================================
#  MindFlow — Auth Route Handlers
#  routes/auth_routes.py  |  Pure Python (no framework)
#
#  These are plain functions, not Flask/Django views.
#  server.py dispatches to them based on METHOD + PATH.
#
#  Each handler receives a `request` dict:
#    {
#      "method":  "POST",
#      "path":    "/api/auth/login",
#      "body":    {...},          # parsed JSON body
#      "headers": {...},          # HTTP headers dict
#      "query":   {...},          # URL query params
#    }
#
#  Each handler returns (status_code, body_str, headers_dict).
# ============================================================

import logging

from backend.services.auth_service import (
    AuthService,
    AuthError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    AccountInactiveError,
    SessionExpiredError,
    WeakPasswordError,
)
from backend.utils.response  import (
    ok, created, bad_request, unauthorized,
    forbidden, conflict, server_error,
)
from backend.utils.middleware import (
    get_token_from_request,
    set_session_cookie,
    clear_session_cookie,
    require_auth,
)

logger = logging.getLogger(__name__)


# ── POST /api/auth/register ──────────────────────────────────
def register(request: dict) -> tuple:
    """
    Register a new user.

    Body (JSON):
        full_name     : str  (required)
        email         : str  (required)
        password      : str  (required)
        date_of_birth : str  (optional, YYYY-MM-DD)
        gender        : str  (optional)
        primary_goal  : str  (optional)
    """
    body = request.get("body", {})

    full_name     = body.get("full_name", "").strip()
    email         = body.get("email", "").strip()
    password      = body.get("password", "")
    date_of_birth = body.get("date_of_birth") or None
    gender        = body.get("gender", "prefer_not_to_say")
    primary_goal  = body.get("primary_goal", "improve_mood")

    try:
        result = AuthService.register(
            full_name     = full_name,
            email         = email,
            password      = password,
            date_of_birth = date_of_birth,
            gender        = gender,
            primary_goal  = primary_goal,
        )
    except EmailAlreadyExistsError as exc:
        return conflict(exc.message)
    except WeakPasswordError as exc:
        return bad_request(exc.message, errors=exc.password_errors)
    except AuthError as exc:
        return bad_request(exc.message)
    except Exception as exc:
        logger.exception("Unexpected error during register: %s", exc)
        return server_error()

    # Set HttpOnly session cookie
    token       = result["session_token"]
    status, body_str, headers = created(
        data    = {"user": result["user"]},
        message = "Account created successfully. Welcome to MindFlow!"
    )
    headers = set_session_cookie(headers, token, days=1, secure=False)  # secure=True in production
    return status, body_str, headers


# ── POST /api/auth/login ─────────────────────────────────────
def login(request: dict) -> tuple:
    """
    Authenticate user and issue a session cookie.

    Body (JSON):
        email       : str   (required)
        password    : str   (required)
        remember_me : bool  (optional, default false)
    """
    body        = request.get("body", {})
    headers_in  = request.get("headers", {})

    email       = body.get("email", "").strip()
    password    = body.get("password", "")
    remember_me = bool(body.get("remember_me", False))

    # Pull IP and user-agent for session audit log
    ip          = headers_in.get("X-Forwarded-For") or headers_in.get("REMOTE_ADDR", "")
    user_agent  = headers_in.get("User-Agent", "")

    try:
        result = AuthService.login(
            email       = email,
            password    = password,
            remember_me = remember_me,
            ip_address  = ip,
            user_agent  = user_agent,
        )
    except (InvalidCredentialsError, AccountInactiveError) as exc:
        return unauthorized(exc.message)
    except AuthError as exc:
        return bad_request(exc.message)
    except Exception as exc:
        logger.exception("Unexpected error during login: %s", exc)
        return server_error()

    token        = result["session_token"]
    expires_days = result["expires_in_days"]

    status, body_str, resp_headers = ok(
        data    = {"user": result["user"]},
        message = "Login successful."
    )
    resp_headers = set_session_cookie(
        resp_headers, token, days=expires_days, secure=False
    )
    return status, body_str, resp_headers


# ── POST /api/auth/logout ────────────────────────────────────
def logout(request: dict) -> tuple:
    """
    Invalidate current session and clear cookie.
    """
    token = get_token_from_request(request.get("headers", {}))
    try:
        AuthService.logout(token)
    except Exception as exc:
        logger.warning("Logout error (non-critical): %s", exc)

    status, body_str, headers = ok(message="Logged out successfully.")
    headers = clear_session_cookie(headers)
    return status, body_str, headers


# ── GET /api/auth/me ─────────────────────────────────────────
@require_auth
def me(request: dict, current_user=None) -> tuple:
    """
    Return the currently authenticated user's profile.
    Requires a valid session cookie or Bearer token.
    """
    return ok(data={"user": current_user.to_dict()}, message="Authenticated.")


# ── POST /api/auth/change-password ───────────────────────────
@require_auth
def change_password(request: dict, current_user=None) -> tuple:
    """
    Change the authenticated user's password.

    Body (JSON):
        old_password : str (required)
        new_password : str (required)
    """
    body         = request.get("body", {})
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")

    if not old_password or not new_password:
        return bad_request("Both old_password and new_password are required.")

    try:
        AuthService.change_password(current_user.id, old_password, new_password)
    except WeakPasswordError as exc:
        return bad_request(exc.message, errors=exc.password_errors)
    except AuthError as exc:
        return bad_request(exc.message)
    except Exception as exc:
        logger.exception("Change-password error: %s", exc)
        return server_error()

    status, body_str, headers = ok(
        message="Password changed. Please log in again on all devices."
    )
    headers = clear_session_cookie(headers)
    return status, body_str, headers


# ── POST /api/auth/logout-all ────────────────────────────────
@require_auth
def logout_all(request: dict, current_user=None) -> tuple:
    """Invalidate every active session for the current user."""
    try:
        AuthService.logout_all_devices(current_user.id)
    except Exception as exc:
        logger.exception("Logout-all error: %s", exc)
        return server_error()

    status, body_str, headers = ok(message="All sessions terminated.")
    headers = clear_session_cookie(headers)
    return status, body_str, headers
