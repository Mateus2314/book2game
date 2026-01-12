# Import all models here for Alembic to detect them
from app.models.user import User
from app.models.book import Book
from app.models.game import Game
from app.models.recommendation import Recommendation

__all__ = ["User", "Book", "Game", "Recommendation"]
