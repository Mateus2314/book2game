"""
Integration tests for user library endpoints (books and games).
"""
import respx
from httpx import Response
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.game import Game


class TestUserBookLibrary:
    """Test user book library endpoints."""

    def test_get_my_library_empty(self, client: TestClient, auth_headers: dict):
        response = client.get("/api/v1/users/me/books", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @respx.mock
    def test_add_book_to_library_from_google_success(self, client: TestClient, auth_headers: dict):
        google_books_id = "gb-test-1"
        mock_book_data = {
            "id": google_books_id,
            "volumeInfo": {
                "title": "Test Book",
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
            f"/api/v1/users/me/books/from-google/{google_books_id}",
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["book"]["google_books_id"] == google_books_id
        assert data["book"]["title"] == "Test Book"

    @respx.mock
    def test_add_book_to_library_from_google_not_found(self, client: TestClient, auth_headers: dict):
        google_books_id = "gb-missing"

        respx.route(host="www.googleapis.com", path=f"/books/v1/volumes/{google_books_id}").mock(
            return_value=Response(404, json={"error": {"code": 404}})
        )

        response = client.post(
            f"/api/v1/users/me/books/from-google/{google_books_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_add_book_to_library_by_id(self, client: TestClient, auth_headers: dict, db: Session):
        book = Book(
            google_books_id="gb-local-1",
            title="Local Book",
            authors="Local Author",
            categories="Fantasy",
            language="en",
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        response = client.post(
            f"/api/v1/users/me/books/{book.id}",
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["book"]["id"] == book.id

    def test_add_book_to_library_by_id_not_found(self, client: TestClient, auth_headers: dict):
        response = client.post(
            "/api/v1/users/me/books/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_library_book(self, client: TestClient, auth_headers: dict, db: Session):
        book = Book(
            google_books_id="gb-local-2",
            title="Local Book 2",
            authors="Local Author",
            categories="Fantasy",
            language="en",
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        add_response = client.post(
            f"/api/v1/users/me/books/{book.id}",
            headers=auth_headers,
        )
        assert add_response.status_code == 201

        response = client.put(
            f"/api/v1/users/me/books/{book.id}",
            headers=auth_headers,
            json={
                "is_favorite": True,
                "reading_status": "reading",
                "personal_rating": 5,
                "notes": "Great book",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is True
        assert data["reading_status"] == "reading"
        assert data["personal_rating"] == 5
        assert data["notes"] == "Great book"

    def test_remove_book_from_library(self, client: TestClient, auth_headers: dict, db: Session):
        book = Book(
            google_books_id="gb-local-3",
            title="Local Book 3",
            authors="Local Author",
            categories="Fantasy",
            language="en",
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        add_response = client.post(
            f"/api/v1/users/me/books/{book.id}",
            headers=auth_headers,
        )
        assert add_response.status_code == 201

        response = client.delete(
            f"/api/v1/users/me/books/{book.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_update_library_book_not_found(self, client: TestClient, auth_headers: dict):
        response = client.put(
            "/api/v1/users/me/books/99999",
            headers=auth_headers,
            json={"reading_status": "reading"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_book_from_library_not_found(self, client: TestClient, auth_headers: dict):
        response = client.delete(
            "/api/v1/users/me/books/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_my_library_invalid_reading_status(self, client: TestClient, auth_headers: dict):
        response = client.get(
            "/api/v1/users/me/books?reading_status=invalid",
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_get_my_library_invalid_limit(self, client: TestClient, auth_headers: dict):
        response = client.get(
            "/api/v1/users/me/books?limit=0",
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestUserGameLibrary:
    """Test user game library endpoints."""

    def test_get_my_game_library_empty(self, client: TestClient, auth_headers: dict):
        response = client.get("/api/v1/users/me/games", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_add_game_to_library_not_found(self, client: TestClient, auth_headers: dict):
        response = client.post("/api/v1/users/me/games/99999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_add_game_to_library_success(self, client: TestClient, auth_headers: dict, db: Session):
        game = Game(
            rawg_id=1001,
            name="Local Game",
            slug="local-game",
            rating=4.0,
            genres="Action",
            tags="action",
        )
        db.add(game)
        db.commit()
        db.refresh(game)

        response = client.post(
            f"/api/v1/users/me/games/{game.id}",
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["game"]["id"] == game.id

    def test_update_library_game(self, client: TestClient, auth_headers: dict, db: Session):
        game = Game(
            rawg_id=1002,
            name="Local Game 2",
            slug="local-game-2",
            rating=4.2,
            genres="RPG",
            tags="rpg",
        )
        db.add(game)
        db.commit()
        db.refresh(game)

        add_response = client.post(
            f"/api/v1/users/me/games/{game.id}",
            headers=auth_headers,
        )
        assert add_response.status_code == 201

        response = client.put(
            f"/api/v1/users/me/games/{game.id}",
            headers=auth_headers,
            json={
                "is_favorite": True,
                "play_status": "playing",
                "personal_rating": 4,
                "notes": "Great game",
                "hours_played": 12,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is True
        assert data["play_status"] == "playing"
        assert data["personal_rating"] == 4
        assert data["notes"] == "Great game"
        assert data["hours_played"] == 12

    def test_remove_game_from_library(self, client: TestClient, auth_headers: dict, db: Session):
        game = Game(
            rawg_id=1003,
            name="Local Game 3",
            slug="local-game-3",
            rating=3.5,
            genres="Adventure",
            tags="adventure",
        )
        db.add(game)
        db.commit()
        db.refresh(game)

        add_response = client.post(
            f"/api/v1/users/me/games/{game.id}",
            headers=auth_headers,
        )
        assert add_response.status_code == 201

        response = client.delete(
            f"/api/v1/users/me/games/{game.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_update_library_game_not_found(self, client: TestClient, auth_headers: dict):
        response = client.put(
            "/api/v1/users/me/games/99999",
            headers=auth_headers,
            json={"play_status": "playing"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_game_from_library_not_found(self, client: TestClient, auth_headers: dict):
        response = client.delete(
            "/api/v1/users/me/games/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_my_game_library_invalid_play_status(self, client: TestClient, auth_headers: dict):
        response = client.get(
            "/api/v1/users/me/games?play_status=invalid",
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_get_my_game_library_invalid_limit(self, client: TestClient, auth_headers: dict):
        response = client.get(
            "/api/v1/users/me/games?limit=0",
            headers=auth_headers,
        )

        assert response.status_code == 422
