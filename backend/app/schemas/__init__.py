from app.schemas.user import Token, TokenPayload, User, UserCreate, UserInDB, UserUpdate
from app.schemas.book import Book, BookCreate, BookInDB, BookSearchResult, BookUpdate
from app.schemas.game import Game, GameCreate, GameInDB, GameUpdate
from app.schemas.recommendation import (
    Recommendation,
    RecommendationCreate,
    RecommendationGame,
    RecommendationInDB,
    RecommendationResponse,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenPayload",
    # Book
    "Book",
    "BookCreate",
    "BookUpdate",
    "BookInDB",
    "BookSearchResult",
    # Game
    "Game",
    "GameCreate",
    "GameUpdate",
    "GameInDB",
    # Recommendation
    "Recommendation",
    "RecommendationCreate",
    "RecommendationInDB",
    "RecommendationResponse",
    "RecommendationGame",
]
