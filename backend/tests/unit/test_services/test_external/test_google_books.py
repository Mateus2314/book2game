import pytest
import respx
from httpx import Response

from app.services.external.google_books import GoogleBooksService


@pytest.mark.unit
@pytest.mark.external_api
class TestGoogleBooksService:
    """Test Google Books API service with respx mocking."""

    @pytest.fixture
    def service(self):
        return GoogleBooksService()

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_books(self, service):
        """Test searching books."""
        mock_response = {
            "totalItems": 1,
            "items": [
                {
                    "id": "book123",
                    "volumeInfo": {
                        "title": "Test Book",
                        "authors": ["Test Author"],
                    },
                }
            ],
        }

        respx.get("https://www.googleapis.com/books/v1/volumes").mock(
            return_value=Response(200, json=mock_response)
        )

        result = await service.search("test query")

        assert result["totalItems"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == "book123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_book_details(self, service):
        """Test getting book details."""
        mock_response = {
            "id": "book123",
            "volumeInfo": {
                "title": "Detailed Book",
                "authors": ["Author Name"],
                "description": "Book description",
            },
        }

        respx.get("https://www.googleapis.com/books/v1/volumes/book123").mock(
            return_value=Response(200, json=mock_response)
        )

        result = await service.get_details("book123")

        assert result["id"] == "book123"
        assert result["volumeInfo"]["title"] == "Detailed Book"

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_api_error(self, service):
        """Test search with API error."""
        respx.get("https://www.googleapis.com/books/v1/volumes").mock(
            return_value=Response(500)
        )

        result = await service.search("error query")

        assert result["totalItems"] == 0
        assert result["items"] == []

    def test_parse_book_data(self, service):
        """Test parsing book data."""
        volume_data = {
            "id": "book123",
            "volumeInfo": {
                "title": "Test Book",
                "authors": ["Author 1", "Author 2"],
                "publisher": "Test Publisher",
                "publishedDate": "2023",
                "description": "Test description",
                "pageCount": 300,
                "categories": ["Fiction", "Adventure"],
                "language": "en",
                "industryIdentifiers": [
                    {"type": "ISBN_10", "identifier": "1234567890"},
                    {"type": "ISBN_13", "identifier": "1234567890123"},
                ],
                "imageLinks": {"thumbnail": "http://example.com/image.jpg"},
                "previewLink": "http://example.com/preview",
            },
        }

        parsed = service.parse_book_data(volume_data)

        assert parsed["google_books_id"] == "book123"
        assert parsed["title"] == "Test Book"
        assert parsed["authors"] == "Author 1, Author 2"
        assert parsed["isbn_10"] == "1234567890"
        assert parsed["isbn_13"] == "1234567890123"
        assert parsed["categories"] == "Fiction, Adventure"
