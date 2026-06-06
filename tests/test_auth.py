# ============================================================
#  MindFlow — Auth Service Unit Tests
#  tests/test_auth.py  |  stdlib unittest (no pytest needed)
# ============================================================

import unittest
from unittest.mock import patch, MagicMock

from backend.utils.password import (
    hash_password, verify_password,
    validate_password_strength,
)
from backend.utils.token import generate_session_token, safe_compare
from backend.utils.validators import validate_email, validate_full_name


class TestPasswordHashing(unittest.TestCase):

    def test_hash_is_not_plain_text(self):
        pw = "MySecret@99"
        h  = hash_password(pw)
        self.assertNotEqual(pw, h)
        self.assertTrue(h.startswith("$2b$"))

    def test_correct_password_verifies(self):
        pw = "Correct@Horse1"
        h  = hash_password(pw)
        self.assertTrue(verify_password(pw, h))

    def test_wrong_password_fails(self):
        h = hash_password("GoodPass@1")
        self.assertFalse(verify_password("WrongPass@1", h))

    def test_empty_password_fails(self):
        h = hash_password("Real@Pass1")
        self.assertFalse(verify_password("", h))

    def test_different_hashes_for_same_password(self):
        pw = "Same@Pass1"
        self.assertNotEqual(hash_password(pw), hash_password(pw))


class TestPasswordStrength(unittest.TestCase):

    def test_strong_password_passes(self):
        ok, errs = validate_password_strength("Str0ng@Pass!")
        self.assertTrue(ok); self.assertEqual(errs, [])

    def test_too_short_fails(self):
        ok, errs = validate_password_strength("Ab1!")
        self.assertFalse(ok)
        self.assertTrue(any("8 characters" in e for e in errs))

    def test_no_uppercase_fails(self):
        ok, errs = validate_password_strength("lowercase1!")
        self.assertFalse(ok)
        self.assertTrue(any("uppercase" in e for e in errs))

    def test_no_digit_fails(self):
        ok, errs = validate_password_strength("NoDigit@Here")
        self.assertFalse(ok)
        self.assertTrue(any("number" in e for e in errs))

    def test_no_special_fails(self):
        ok, errs = validate_password_strength("NoSpecial1A")
        self.assertFalse(ok)
        self.assertTrue(any("special" in e for e in errs))


class TestTokenGeneration(unittest.TestCase):

    def test_token_is_string(self):
        self.assertIsInstance(generate_session_token(), str)

    def test_tokens_are_unique(self):
        tokens = {generate_session_token() for _ in range(100)}
        self.assertEqual(len(tokens), 100)

    def test_safe_compare_same(self):
        self.assertTrue(safe_compare("abc", "abc"))

    def test_safe_compare_different(self):
        self.assertFalse(safe_compare("abc", "xyz"))


class TestValidators(unittest.TestCase):

    def test_valid_email(self):
        ok, err = validate_email("user@example.com")
        self.assertTrue(ok); self.assertIsNone(err)

    def test_invalid_email(self):
        ok, err = validate_email("userexample.com")
        self.assertFalse(ok); self.assertIsNotNone(err)

    def test_empty_email(self):
        ok, _ = validate_email("")
        self.assertFalse(ok)

    def test_valid_name(self):
        ok, err = validate_full_name("Sarah Williams")
        self.assertTrue(ok)

    def test_name_too_short(self):
        ok, _ = validate_full_name("X")
        self.assertFalse(ok)

    def test_name_with_numbers_fails(self):
        ok, _ = validate_full_name("Sarah123")
        self.assertFalse(ok)


class TestAuthServiceMocked(unittest.TestCase):

    @patch("backend.services.auth_service.UserRepository")
    @patch("backend.services.auth_service.SessionRepository")
    def test_register_success(self, mock_sess, mock_user):
        mock_user.email_exists.return_value = False
        mock_user.create.return_value       = 42
        mock_user.find_by_id.return_value   = MagicMock(
            id=42, to_dict=lambda: {"id": 42, "email": "t@e.com"}
        )
        mock_sess.create.return_value = 1

        from backend.services.auth_service import AuthService
        res = AuthService.register("Test User", "t@e.com", "Secure@Pass1")
        self.assertIn("user", res)
        self.assertIn("session_token", res)

    @patch("backend.services.auth_service.UserRepository")
    def test_register_duplicate_email(self, mock_user):
        mock_user.email_exists.return_value = True
        from backend.services.auth_service import AuthService, EmailAlreadyExistsError
        with self.assertRaises(EmailAlreadyExistsError):
            AuthService.register("Test", "dupe@e.com", "Secure@Pass1")

    @patch("backend.services.auth_service.UserRepository")
    @patch("backend.services.auth_service.SessionRepository")
    @patch("backend.services.auth_service.verify_password", return_value=True)
    @patch("backend.services.auth_service.needs_rehash",    return_value=False)
    def test_login_success(self, _r, _v, mock_sess, mock_user):
        u = MagicMock(id=1, is_active=True, to_dict=lambda: {"id": 1})
        mock_user.find_by_email.return_value = u
        mock_sess.create.return_value = 10
        from backend.services.auth_service import AuthService
        res = AuthService.login("u@e.com", "Secure@Pass1")
        self.assertIn("session_token", res)

    @patch("backend.services.auth_service.UserRepository")
    def test_login_unknown_email(self, mock_user):
        mock_user.find_by_email.return_value = None
        from backend.services.auth_service import AuthService, InvalidCredentialsError
        with self.assertRaises(InvalidCredentialsError):
            AuthService.login("no@e.com", "Secure@Pass1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
