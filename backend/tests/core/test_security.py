"""
test_security.py
Unit tests for the core security module (app/core/security.py).
These are fully deterministic — no database or HTTP client needed.
"""
import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
import jwt
from datetime import timedelta


class TestPasswordHashing:
    """Tests for bcrypt password hashing."""

    def test_hash_is_not_plaintext(self):
        """The hashed password must never equal the original plaintext."""
        plain = "MySuperSecret123!"
        hashed = get_password_hash(plain)
        assert hashed != plain

    def test_hash_starts_with_bcrypt_prefix(self):
        """bcrypt hashes always start with '$2b$', confirming the correct algorithm."""
        hashed = get_password_hash("any_password")
        assert hashed.startswith("$2b$")

    def test_same_password_produces_different_hashes(self):
        """Because of the random salt, hashing the same password twice must produce
        two *different* hashes (salted hashing)."""
        plain = "SamePassword"
        hash1 = get_password_hash(plain)
        hash2 = get_password_hash(plain)
        assert hash1 != hash2

    def test_hash_is_string(self):
        """The output of get_password_hash must be a Python string."""
        hashed = get_password_hash("test_password")
        assert isinstance(hashed, str)


class TestPasswordVerification:
    """Tests for bcrypt password verification."""

    def test_correct_password_returns_true(self):
        """verify_password must return True for the correct plaintext password."""
        plain = "CorrectPassword"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self):
        """verify_password must return False for an incorrect plaintext password."""
        plain = "CorrectPassword"
        hashed = get_password_hash(plain)
        assert verify_password("WrongPassword", hashed) is False

    def test_empty_password_is_rejected(self):
        """An empty string must not match a hashed non-empty password."""
        hashed = get_password_hash("some_password")
        assert verify_password("", hashed) is False

    def test_case_sensitive_verification(self):
        """Password verification must be case-sensitive."""
        plain = "CaseSensitive"
        hashed = get_password_hash(plain)
        assert verify_password("casesensitive", hashed) is False
        assert verify_password("CASESENSITIVE", hashed) is False


class TestAccessTokenCreation:
    """Tests for JWT access token generation."""

    def test_token_is_a_string(self):
        """create_access_token must return a string."""
        token = create_access_token(subject="user_id_42")
        assert isinstance(token, str)

    def test_token_contains_correct_subject(self):
        """The decoded token payload must contain the correct 'sub' claim."""
        user_id = "99"
        token = create_access_token(subject=user_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id

    def test_token_contains_expiry(self):
        """The decoded token payload must contain an 'exp' claim."""
        token = create_access_token(subject="user_id_1")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_custom_expiry_is_respected(self):
        """A token created with a custom expiry should have a later 'exp' than default."""
        import time
        default_token = create_access_token(subject="u1")
        long_token = create_access_token(subject="u1", expires_delta=timedelta(hours=24))
        
        default_payload = jwt.decode(default_token, SECRET_KEY, algorithms=[ALGORITHM])
        long_payload = jwt.decode(long_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert long_payload["exp"] > default_payload["exp"]
