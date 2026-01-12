import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

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
    yield TestClient(app, raise_server_exceptions=False)
    Base.metadata.drop_all(bind=engine)


def create_test_user_and_login(client, email="testuser@example.com"):
    """Helper to create a user and get auth token."""
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Test User",
        },
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        params={
            "email": email,
            "password": "password123",
        },
    )
    
    return response.json()["access_token"]


@pytest.mark.integration
class TestBooksEndpoints:
    """Test books endpoints."""

    @patch('app.services.external.google_books_service.search')
    def test_search_books_success(self, mock_search, client):
        """Test successful book search."""
        auth_token = create_test_user_and_login(client)
        
        # Mock Google Books API response
        mock_search.return_value = {
            "totalItems": 2,
            "items": [
                {
                    "id": "book1",
                    "volumeInfo": {
                        "title": "Harry Potter",
                        "authors": ["J.K. Rowling"],
                    }
                },
                {
                    "id": "book2",
                    "volumeInfo": {
                        "title": "Harry Potter 2",
                        "authors": ["J.K. Rowling"],
                    }
                }
            ]
        }
        
        response = client.get(
            "/api/v1/books/search?query=Harry Potter&max_results=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 2
        assert len(data["items"]) == 2
        assert data["query"] == "Harry Potter"
        assert data["max_results"] == 10

    def test_search_books_unauthorized(self, client):
        """Test book search without authentication."""
        response = client.get("/api/v1/books/search?query=test")
        
        assert response.status_code == 403

    @patch('app.services.external.google_books_service.search')
    def test_search_books_empty_result(self, mock_search, client):
        """Test book search with no results."""
        auth_token = create_test_user_and_login(client, "user2@example.com")
        mock_search.return_value = {}
        
        response = client.get(
            "/api/v1/books/search?query=nonexistent",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 0
        assert data["items"] == []

    def test_search_books_invalid_params(self, client):
        """Test book search with invalid parameters."""
        auth_token = create_test_user_and_login(client, "user3@example.com")
        
        # Empty query
        response = client.get(
            "/api/v1/books/search?query=",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422
        
        # Invalid max_results (too high)
        response = client.get(
            "/api/v1/books/search?query=test&max_results=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    @patch('app.services.external.google_books_service.get_details')
    def test_get_book_details_success(self, mock_get_details, client):
        """Test getting book details by ID."""
        auth_token = create_test_user_and_login(client, "user4@example.com")
        mock_get_details.return_value = {
            "id": "book123",
            "volumeInfo": {
                "title": "Test Book",
                "authors": ["Test Author"],
                "description": "Test description",
            }
        }
        
        response = client.get(
            "/api/v1/books/book123",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "book123"

    @patch('app.services.external.google_books_service.get_details')
    def test_get_book_details_not_found(self, mock_get_details, client):
        """Test getting details for non-existent book."""
        auth_token = create_test_user_and_login(client, "user5@example.com")
        mock_get_details.return_value = None
        
        response = client.get(
            "/api/v1/books/nonexistent",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_book_success(self, client):
        """Test creating a book in database."""
        auth_token = create_test_user_and_login(client, "user6@example.com")
        
        response = client.post(
            "/api/v1/books/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "google_books_id": "test_id_123",
                "title": "Test Book",
                "authors": "Test Author",
                "description": "Test description",
                "categories": "Fiction",
                "language": "en",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["google_books_id"] == "test_id_123"
        assert data["title"] == "Test Book"
        assert "id" in data

    def test_create_book_duplicate(self, client):
        """Test creating duplicate book returns existing."""
        auth_token = create_test_user_and_login(client, "user7@example.com")
        
        book_data = {
            "google_books_id": "duplicate_id",
            "title": "Duplicate Book",
            "authors": "Author",
        }
        
        # Create first time
        response1 = client.post(
            "/api/v1/books/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=book_data
        )
        assert response1.status_code == 201
        
        # Create second time (should return existing)
        response2 = client.post(
            "/api/v1/books/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=book_data
        )
        assert response2.status_code == 201
        assert response1.json()["id"] == response2.json()["id"]
