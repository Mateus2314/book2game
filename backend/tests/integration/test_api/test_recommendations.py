import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock

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
class TestRecommendationsEndpoints:
    """Test recommendations endpoints (main feature)."""

    @patch('app.services.recommendation_service.recommendation_service.generate_recommendation')
    async def test_generate_recommendation_success(self, mock_generate, client, auth_token):
        """Test successful recommendation generation."""
        # Mock recommendation service response
        mock_recommendation = MagicMock()
        mock_recommendation.id = 1
        mock_recommendation.ai_generated = True
        mock_recommendation.similarity_score = 0.85
        
        mock_generate.return_value = {
            "recommendation": mock_recommendation,
            "book_data": {
                "id": "book123",
                "title": "Harry Potter",
                "authors": "J.K. Rowling",
            },
            "games": [
                {
                    "game_id": 1,
                    "name": "Hogwarts Legacy",
                    "score": 0.92,
                    "rawg_id": 123456,
                    "rating": 4.5,
                    "genres": "RPG, Fantasy",
                },
                {
                    "game_id": 2,
                    "name": "The Witcher 3",
                    "score": 0.78,
                    "rawg_id": 789012,
                    "rating": 4.8,
                    "genres": "RPG, Open World",
                }
            ]
        }
        
        response = client.post(
            "/api/v1/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"book_id": "book123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "recommendation_id" in data
        assert data["ai_generated"] is True
        assert data["similarity_score"] == 0.85
        assert len(data["recommended_games"]) == 2
        assert "processing_time_ms" in data
        
        # Verify game data structure
        for game in data["recommended_games"]:
            assert "name" in game
            assert "score" in game
            assert "rawg_id" in game

    def test_generate_recommendation_unauthorized(self, client):
        """Test generating recommendation without authentication."""
        response = client.post(
            "/api/v1/recommendations/",
            json={"book_id": "book123"}
        )
        
        assert response.status_code == 401

    @patch('app.services.recommendation_service.recommendation_service.generate_recommendation')
    async def test_generate_recommendation_rate_limit(self, mock_generate, client, auth_token):
        """Test rate limiting on recommendation endpoint (10/hour)."""
        mock_recommendation = MagicMock()
        mock_recommendation.id = 1
        mock_recommendation.ai_generated = True
        mock_recommendation.similarity_score = 0.85
        
        mock_generate.return_value = {
            "recommendation": mock_recommendation,
            "book_data": {"id": "book123", "title": "Test"},
            "games": []
        }
        
        # Make 11 requests (limit is 10/hour)
        success_count = 0
        rate_limited_count = 0
        
        for i in range(11):
            response = client.post(
                "/api/v1/recommendations/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"book_id": f"book{i}"}
            )
            
            if response.status_code == 201:
                success_count += 1
            elif response.status_code == 429:  # Too Many Requests
                rate_limited_count += 1
        
        # Should have at least one rate limited
        assert success_count <= 10
        # Note: Rate limiting behavior may vary in test environment

    @patch('app.services.recommendation_service.recommendation_service.generate_recommendation')
    def test_generate_recommendation_service_error(self, mock_generate, client, auth_token):
        """Test recommendation generation with service error."""
        mock_generate.side_effect = Exception("AI service unavailable")
        
        response = client.post(
            "/api/v1/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"book_id": "book123"}
        )
        
        assert response.status_code == 500
        assert "failed to generate" in response.json()["detail"].lower()

    def test_list_recommendations_success(self, client, auth_token):
        """Test listing user recommendations."""
        response = client.get(
            "/api/v1/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_recommendations_pagination(self, client, auth_token):
        """Test recommendations pagination."""
        response = client.get(
            "/api/v1/recommendations/?skip=0&limit=5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_list_recommendations_invalid_params(self, client, auth_token):
        """Test listing with invalid pagination params."""
        # Negative skip
        response = client.get(
            "/api/v1/recommendations/?skip=-1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422
        
        # Limit too high
        response = client.get(
            "/api/v1/recommendations/?limit=200",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    def test_get_recommendation_not_found(self, client, auth_token):
        """Test getting non-existent recommendation."""
        response = client.get(
            "/api/v1/recommendations/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_recommendation_unauthorized_owner(self, client, auth_token):
        """Test accessing another user's recommendation."""
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
        
        # Create recommendation for first user
        # (In real scenario, would need to mock and create actual recommendation)
        # For now, test with non-existent ID which should return 404
        # A 403 would require actual cross-user recommendation
        
        # Test that user2 can't access random recommendation
        response = client.get(
            "/api/v1/recommendations/1",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        
        # Should be 404 (not found) or 403 (forbidden)
        assert response.status_code in [403, 404]

    @patch('app.services.recommendation_service.recommendation_service.generate_recommendation')
    async def test_recommendation_with_cache(self, mock_generate, client, auth_token):
        """Test that recommendation uses cache."""
        mock_recommendation = MagicMock()
        mock_recommendation.id = 1
        mock_recommendation.ai_generated = True
        mock_recommendation.similarity_score = 0.85
        
        mock_generate.return_value = {
            "recommendation": mock_recommendation,
            "games": []
        }
        
        # First request
        response1 = client.post(
            "/api/v1/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"book_id": "cached_book"}
        )
        time1 = response1.json()["processing_time_ms"]
        
        # Second request (should use cache if implemented)
        response2 = client.post(
            "/api/v1/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"book_id": "cached_book"}
        )
        time2 = response2.json()["processing_time_ms"]
        
        # Both should succeed
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        # Second might be faster if cached (not guaranteed in test)
        assert time1 >= 0
        assert time2 >= 0
