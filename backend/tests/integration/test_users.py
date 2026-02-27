"""
Integration tests for user endpoints.

Tests cover:
- Getting current user profile
- Updating user profile (email, full_name, password)
- Authentication and authorization requirements
- User profile validation
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password


@pytest.mark.integration
class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_me_authenticated(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting current user profile with valid authentication."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user data matches test_user
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_me_unauthenticated(self, client: TestClient):
        """Test getting profile without authentication."""
        response = client.get("/api/v1/users/me")
        
        # Should return 401 Unauthorized (no auth header provided)
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client: TestClient):
        """Test getting profile with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid-token-here"}
        response = client.get("/api/v1/users/me", headers=invalid_headers)
        
        assert response.status_code == 401


@pytest.mark.integration
class TestUserProfileUpdate:
    """Test user profile update endpoint."""

    def test_update_full_name(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test updating user's full name."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "Updated Name"
        assert data["email"] == test_user.email  # Email unchanged

    def test_update_email(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test updating user's email address."""
        new_email = "newemail@example.com"
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": new_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == new_email
        assert data["id"] == test_user.id

    def test_update_password(self, client: TestClient, test_user: User, auth_headers: dict, db: Session):
        """Test updating user's password."""
        new_password = "newSecurePassword456"
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"password": new_password}
        )
        
        assert response.status_code == 200
        
        # Verify password was updated by trying to login
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "email": test_user.email,
                "password": new_password
            }
        )
        
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_update_email_to_existing(self, client: TestClient, test_user: User, auth_headers: dict, db: Session):
        """Test updating email to one that already exists."""
        # Create another user
        from app.core.security import get_password_hash
        other_user = User(
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other User"
        )
        db.add(other_user)
        db.commit()
        
        # Try to update test_user's email to other_user's email
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "other@example.com"}
        )
        
        # Should fail with 400 Bad Request
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_update_email_invalid_format(self, client: TestClient, auth_headers: dict):
        """Test updating email with invalid format."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "not-an-email"}
        )
        
        # Should fail validation
        assert response.status_code in [400, 422]

    def test_update_password_too_short(self, client: TestClient, auth_headers: dict):
        """Test updating password with too short value."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"password": "short"}  # Less than 8 characters
        )
        
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422

    def test_update_profile_unauthenticated(self, client: TestClient):
        """Test updating profile without authentication."""
        response = client.put(
            "/api/v1/users/me",
            json={"full_name": "Hacker Name"}
        )
        
        # Should require authentication (401 = Unauthorized/Not authenticated)
        assert response.status_code == 401

    def test_update_multiple_fields(self, client: TestClient, auth_headers: dict):
        """Test updating multiple profile fields at once."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "full_name": "New Full Name",
                "email": "multupdate@example.com",
                "password": "newPassword789"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "New Full Name"
        assert data["email"] == "multupdate@example.com"
        
        # Verify new password works
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "multupdate@example.com",
                "password": "newPassword789"
            }
        )
        
        assert login_response.status_code == 200


@pytest.mark.integration
class TestUserRecommendations:
    """Test user recommendations endpoint."""

    def test_get_recommendations_authenticated(self, client: TestClient, auth_headers: dict):
        """Test getting user recommendations with authentication."""
        response = client.get("/api/v1/users/me/recommendations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return list (empty initially)
        assert isinstance(data, list)

    def test_get_recommendations_with_pagination(self, client: TestClient, auth_headers: dict):
        """Test recommendations with pagination parameters."""
        response = client.get(
            "/api/v1/users/me/recommendations?skip=0&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_get_recommendations_unauthenticated(self, client: TestClient):
        """Test getting recommendations without authentication."""
        response = client.get("/api/v1/users/me/recommendations")
        
        # 401 = Not authenticated (no token provided)
        assert response.status_code == 401
