import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# Test database
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_token(client):
    """Create a user and return auth token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    
    return response.json()["access_token"]


@pytest.mark.integration
class TestUsersEndpoints:
    """Test users endpoints."""

    def test_get_current_user_profile(self, client, auth_token):
        """Test getting current user profile."""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
        assert "is_active" in data
        assert "hashed_password" not in data

    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token."""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

    def test_update_user_profile_full_name(self, client, auth_token):
        """Test updating user's full name."""
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"full_name": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == "testuser@example.com"

    def test_update_user_profile_email(self, client, auth_token):
        """Test updating user's email."""
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"

    def test_update_user_profile_password(self, client, auth_token):
        """Test updating user's password."""
        # Update password
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"password": "newpassword123"}
        )
        
        assert response.status_code == 200
        
        # Try login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "testuser@example.com",
                "password": "newpassword123",
            },
        )
        
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_update_user_profile_invalid_email(self, client, auth_token):
        """Test updating with invalid email format."""
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"email": "invalid-email"}
        )
        
        assert response.status_code == 400

    def test_update_user_profile_short_password(self, client, auth_token):
        """Test updating with too short password."""
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"password": "short"}
        )
        
        assert response.status_code == 422

    def test_update_user_profile_multiple_fields(self, client, auth_token):
        """Test updating multiple fields at once."""
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "email": "updated@example.com",
                "full_name": "Updated User",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["full_name"] == "Updated User"

    def test_update_user_profile_empty_request(self, client, auth_token):
        """Test updating with empty request body."""
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        
        # Should succeed but not change anything
        assert response.status_code == 200

    def test_get_user_recommendations(self, client, auth_token):
        """Test getting user's recommendations."""
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_recommendations_pagination(self, client, auth_token):
        """Test recommendations pagination."""
        response = client.get(
            "/api/v1/users/me/recommendations?skip=0&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_get_user_recommendations_invalid_params(self, client, auth_token):
        """Test recommendations with invalid params."""
        # Negative skip
        response = client.get(
            "/api/v1/users/me/recommendations?skip=-1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422
        
        # Limit too high
        response = client.get(
            "/api/v1/users/me/recommendations?limit=200",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    def test_user_isolation(self, client, auth_token):
        """Test that users can only see their own data."""
        # Create second user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "password": "password123",
                "full_name": "User Two",
            },
        )
        
        user2_response = client.post(
            "/api/v1/auth/login",
            data={
                "email": "user2@example.com",
                "password": "password123",
            },
        )
        user2_token = user2_response.json()["access_token"]
        
        # Get user2 profile
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user2@example.com"
        # Should not see first user's data
        assert data["email"] != "testuser@example.com"
