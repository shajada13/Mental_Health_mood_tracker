# ============================================================
#  MindFlow — Authentication Service
#  services/auth_service.py  |  Pure Python (no framework)
# ============================================================

from __future__ import annotations
import logging
from typing import Optional

from backend.models.user    import User, UserRepository
from backend.models.session import SessionRepository
from backend.utils.password import (
    hash_password,
    verify_password,
    validate_password_strength,
    needs_rehash,
)
from backend.utils.token      import generate_session_token
from backend.utils.validators import validate_email, validate_full_name

logger = logging.getLogger(__name__)


# ── Custom domain exceptions ─────────────────────────────────
class AuthError(Exception):
    """Base authentication exception."""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code    = code
        super().__init__(message)

class EmailAlreadyExistsError(AuthError):
    def __init__(self):
        super().__init__("An account with this email already exists.", code=409)

class InvalidCredentialsError(AuthError):
    def __init__(self):
        # Generic message prevents user-enumeration attacks
        super().__init__("Invalid email or password.", code=401)

class AccountInactiveError(AuthError):
    def __init__(self):
        super().__init__("This account has been deactivated. Please contact support.", code=403)

class SessionExpiredError(AuthError):
    def __init__(self):
        super().__init__("Your session has expired. Please log in again.", code=401)

class WeakPasswordError(AuthError):
    def __init__(self, errors: list[str]):
        self.password_errors = errors
        super().__init__("Password does not meet requirements.", code=400)


# ── Auth Service ─────────────────────────────────────────────
class AuthService:

    # ── REGISTER ────────────────────────────────────────────
    @staticmethod
    def register(
        full_name:      str,
        email:          str,
        password:       str,
        date_of_birth:  Optional[str] = None,
        gender:         str           = "prefer_not_to_say",
        primary_goal:   str           = "improve_mood",
    ) -> dict:
        """
        Create a new user account.

        Returns:
            dict with keys: user (dict), session_token (str)

        Raises:
            AuthError subclasses on validation / business-logic failures.
        """
        # ── 1. Input validation ──────────────────────────────
        name_ok, name_err = validate_full_name(full_name)
        if not name_ok:
            raise AuthError(name_err, code=400)

        email_ok, email_err = validate_email(email)
        if not email_ok:
            raise AuthError(email_err, code=400)

        pw_ok, pw_errors = validate_password_strength(password)
        if not pw_ok:
            raise WeakPasswordError(pw_errors)

        # ── 2. Duplicate email check ─────────────────────────
        if UserRepository.email_exists(email):
            raise EmailAlreadyExistsError()

        # ── 3. Hash password ─────────────────────────────────
        pw_hash = hash_password(password)

        # ── 4. Persist user ──────────────────────────────────
        user_id = UserRepository.create(
            full_name    = full_name,
            email        = email,
            password_hash= pw_hash,
            date_of_birth= date_of_birth,
            gender       = gender,
            primary_goal = primary_goal,
        )
        logger.info("New user registered: id=%s email=%s", user_id, email)

        # ── 5. Create initial session ────────────────────────
        token = generate_session_token()
        SessionRepository.create(
            user_id    = user_id,
            token      = token,
            remember_me= False,
        )

        # ── 6. Fetch & return user ───────────────────────────
        user = UserRepository.find_by_id(user_id)
        return {
            "user":          user.to_dict(),
            "session_token": token,
        }

    # ── LOGIN ────────────────────────────────────────────────
    @staticmethod
    def login(
        email:       str,
        password:    str,
        remember_me: bool = False,
        ip_address:  str  = "",
        user_agent:  str  = "",
    ) -> dict:
        """
        Authenticate a user and create a new session.

        Returns:
            dict with keys: user (dict), session_token (str), expires_in_days (int)

        Raises:
            AuthError subclasses on failure.
        """
        # ── 1. Basic input checks ────────────────────────────
        if not email or not password:
            raise AuthError("Email and password are required.", code=400)

        # ── 2. Lookup user (by email) ────────────────────────
        user = UserRepository.find_by_email(email)

        # Generic "invalid credentials" for both wrong email AND wrong password
        # to prevent user enumeration
        if user is None:
            logger.warning("Login attempt for unknown email: %s", email)
            raise InvalidCredentialsError()

        # ── 3. Check account status ──────────────────────────
        if not user.is_active:
            raise AccountInactiveError()

        # ── 4. Verify password ───────────────────────────────
        if not verify_password(password, user.password_hash):
            logger.warning("Failed login for user id=%s", user.id)
            raise InvalidCredentialsError()

        # ── 5. Opportunistic password rehash (if rounds changed) ──
        if needs_rehash(user.password_hash):
            new_hash = hash_password(password)
            UserRepository.update_password(user.id, new_hash)
            logger.info("Password rehashed for user id=%s", user.id)

        # ── 6. Update last-login timestamp ───────────────────
        UserRepository.update_last_login(user.id)

        # ── 7. Issue session token ───────────────────────────
        token = generate_session_token()
        SessionRepository.create(
            user_id    = user.id,
            token      = token,
            remember_me= remember_me,
            ip_address = ip_address,
            user_agent = user_agent,
        )
        logger.info("User id=%s logged in (remember_me=%s)", user.id, remember_me)

        from backend.models.session import (
            SESSION_DURATION_DAYS,
            SESSION_DURATION_REMEMBER_DAYS,
        )
        expires_days = SESSION_DURATION_REMEMBER_DAYS if remember_me else SESSION_DURATION_DAYS

        return {
            "user":            user.to_dict(),
            "session_token":   token,
            "expires_in_days": expires_days,
        }

    # ── LOGOUT ───────────────────────────────────────────────
    @staticmethod
    def logout(session_token: str) -> None:
        """Invalidate the current session token."""
        if session_token:
            SessionRepository.invalidate(session_token)
            logger.info("Session invalidated")

    # ── LOGOUT ALL DEVICES ───────────────────────────────────
    @staticmethod
    def logout_all_devices(user_id: int) -> None:
        """Invalidate ALL sessions for a user (e.g. after password change)."""
        SessionRepository.invalidate_all_for_user(user_id)
        logger.info("All sessions cleared for user id=%s", user_id)

    # ── GET CURRENT USER (session check) ─────────────────────
    @staticmethod
    def get_current_user(session_token: str) -> User:
        """
        Validate a session token and return the authenticated User.

        Raises SessionExpiredError if token is missing or expired.
        """
        if not session_token:
            raise SessionExpiredError()

        session = SessionRepository.find_by_token(session_token)
        if not session:
            raise SessionExpiredError()

        user = UserRepository.find_by_id(session.user_id)
        if not user or not user.is_active:
            raise SessionExpiredError()

        return user

    # ── CHANGE PASSWORD ───────────────────────────────────────
    @staticmethod
    def change_password(
        user_id:      int,
        old_password: str,
        new_password: str,
    ) -> None:
        """
        Verify old password then store a new hash.
        Invalidates all existing sessions to force re-login.
        """
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise AuthError("User not found.", code=404)

        if not verify_password(old_password, user.password_hash):
            raise AuthError("Current password is incorrect.", code=401)

        pw_ok, pw_errors = validate_password_strength(new_password)
        if not pw_ok:
            raise WeakPasswordError(pw_errors)

        new_hash = hash_password(new_password)
        UserRepository.update_password(user_id, new_hash)
        AuthService.logout_all_devices(user_id)
        logger.info("Password changed for user id=%s", user_id)
