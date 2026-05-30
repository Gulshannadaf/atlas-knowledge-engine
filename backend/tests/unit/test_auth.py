"""Unit tests for authentication service."""

from app.services.auth import AuthService


class TestAuthService:
    """Tests for AuthService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.auth_service = AuthService()

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = self.auth_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test correct password verification."""
        password = "test_password_123"
        hashed = self.auth_service.hash_password(password)

        assert self.auth_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test incorrect password verification."""
        password = "test_password_123"
        hashed = self.auth_service.hash_password(password)

        assert self.auth_service.verify_password("wrong_password", hashed) is False

    def test_create_access_token(self):
        """Test access token creation."""
        user_id = "test-user-id"
        token = self.auth_service.create_access_token(user_id)

        assert token is not None
        assert len(token) > 0

    def test_verify_access_token(self):
        """Test access token verification."""
        user_id = "test-user-id"
        token = self.auth_service.create_access_token(user_id)
        payload = self.auth_service.verify_access_token(token)

        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "access"

    def test_verify_invalid_token(self):
        """Test invalid token verification."""
        payload = self.auth_service.verify_access_token("invalid-token")
        assert payload is None

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user_id = "test-user-id"
        token = self.auth_service.create_refresh_token(user_id)

        assert token is not None
        assert len(token) > 0

    def test_verify_refresh_token(self):
        """Test refresh token verification."""
        user_id = "test-user-id"
        token = self.auth_service.create_refresh_token(user_id)
        payload = self.auth_service.verify_refresh_token(token)

        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "refresh"

    def test_access_token_not_valid_as_refresh(self):
        """Test that access token cannot be used as refresh token."""
        user_id = "test-user-id"
        access_token = self.auth_service.create_access_token(user_id)
        payload = self.auth_service.verify_refresh_token(access_token)

        assert payload is None
