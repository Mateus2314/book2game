from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.core.database import Base


class Recommendation(Base):
    """Recommendation model linking users, books, and games."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    
    # Recommended games (JSON string of game IDs and scores)
    games = Column(Text, nullable=False)  # JSON: [{"game_id": 1, "score": 0.85}, ...]
    
    # AI-generated or manual mapping
    ai_generated = Column(String, default=True)  # True if from Hugging Face, False if fallback
    
    # Similarity score (0.0 to 1.0)
    similarity_score = Column(Float, nullable=True)
    
    # Processing metadata
    processing_time_ms = Column(Integer, nullable=True)  # Time taken to generate recommendation
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, book_id={self.book_id})>"
