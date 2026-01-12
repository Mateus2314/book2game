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


@pytest.mark.integration
class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "New User",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
            },
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
            },
        )
        
        # Try to register again with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password456",
            },
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client):
        """Test successful login."""
        # Register user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "password123",
            },
        )
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            params={
                "email": "logintest@example.com",
                "password": "password123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # Register user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "password123",
            },
        )
        
        # Try login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            params={
                "email": "wrongpass@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            params={
                "email": "notfound@example.com",
                "password": "password123",
            },
        )
        
        assert response.status_code == 401

    def test_login_invalid_email(self, client):
        """Test login with invalid email format."""
        response = client.post(
            "/api/v1/auth/login",
            params={
                "email": "invalid-email",
                "password": "password123",
            },
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "password123",
            },
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            params={
                "email": "refresh@example.com",
                "password": "password123",
            },
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh-token",
            params={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh-token",
            params={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_rate_limiting_register(self, client):
        """Test rate limiting on register endpoint."""
        # Make 6 requests (limit is 5/minute)
        for i in range(6):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"ratelimit{i}@example.com",
                    "password": "password123",
                },
            )
            
            if i < 5:
                # First 5 should succeed or fail for business reasons
                assert response.status_code in [201, 400]
            else:
                # 6th should be rate limited
                assert response.status_code == 429

    def test_rate_limiting_login(self, client):
        """Test rate limiting on login endpoint."""
        # Register a user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "ratetest@example.com",
                "password": "password123",
            },
        )
        
        # Make 6 login attempts (limit is 5/minute)
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                params={
                    "email": "ratetest@example.com",
                    "password": "password123",
                },
            )
            
            if i < 5:
                # First 5 should succeed
                assert response.status_code == 200
            else:
                # 6th should be rate limited
                assert response.status_code == 429
