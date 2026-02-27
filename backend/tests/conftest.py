"""
Pytest configuration and shared fixtures for Book2Game tests.

This module provides test fixtures for:
- Database setup and teardown
- FastAPI TestClient with dependency overrides
- Test user creation and authentication
- Mock external services
"""
import os
import pytest
from typing import Generator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# CRITICAL: Set TESTING flag BEFORE importing app (to disable rate limiting)
os.environ["TESTING"] = "true"

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.main import app


# ================================
# Test Database Configuration
# ================================

# Verify testing mode is enabled
settings.TESTING = True

# Use TEST_DATABASE_URL for integration tests
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ================================
# Session-scoped Fixtures
# ================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create database schema before all tests, drop after all tests.
    Runs once per test session.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after tests complete
    Base.metadata.drop_all(bind=test_engine)


# ================================
# Function-scoped Fixtures
# ================================

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a new database session for each test.
    Automatically rolls back changes after test completes.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create FastAPI TestClient with database dependency override.
    Each test gets a fresh client with isolated database session.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Session cleanup handled by db fixture
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ================================
# User & Authentication Fixtures
# ================================

@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    """
    Create a test user in the database.
    Email: test@example.com
    Password: testpassword123
    """
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_superuser(db: Session) -> User:
    """
    Create a test superuser in the database.
    Email: admin@example.com
    Password: adminpassword123
    """
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user: User) -> str:
    """
    Create a valid JWT access token for test_user.
    Use with Authorization: Bearer {token}
    """
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture(scope="function")
def superuser_token(test_superuser: User) -> str:
    """
    Create a valid JWT access token for test_superuser.
    """
    return create_access_token(data={"sub": str(test_superuser.id)})


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> Dict[str, str]:
    """
    Return HTTP headers with Bearer token for authenticated requests.
    Usage: client.get("/endpoint", headers=auth_headers)
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def superuser_headers(superuser_token: str) -> Dict[str, str]:
    """
    Return HTTP headers with Bearer token for superuser requests.
    """
    return {"Authorization": f"Bearer {superuser_token}"}


# ================================
# Mock External Services
# ================================

@pytest.fixture
def mock_google_books_response() -> Dict[str, Any]:
    """
    Mock response from Google Books API.
    """
    return {
        "kind": "books#volumes",
        "totalItems": 1,
        "items": [
            {
                "id": "test-book-id",
                "volumeInfo": {
                    "title": "Test Book",
                    "authors": ["Test Author"],
                    "description": "A test book description",
                    "categories": ["Fiction"],
                    "publishedDate": "2023-01-01",
                    "imageLinks": {
                        "thumbnail": "https://example.com/image.jpg"
                    },
                    "pageCount": 300,
                    "language": "en"
                }
            }
        ]
    }


@pytest.fixture
def mock_huggingface_response() -> Dict[str, Any]:
    """
    Mock response from Hugging Face API for game generation.
    """
    return {
        "generated_text": "A thrilling adventure game based on the book...",
        "game_title": "Test Game",
        "game_genre": "Adventure",
        "game_mechanics": ["exploration", "puzzle-solving"],
        "estimated_playtime": "10 hours"
    }


# ================================
# Pytest Configuration
# ================================

def pytest_configure(config):
    """
    Register custom markers.
    """
    config.addinivalue_line(
        "markers", "unit: Unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require database and API)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 1 second"
    )
    config.addinivalue_line(
        "markers", "external: Tests that call external APIs (mock recommended)"
    )
