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
class TestGamesEndpoints:
    """Test games endpoints."""

    def test_search_games_success(self, client):
        """Test successful game search from database."""
        auth_token = create_test_user_and_login(client)
        
        # Create test games in database
        client.post(
            "/api/v1/games/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "rawg_id": 1,
                "name": "The Witcher 3",
                "slug": "the-witcher-3",
                "description": "Test game",
                "rating": 4.5,
                "genres": "RPG"
            }
        )
        
        response = client.get(
            "/api/v1/games/search?query=Witcher&page_size=10&page=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert data["query"] == "Witcher"

    def test_search_games_unauthorized(self, client):
        """Test game search without authentication."""
        response = client.get("/api/v1/games/search?query=test")
        
        assert response.status_code == 403

    def test_search_games_empty_result(self, client):
        """Test game search with no results."""
        auth_token = create_test_user_and_login(client, "user2@example.com")
        
        response = client.get(
            "/api/v1/games/search?query=nonexistent_game_xyz123",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_search_games_invalid_params(self, client):
        """Test game search with invalid parameters."""
        auth_token = create_test_user_and_login(client, "user3@example.com")
        
        # Invalid page_size (too high)
        response = client.get(
            "/api/v1/games/search?query=test&page_size=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422
        
        # Invalid page (zero)
        response = client.get(
            "/api/v1/games/search?query=test&page=0",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    def test_get_game_details_success(self, client):
        """Test getting game details by ID from database."""
        auth_token = create_test_user_and_login(client, "user4@example.com")
        
        # Create test game
        game_response = client.post(
            "/api/v1/games/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "rawg_id": 123,
                "name": "Test Game",
                "slug": "test-game",
                "description": "Test description",
                "rating": 4.5,
                "genres": "RPG"
            }
        )
        game_id = game_response.json()["id"]
        
        response = client.get(
            f"/api/v1/games/{game_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rawg_id"] == 123
        assert data["name"] == "Test Game"

    def test_get_game_details_not_found(self, client):
        """Test getting details for non-existent game."""
        auth_token = create_test_user_and_login(client, "user5@example.com")
        
        response = client.get(
            "/api/v1/games/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_search_games_by_tags_success(self, client):
        """Test searching games by tags from database."""
        auth_token = create_test_user_and_login(client, "user6@example.com")
        
        # Create test game with tags
        client.post(
            "/api/v1/games/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "rawg_id": 1,
                "name": "Fantasy Game",
                "slug": "fantasy-game",
                "description": "Fantasy description",
                "rating": 4.5,
                "genres": "Fantasy,Magic"
            }
        )
        
        response = client.get(
            "/api/v1/games/tags/fantasy,magic?page_size=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tags"] == ["fantasy", "magic"]

    def test_search_games_by_tags_empty(self, client):
        """Test searching with empty tags."""
        auth_token = create_test_user_and_login(client, "user7@example.com")
        
        response = client.get(
            "/api/v1/games/tags/  ?page_size=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "at least one tag" in response.json()["detail"].lower()

    def test_search_games_by_tags_too_many(self, client):
        """Test searching with too many tags."""
        auth_token = create_test_user_and_login(client, "user8@example.com")
        
        tags = ",".join([f"tag{i}" for i in range(15)])
        response = client.get(
            f"/api/v1/games/tags/{tags}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "maximum 10 tags" in response.json()["detail"].lower()

    def test_create_game_success(self, client):
        """Test creating a game in database."""
        auth_token = create_test_user_and_login(client, "user9@example.com")
        
        response = client.post(
            "/api/v1/games/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "rawg_id": 12345,
                "name": "Test Game",
                "slug": "test-game",
                "description": "Test description",
                "rating": 4.5,
                "genres": "RPG,Adventure",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["rawg_id"] == 12345
        assert data["name"] == "Test Game"
        assert "id" in data

    def test_create_game_duplicate(self, client):
        """Test creating duplicate game returns existing."""
        auth_token = create_test_user_and_login(client, "user10@example.com")
        
        game_data = {
            "rawg_id": 99999,
            "name": "Duplicate Game",
            "slug": "duplicate-game",
        }
        
        # Create first time
        response1 = client.post(
            "/api/v1/games/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=game_data
        )
        assert response1.status_code == 201
        
        # Create second time (should return existing)
        response2 = client.post(
            "/api/v1/games/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=game_data
        )
        assert response2.status_code == 201
        assert response1.json()["id"] == response2.json()["id"]
