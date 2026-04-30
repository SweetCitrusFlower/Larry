"""
test_auth.py
Integration tests for the authentication API endpoints.
Routes tested:
  - POST /api/v1/auth/register
  - POST /api/v1/auth/login

All tests use the in-memory SQLite database injected via conftest.py.
"""
import pytest

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

VALID_USER = {
    "email": "test@larry.ai",
    "password": "SecurePassword123!",
}


def register_user(client, email=None, password=None):
    """Helper to register a user with optional overrides."""
    payload = {
        "email": email or VALID_USER["email"],
        "password": password or VALID_USER["password"],
    }
    return client.post(REGISTER_URL, json=payload)


# ─────────────────────────────────────────────
# Registration Tests
# ─────────────────────────────────────────────
class TestUserRegistration:
    """Tests for POST /api/v1/auth/register"""

    def test_register_new_user_returns_201_or_200(self, client):
        """Registering a brand-new email must succeed (2xx status)."""
        response = register_user(client)
        assert response.status_code in (200, 201), response.text

    def test_register_new_user_returns_email(self, client):
        """The response body must include the registered email address."""
        response = register_user(client)
        assert response.json()["email"] == VALID_USER["email"]

    def test_register_password_is_not_in_response(self, client):
        """The plaintext password must NEVER appear in the API response."""
        response = register_user(client)
        response_text = response.text
        assert VALID_USER["password"] not in response_text

    def test_register_duplicate_email_returns_400(self, client):
        """Registering the same email twice must return HTTP 400 Bad Request."""
        register_user(client)  # First registration — must succeed
        second_response = register_user(client)  # Duplicate — must fail
        assert second_response.status_code == 400

    def test_register_duplicate_email_error_message(self, client):
        """The 400 error for a duplicate email must contain a meaningful message."""
        register_user(client)
        response = register_user(client)
        detail = response.json().get("detail", "")
        assert "already exists" in detail or "already registered" in detail or len(detail) > 0

    def test_register_invalid_email_returns_422(self, client):
        """Registering with a malformed email must return HTTP 422 Unprocessable Entity."""
        response = client.post(REGISTER_URL, json={"email": "not-an-email", "password": "abc"})
        assert response.status_code == 422

    def test_register_missing_password_returns_422(self, client):
        """Omitting the password field must return HTTP 422."""
        response = client.post(REGISTER_URL, json={"email": "user@test.com"})
        assert response.status_code == 422


# ─────────────────────────────────────────────
# Login Tests
# ─────────────────────────────────────────────
class TestUserLogin:
    """Tests for POST /api/v1/auth/login"""

    def _register_and_login(self, client, email=None, password=None):
        """Register a user and attempt to login, returning the login response."""
        email = email or VALID_USER["email"]
        password = password or VALID_USER["password"]
        register_user(client, email=email, password=password)
        # Login uses OAuth2 form data (application/x-www-form-urlencoded)
        return client.post(
            LOGIN_URL,
            data={"username": email, "password": password},
        )

    def test_login_valid_credentials_returns_200(self, client):
        """A valid login must return HTTP 200 OK."""
        response = self._register_and_login(client)
        assert response.status_code == 200, response.text

    def test_login_returns_access_token(self, client):
        """A valid login response must include an 'access_token' field."""
        response = self._register_and_login(client)
        data = response.json()
        assert "access_token" in data
        assert len(data["access_token"]) > 0

    def test_login_returns_bearer_token_type(self, client):
        """The token_type in the login response must be 'bearer'."""
        response = self._register_and_login(client)
        assert response.json()["token_type"] == "bearer"

    def test_login_wrong_password_returns_400(self, client):
        """Login with a wrong password must return HTTP 400 Bad Request."""
        register_user(client)
        response = client.post(
            LOGIN_URL,
            data={"username": VALID_USER["email"], "password": "WrongPassword!"},
        )
        assert response.status_code == 400

    def test_login_nonexistent_user_returns_400(self, client):
        """Attempting to login with a non-existent email must return HTTP 400."""
        response = client.post(
            LOGIN_URL,
            data={"username": "ghost@larry.ai", "password": "doesntmatter"},
        )
        assert response.status_code == 400

    def test_login_wrong_password_has_no_token(self, client):
        """A failed login response must NOT contain any access_token."""
        register_user(client)
        response = client.post(
            LOGIN_URL,
            data={"username": VALID_USER["email"], "password": "BadPassword!"},
        )
        assert "access_token" not in response.json()

    def test_login_case_sensitive_password(self, client):
        """Passwords are case-sensitive; all-uppercase should fail."""
        register_user(client)
        response = client.post(
            LOGIN_URL,
            data={
                "username": VALID_USER["email"],
                "password": VALID_USER["password"].upper(),
            },
        )
        assert response.status_code == 400
