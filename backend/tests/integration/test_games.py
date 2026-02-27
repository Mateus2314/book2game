"""
Integration tests for games endpoints.

Tests cover:
- Game search in local database
- Getting game details
- Creating games manually
- Searching games by tags
- Authentication requirements
- Error handling
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.game import Game


@pytest.mark.integration
class TestGameSearch:
    """Test game search endpoint."""

    def test_search_games_empty_database(
        self, client: TestClient, auth_headers: dict
    ):
        """Test searching games when database is empty."""
        response = client.get(
            "/api/v1/games/search?query=adventure",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 0
        assert data["results"] == []
        assert data["query"] == "adventure"

    def test_search_games_with_results(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test searching games with existing games in database."""
        # Create test games
        game1 = Game(
            rawg_id=1,
            name="Adventure Game",
            slug="adventure-game",
            rating=4.5,
            released="2023-01-01",
            image_url="https://example.com/game1.jpg",
            genres="Adventure, RPG",
            tags="fantasy, exploration"
        )
        game2 = Game(
            rawg_id=2,
            name="Another Adventure",
            slug="another-adventure",
            rating=4.0,
            released="2023-06-01",
            image_url="https://example.com/game2.jpg",
            genres="Adventure",
            tags="action, quest"
        )
        db.add(game1)
        db.add(game2)
        db.commit()
        
        response = client.get(
            "/api/v1/games/search?query=adventure",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] >= 2
        assert len(data["results"]) >= 2

    def test_search_games_with_pagination(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test game search with pagination parameters."""
        # Create multiple test games
        for i in range(15):
            game = Game(
                rawg_id=100 + i,
                name=f"Test Game {i}",
                slug=f"test-game-{i}",
                rating=4.0,
                released="2023-01-01",
                genres="Test",
                tags="tag"
            )
            db.add(game)
        db.commit()
        
        # Get first page
        response = client.get(
            "/api/v1/games/search?query=test&page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert len(data["results"]) <= 10

    def test_search_games_empty_query(
        self, client: TestClient, auth_headers: dict
    ):
        """Test game search with empty query."""
        response = client.get(
            "/api/v1/games/search?query=",
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422

    def test_search_games_unauthenticated(self, client: TestClient):
        """Test game search without authentication."""
        response = client.get("/api/v1/games/search?query=test")
        
        assert response.status_code == 401


@pytest.mark.integration
class TestGameDetails:
    """Test game details endpoint."""

    def test_get_game_details_success(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test getting game details by internal ID."""
        # Create test game
        game = Game(
            rawg_id=200,
            name="Detailed Game",
            slug="detailed-game",
            rating=4.8,
            released="2024-01-01",
            image_url="https://example.com/detailed.jpg",
            description="A detailed game description",
            genres="RPG, Adventure",
            tags="fantasy, magic, story-rich",
            playtime=50,
            metacritic=92
        )
        db.add(game)
        db.commit()
        db.refresh(game)
        
        response = client.get(
            f"/api/v1/games/{game.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Detailed Game"
        assert data["rating"] == 4.8
        assert data["genres"] == "RPG, Adventure"
        assert data["id"] == game.id

    def test_get_game_details_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting details for non-existent game."""
        response = client.get(
            "/api/v1/games/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_game_details_unauthenticated(self, client: TestClient):
        """Test getting game details without authentication."""
        response = client.get("/api/v1/games/1")
        
        assert response.status_code == 401


@pytest.mark.integration
class TestGameSearchByTags:
    """Test game search by tags endpoint."""

    def test_search_games_by_tags_success(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test searching games by tags."""
        # Create games with specific tags
        game1 = Game(
            rawg_id=300,
            name="Fantasy Quest",
            slug="fantasy-quest",
            rating=4.5,
            released="2023-01-01",
            genres="RPG",
            tags="fantasy, magic, adventure"
        )
        game2 = Game(
            rawg_id=301,
            name="Space Explorer",
            slug="space-explorer",
            rating=4.2,
            released="2023-03-01",
            genres="Action",
            tags="sci-fi, space, adventure"
        )
        db.add(game1)
        db.add(game2)
        db.commit()
        
        response = client.get(
            "/api/v1/games/tags/fantasy,magic",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["results"], list)
        assert data["tags"] == ["fantasy", "magic"]

    def test_search_games_by_single_tag(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test searching games by single tag."""
        game = Game(
            rawg_id=400,
            name="RPG Game",
            slug="rpg-game",
            rating=4.0,
            released="2023-01-01",
            genres="RPG",
            tags="rpg, adventure"
        )
        db.add(game)
        db.commit()
        
        response = client.get(
            "/api/v1/games/tags/rpg",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tags"] == ["rpg"]

    def test_search_games_by_tags_empty(
        self, client: TestClient, auth_headers: dict
    ):
        """Test searching with empty tags."""
        response = client.get(
            "/api/v1/games/tags/,,,",
            headers=auth_headers
        )
        
        # Should return 400 Bad Request
        assert response.status_code == 400
        assert "at least one tag" in response.json()["detail"].lower()

    def test_search_games_by_too_many_tags(
        self, client: TestClient, auth_headers: dict
    ):
        """Test searching with more than 10 tags."""
        tags = ",".join([f"tag{i}" for i in range(15)])
        response = client.get(
            f"/api/v1/games/tags/{tags}",
            headers=auth_headers
        )
        
        # Should return 400 Bad Request
        assert response.status_code == 400
        assert "maximum" in response.json()["detail"].lower()

    def test_search_games_by_tags_with_pagination(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test tag search with pagination."""
        # Create multiple games with same tag
        for i in range(15):
            game = Game(
                rawg_id=500 + i,
                name=f"Tagged Game {i}",
                slug=f"tagged-game-{i}",
                rating=4.0,
                released="2023-01-01",
                genres="Action",
                tags="action, popular"
            )
            db.add(game)
        db.commit()
        
        response = client.get(
            "/api/v1/games/tags/action?page=1&page_size=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["results"]) <= 5

    def test_search_games_by_tags_unauthenticated(self, client: TestClient):
        """Test tag search without authentication."""
        response = client.get("/api/v1/games/tags/fantasy")
        
        assert response.status_code == 401


@pytest.mark.integration
class TestGameCreation:
    """Test manual game creation endpoint."""

    def test_create_game_success(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating a new game."""
        game_data = {
            "rawg_id": 12345,
            "name": "New Test Game",
            "slug": "new-test-game",
            "rating": 4.5,
            "released": "2024-01-01",
            "genres": "Action, RPG",
            "tags": "new, test"
        }
        
        response = client.post(
            "/api/v1/games/",
            headers=auth_headers,
            json=game_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "New Test Game"
        assert data["rawg_id"] == 12345
        assert "id" in data

    def test_create_game_duplicate(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test creating duplicate game returns existing one."""
        rawg_id = 99999
        
        # Create first game
        game_data = {
            "rawg_id": rawg_id,
            "name": "Original Game",
            "slug": "original-game",
            "rating": 4.0,
            "released": "2024-01-01",
            "genres": "Action",
            "tags": "tag"
        }
        
        response1 = client.post(
            "/api/v1/games/",
            headers=auth_headers,
            json=game_data
        )
        
        assert response1.status_code == 201
        game1_id = response1.json()["id"]
        
        # Try to create duplicate
        response2 = client.post(
            "/api/v1/games/",
            headers=auth_headers,
            json=game_data
        )
        
        assert response2.status_code == 201
        game2_id = response2.json()["id"]
        
        # Should return same game
        assert game1_id == game2_id

    def test_create_game_unauthenticated(self, client: TestClient):
        """Test creating game without authentication."""
        game_data = {
            "rawg_id": 88888,
            "name": "Test Game",
            "slug": "test-game",
            "rating": 4.0,
            "released": "2024-01-01",
            "genres": "Action",
            "tags": "test"
        }
        
        response = client.post("/api/v1/games/", json=game_data)
        
        assert response.status_code == 401
