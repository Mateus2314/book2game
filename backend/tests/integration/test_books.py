"""
Integration tests for books endpoints.

Tests cover:
- Book search via Google Books API
- Getting book details
- Creating books from Google Books
- Error handling for external API failures
- Authentication requirements
"""
import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.book import Book


@pytest.mark.integration
class TestBookSearch:
    """Test book search endpoint."""

    @respx.mock
    def test_search_books_success(self, client: TestClient, auth_headers: dict):
        """Test successful book search with mocked Google Books API."""
        # Mock Google Books API response
        mock_response = {
            "kind": "books#volumes",
            "totalItems": 2,
            "items": [
                {
                    "id": "book-id-1",
                    "volumeInfo": {
                        "title": "Test Book 1",
                        "authors": ["Author One"],
                        "description": "A test book",
                        "categories": ["Fiction"],
                        "publishedDate": "2023-01-01",
                        "imageLinks": {
                            "thumbnail": "https://example.com/image1.jpg"
                        },
                        "pageCount": 300,
                        "language": "en"
                    }
                },
                {
                    "id": "book-id-2",
                    "volumeInfo": {
                        "title": "Test Book 2",
                        "authors": ["Author Two"],
                        "description": "Another test book",
                        "categories": ["Non-Fiction"],
                        "publishedDate": "2023-06-15",
                        "pageCount": 250,
                        "language": "en"
                    }
                }
            ]
        }
        
        respx.route(host="www.googleapis.com", path="/books/v1/volumes").mock(
            return_value=Response(200, json=mock_response)
        )
        
        response = client.get(
            "/api/v1/books/search?query=test&max_results=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_items"] == 2
        assert data["query"] == "test"
        assert len(data["items"]) == 2
        assert data["items"][0]["title"] == "Test Book 1"

    @respx.mock
    def test_search_books_with_pagination(self, client: TestClient, auth_headers: dict):
        """Test book search with pagination parameters."""
        mock_response = {
            "kind": "books#volumes",
            "totalItems": 100,
            "items": []
        }
        
        respx.route(host="www.googleapis.com", path="/books/v1/volumes").mock(
            return_value=Response(200, json=mock_response)
        )
        
        response = client.get(
            "/api/v1/books/search?query=python&max_results=20&start_index=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["max_results"] == 20
        assert data["start_index"] == 10

    def test_search_books_unauthenticated(self, client: TestClient):
        """Test book search without authentication."""
        response = client.get("/api/v1/books/search?query=test")
        
        assert response.status_code == 401

    def test_search_books_empty_query(self, client: TestClient, auth_headers: dict):
        """Test book search with empty query."""
        response = client.get("/api/v1/books/search?query=", headers=auth_headers)
        
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422

    @respx.mock
    def test_search_books_api_error(self, client: TestClient, auth_headers: dict):
        """Test book search when Google Books API returns error."""
        # Mock API returning 500 error
        respx.route(host="www.googleapis.com", path="/books/v1/volumes").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )
        
        # Use unique query to avoid cache hits from previous tests
        response = client.get(
            "/api/v1/books/search?query=unique_api_error_test_query_xyz",
            headers=auth_headers
        )
        
        # Should return 503 Service Unavailable
        assert response.status_code == 503
        assert "google books api error" in response.json()["detail"].lower()


@pytest.mark.integration
class TestBookDetails:
    """Test book details endpoint."""

    @respx.mock
    def test_get_book_details_success(self, client: TestClient, auth_headers: dict):
        """Test getting book details by Google Books ID."""
        book_id = "test-book-id-123"
        mock_book_data = {
            "id": book_id,
            "volumeInfo": {
                "title": "Detailed Test Book",
                "authors": ["Test Author"],
                "description": "A detailed description",
                "categories": ["Technology"],
                "publishedDate": "2023-01-01",
                "pageCount": 400,
                "language": "en",
                "imageLinks": {
                    "thumbnail": "https://example.com/image.jpg",
                    "smallThumbnail": "https://example.com/small.jpg"
                }
            }
        }
        
        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{book_id}").mock(
            return_value=Response(200, json=mock_book_data)
        )
        
        response = client.get(
            f"/api/v1/books/{book_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == book_id
        assert data["volumeInfo"]["title"] == "Detailed Test Book"

    @respx.mock
    def test_get_book_details_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting details for non-existent book."""
        book_id = "nonexistent-book-id"
        
        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{book_id}").mock(
            return_value=Response(404, json={"error": {"code": 404, "message": "Not found"}})
        )
        
        response = client.get(
            f"/api/v1/books/{book_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_book_details_unauthenticated(self, client: TestClient):
        """Test getting book details without authentication."""
        response = client.get("/api/v1/books/some-book-id")
        
        assert response.status_code == 401


@pytest.mark.integration
class TestCreateBookFromGoogle:
    """Test creating book from Google Books API."""

    @respx.mock
    def test_create_book_from_google_success(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test successfully creating a book from Google Books API."""
        google_books_id = "new-book-id"
        mock_book_data = {
            "id": google_books_id,
            "volumeInfo": {
                "title": "New Book Title",
                "authors": ["New Author"],
                "description": "Book description",
                "categories": ["Fiction"],
                "publishedDate": "2024-01-01",
                "pageCount": 350,
                "language": "en",
                "publisher": "Test Publisher",
                "imageLinks": {
                    "thumbnail": "https://example.com/thumb.jpg"
                }
            }
        }
        
        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{google_books_id}").mock(
            return_value=Response(200, json=mock_book_data)
        )
        
        response = client.post(
            f"/api/v1/books/from-google/{google_books_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "New Book Title"
        assert data["google_books_id"] == google_books_id
        assert "id" in data  # Has internal database ID

    @respx.mock
    def test_create_book_from_google_already_exists(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test creating book that already exists in database."""
        google_books_id = "existing-book"
        
        # Create book first
        from app.models.book import Book
        existing_book = Book(
            google_books_id=google_books_id,
            title="Existing Book",
            authors=["Author"],
            description="Description",
            categories=["Fiction"],
            published_date="2023-01-01",
            page_count=300,
            language="en"
        )
        db.add(existing_book)
        db.commit()
        db.refresh(existing_book)
        
        # Try to create again (should return existing)
        mock_book_data = {
            "id": google_books_id,
            "volumeInfo": {
                "title": "Different Title",
                "authors": ["Different Author"],
                "publishedDate": "2024-01-01",
                "pageCount": 400,
                "language": "en"
            }
        }
        
        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{google_books_id}").mock(
            return_value=Response(200, json=mock_book_data)
        )
        
        response = client.post(
            f"/api/v1/books/from-google/{google_books_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Should return existing book, not create new one
        assert data["id"] == existing_book.id
        assert data["title"] == "Existing Book"  # Original title

    @respx.mock
    def test_create_book_from_google_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating book with invalid Google Books ID."""
        google_books_id = "invalid-id"
        
        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{google_books_id}").mock(
            return_value=Response(404, json={"error": {"code": 404}})
        )
        
        response = client.post(
            f"/api/v1/books/from-google/{google_books_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @respx.mock
    def test_create_book_from_google_missing_title(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating book when Google Books data is missing title."""
        google_books_id = "missing-title"

        mock_book_data = {
            "id": google_books_id,
            "volumeInfo": {
                "authors": ["Test Author"],
                "description": "A test book",
                "categories": ["Fantasy"],
                "publishedDate": "2023-01-01",
                "pageCount": 123,
                "language": "en",
            },
        }

        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{google_books_id}").mock(
            return_value=Response(200, json=mock_book_data)
        )

        response = client.post(
            f"/api/v1/books/from-google/{google_books_id}",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "missing required field" in response.json()["detail"].lower()

    def test_create_book_from_google_api_error(self, client: TestClient, auth_headers: dict):
        """Test creating book when Google Books service raises an error."""
        from app.services.external import google_books_service

        google_books_id = "error-book"

        async def raise_error(book_id: str):
            raise RuntimeError("API down")

        original = google_books_service.get_details
        google_books_service.get_details = raise_error
        try:
            response = client.post(
                f"/api/v1/books/from-google/{google_books_id}",
                headers=auth_headers,
            )
        finally:
            google_books_service.get_details = original

        assert response.status_code == 503
        assert "google books api error" in response.json()["detail"].lower()

    def test_create_book_from_google_unauthenticated(self, client: TestClient):
        """Test creating book without authentication."""
        response = client.post("/api/v1/books/from-google/some-id")
        
        assert response.status_code == 401


@pytest.mark.integration
class TestManualBookCreation:
    """Test manual book creation endpoint."""

    def test_create_book_manually(self, client: TestClient, auth_headers: dict):
        """Test creating book with manual data entry."""
        book_data = {
            "google_books_id": "manual-book-123",
            "title": "Manual Book",
            "authors": "Manual Author",
            "description": "Manually entered book",
            "categories": "Technology",
            "published_date": "2024-01-01",
            "page_count": 200,
            "language": "en"
        }
        
        response = client.post(
            "/api/v1/books/",
            headers=auth_headers,
            json=book_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "Manual Book"
        assert data["google_books_id"] == "manual-book-123"
        assert "id" in data

    def test_create_book_manually_duplicate(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test creating duplicate book returns existing one."""
        google_books_id = "duplicate-manual"
        
        # Create first book
        book_data = {
            "google_books_id": google_books_id,
            "title": "Original Book",
            "authors": "Author",
            "published_date": "2024-01-01",
            "page_count": 200,
            "language": "en"
        }
        
        response1 = client.post(
            "/api/v1/books/",
            headers=auth_headers,
            json=book_data
        )
        
        assert response1.status_code == 201
        book1_id = response1.json()["id"]
        
        # Try to create duplicate
        response2 = client.post(
            "/api/v1/books/",
            headers=auth_headers,
            json=book_data
        )
        
        assert response2.status_code == 201
        book2_id = response2.json()["id"]
        
        # Should return same book
        assert book1_id == book2_id
