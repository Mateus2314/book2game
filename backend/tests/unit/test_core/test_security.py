import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    validate_email,
    verify_password,
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


@pytest.mark.unit
class TestEmailValidation:
    """Test email validation."""

    def test_valid_emails(self):
        """Test valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "first+last@test.io",
            "123@test.com",
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True, f"Failed for {email}"

    def test_invalid_emails(self):
        """Test invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "",
            None,
            "user@domain",
            "user..name@example.com",
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False, f"Should fail for {email}"


@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == 1
        assert decoded["email"] == "test@example.com"
        assert decoded["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        
        decoded = decode_token(invalid_token)
        
        assert decoded is None

    def test_token_types(self):
        """Test different token types."""
        data = {"sub": 1}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
