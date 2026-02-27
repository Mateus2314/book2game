"""
Unit tests for security module (password hashing and JWT tokens).

Tests cover:
- Password hashing and verification
- JWT token creation and decoding
- Token expiration handling
- Email validation
"""
import pytest
from datetime import timedelta, datetime
from freezegun import freeze_time
from jose import jwt

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_email,
)
from app.core.config import settings


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_get_password_hash(self):
        """Test that password is properly hashed."""
        password = "mySecurePassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        # Hash should be a non-empty string
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        # Hash should start with bcrypt identifier
        assert hashed.startswith("$2b$")

    def test_verify_password_valid(self):
        """Test password verification with correct password."""
        password = "mySecurePassword123"
        hashed = get_password_hash(password)
        
        # Correct password should verify successfully
        assert verify_password(password, hashed) is True

    def test_verify_password_invalid(self):
        """Test password verification with incorrect password."""
        password = "mySecurePassword123"
        wrong_password = "wrongPassword456"
        hashed = get_password_hash(password)
        
        # Wrong password should fail verification
        assert verify_password(wrong_password, hashed) is False

    def test_password_hash_is_unique(self):
        """Test that same password generates different hashes (salt)."""
        password = "mySecurePassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Different hashes due to different salts
        assert hash1 != hash2
        # Both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_password_hash_long_password(self):
        """Test password hashing with long password (bcrypt 72 byte limit)."""
        # Bcrypt has 72 byte limit
        long_password = "a" * 100
        hashed = get_password_hash(long_password)
        
        # Should hash and verify successfully (truncated to 72 bytes)
        assert verify_password(long_password, hashed) is True


@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token_with_default_expiry(self):
        """Test creating access token with default expiration."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_with_custom_expiry(self):
        """Test creating access token with custom expiration."""
        data = {"sub": "456"}
        expires_delta = timedelta(minutes=30)
        
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(data, expires_delta=expires_delta)
            payload = decode_token(token)
            
            assert payload is not None
            # Check expiration is approximately 30 minutes from now
            exp_time = datetime.utcfromtimestamp(payload["exp"])
            expected_time = datetime(2024, 1, 1, 12, 30, 0)
            assert abs((exp_time - expected_time).total_seconds()) < 2

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        data = {"sub": "789"}
        token = create_refresh_token(data)
        
        # Token should be valid
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "789"
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_decode_access_token_valid(self):
        """Test decoding a valid access token."""
        data = {"sub": "user123", "role": "admin"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "admin"
        assert decoded["type"] == "access"

    def test_decode_access_token_expired(self):
        """Test decoding an expired token."""
        data = {"sub": "user123"}
        
        # Create token that expires immediately
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Try to decode 2 seconds later (after expiration)
        with freeze_time("2024-01-01 12:00:03"):
            decoded = decode_token(token)
            
            # Should return None for expired token
            assert decoded is None

    def test_decode_access_token_invalid(self):
        """Test decoding an invalid/malformed token."""
        invalid_tokens = [
            "invalid.token.here",
            "not-a-jwt",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
        ]
        
        for invalid_token in invalid_tokens:
            decoded = decode_token(invalid_token)
            assert decoded is None

    def test_decode_token_with_wrong_secret(self):
        """Test that token signed with different secret fails."""
        data = {"sub": "user123"}
        
        # Create token with correct secret
        token = jwt.encode(data, "wrong-secret-key", algorithm=settings.ALGORITHM)
        
        # Try to decode with settings secret
        decoded = decode_token(token)
        
        # Should fail to decode
        assert decoded is None


@pytest.mark.unit
class TestEmailValidation:
    """Test email validation function."""

    def test_validate_email_valid(self):
        """Test validation with valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
            "a@b.co",
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True, f"Failed for {email}"

    def test_validate_email_invalid(self):
        """Test validation with invalid email addresses."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            "user@domain",
            "",
            "user@domain..com",
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False, f"Should fail for {email}"

    def test_validate_email_none(self):
        """Test validation with None value."""
        assert validate_email(None) is False

    def test_validate_email_non_string(self):
        """Test validation with non-string values."""
        assert validate_email(123) is False
        assert validate_email([]) is False
        assert validate_email({}) is False
