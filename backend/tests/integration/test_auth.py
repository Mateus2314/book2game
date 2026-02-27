"""
Integration tests for authentication endpoints.

Tests cover:
- User registration with validation
- User login and authentication
- Token refresh mechanism
- Error handling for invalid credentials
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_refresh_token, get_password_hash
from app.models.user import User


@pytest.mark.integration
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == "newuser@example.com"
        assert user["full_name"] == "New User"
        assert user["is_active"] is True
        assert user["is_superuser"] is False
        assert "id" in user

    def test_register_duplicate_email(self, client: TestClient, db: Session):
        """Test registration with already registered email."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "differentpassword456",
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
        ]
        
        for email in invalid_emails:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "password123",
                }
            )
            
            # FastAPI returns 422 for Pydantic validation errors
            assert response.status_code == 422
            assert "email" in str(response.json()).lower()

    def test_register_short_password(self, client: TestClient):
        """Test registration with password too short."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",  # Less than 8 characters
            }
        )
        
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422

    def test_register_without_full_name(self, client: TestClient):
        """Test registration without full_name (optional field)."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "noname@example.com",
                "password": "password123",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["full_name"] is None


@pytest.mark.integration
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login with valid credentials."""
        # test_user has email="test@example.com", password="testpassword123"
        response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "test@example.com",
                "password": "testpassword123",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == "test@example.com"
        assert user["id"] == test_user.id

    def test_login_invalid_password(self, client: TestClient, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "test@example.com",
                "password": "wrongpassword",
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with email that doesn't exist."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "nonexistent@example.com",
                "password": "somepassword",
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "not-an-email",
                "password": "password123",
            }
        )
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing email or password."""
        # Missing password
        response = client.post(
            "/api/v1/auth/login",
            data={"email": "test@example.com"}
        )
        assert response.status_code == 422
        
        # Missing email
        response = client.post(
            "/api/v1/auth/login",
            data={"password": "password123"}
        )
        assert response.status_code == 422

    def test_login_inactive_user(self, client: TestClient, db: Session):
        """Test login for inactive user returns 400."""
        user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Inactive User",
            is_active=False,
            is_superuser=False,
        )
        db.add(user)
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "inactive@example.com",
                "password": "password123",
            }
        )

        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()


@pytest.mark.integration
class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_success(self, client: TestClient, test_user):
        """Test successful token refresh."""
        # Create a valid refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(test_user.id), "email": test_user.email}
        )
        
        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return new tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != refresh_token
        assert data["refresh_token"] != refresh_token

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": "invalid-token"}
        )
        
        assert response.status_code == 401
        assert "could not decode" in response.json()["detail"].lower()

    def test_refresh_token_with_access_token(self, client: TestClient, auth_token):
        """Test refresh endpoint with access token instead of refresh token."""
        # Try to use access token for refresh
        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": auth_token}
        )
        
        assert response.status_code == 401
        assert "type" in response.json()["detail"].lower()

    def test_refresh_token_nonexistent_user(self, client: TestClient):
        """Test refresh token for user that doesn't exist."""
        # Create refresh token for non-existent user ID
        fake_refresh_token = create_refresh_token(
            data={"sub": "99999", "email": "fake@example.com"}
        )
        
        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": fake_refresh_token}
        )
        
        assert response.status_code == 401
        assert "not found" in response.json()["detail"].lower()

    def test_refresh_token_missing_sub(self, client: TestClient, test_user: User):
        """Test refresh token missing sub claim."""
        refresh_token = create_refresh_token(
            data={"email": test_user.email}
        )

        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert "missing user id" in response.json()["detail"].lower()

    def test_refresh_token_invalid_sub_format(self, client: TestClient):
        """Test refresh token with invalid sub format."""
        refresh_token = create_refresh_token(
            data={"sub": "not-an-int", "email": "fake@example.com"}
        )

        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert "invalid user id format" in response.json()["detail"].lower()

    def test_refresh_token_inactive_user(self, client: TestClient, db: Session):
        """Test refresh token for inactive user returns 401."""
        user = User(
            email="inactive-refresh@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Inactive User",
            is_active=False,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()
