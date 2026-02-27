"""
Integration tests for recommendations endpoints.

Tests cover:
- Generate recommendation (success and error path)
- List recommendations with pagination
- Get recommendation details, not found, and ownership checks
"""
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.crud import recommendation as crud_recommendation
from app.models.book import Book
from app.models.user import User
from app.services.recommendation_service import recommendation_service


@pytest.mark.integration
class TestRecommendations:
    """Test recommendations endpoints."""

    def _create_book(self, db: Session, google_books_id: str = "gb-1") -> Book:
        book = Book(
            google_books_id=google_books_id,
            title="Test Book",
            authors="Test Author",
            description="Test description",
            categories="Fantasy",
            language="en",
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def _create_other_user(db: Session) -> User:
        user = User(
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other User",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def test_generate_recommendation_success(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test generating recommendation with mocked service."""
        book = self._create_book(db)

        async def fake_generate_recommendation(db: Session, user_id: int, book_id: int):
            rec = crud_recommendation.create_recommendation(
                db=db,
                user_id=user_id,
                book_id=book_id,
                games=json.dumps([{"game_id": 1, "score": 0.9}]),
                ai_generated=True,
                similarity_score=0.9,
                processing_time_ms=123,
            )
            return {
                "recommendation": rec,
                "book_data": {
                    "title": "Test Book",
                    "google_books_id": book.google_books_id,
                },
                "games": [{"game_id": 1, "score": 0.9}],
            }

        original = recommendation_service.generate_recommendation
        recommendation_service.generate_recommendation = fake_generate_recommendation
        try:
            response = client.post(
                "/api/v1/recommendations/",
                headers=auth_headers,
                json={"book_id": book.id},
            )
        finally:
            recommendation_service.generate_recommendation = original

        assert response.status_code == 201
        data = response.json()

        assert "recommendation_id" in data
        assert data["book"]["title"] == "Test Book"
        assert isinstance(data["recommended_games"], list)
        ai_generated = data["ai_generated"]
        if isinstance(ai_generated, str):
            ai_generated = ai_generated.lower() == "true"
        assert ai_generated is True
        assert data["similarity_score"] == 0.9
        assert isinstance(data["processing_time_ms"], int)
        assert data["processing_time_ms"] >= 0

    def test_generate_recommendation_error(self, client: TestClient, auth_headers: dict):
        """Test generate recommendation error path returns 500."""
        async def fake_generate_recommendation(db: Session, user_id: int, book_id: int):
            raise ValueError("Book with ID 999 not found in database")

        original = recommendation_service.generate_recommendation
        recommendation_service.generate_recommendation = fake_generate_recommendation
        try:
            response = client.post(
                "/api/v1/recommendations/",
                headers=auth_headers,
                json={"book_id": 999},
            )
        finally:
            recommendation_service.generate_recommendation = original

        assert response.status_code == 500
        assert "failed to generate recommendation" in response.json()["detail"].lower()

    def test_list_recommendations_with_pagination(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test listing recommendations with pagination."""
        book = self._create_book(db, google_books_id="gb-2")

        crud_recommendation.create_recommendation(
            db=db,
            user_id=test_user.id,
            book_id=book.id,
            games=json.dumps([{"game_id": 10, "score": 0.8}]),
            ai_generated=True,
            similarity_score=0.8,
            processing_time_ms=50,
        )
        crud_recommendation.create_recommendation(
            db=db,
            user_id=test_user.id,
            book_id=book.id,
            games=json.dumps([{"game_id": 11, "score": 0.7}]),
            ai_generated=False,
            similarity_score=0.7,
            processing_time_ms=60,
        )

        response = client.get(
            "/api/v1/recommendations?skip=0&limit=1",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_get_recommendation_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting recommendation that does not exist."""
        response = client.get("/api/v1/recommendations/99999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_recommendation_not_owner(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test recommendation ownership enforcement."""
        book = self._create_book(db, google_books_id="gb-3")
        rec = crud_recommendation.create_recommendation(
            db=db,
            user_id=test_user.id,
            book_id=book.id,
            games=json.dumps([{"game_id": 12, "score": 0.6}]),
            ai_generated=True,
            similarity_score=0.6,
            processing_time_ms=70,
        )

        other_user = self._create_other_user(db)
        other_token = create_access_token(data={"sub": str(other_user.id)})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.get(
            f"/api/v1/recommendations/{rec.id}",
            headers=other_headers,
        )

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()
