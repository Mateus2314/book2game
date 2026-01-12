from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.core.database import Base


class Game(Base):
    """Game model with AI-generated game data."""

    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    rawg_id = Column(Integer, unique=True, index=True, nullable=False)  # ID único do jogo (gerado pela IA)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    released = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    metacritic = Column(Integer, nullable=True)
    playtime = Column(Integer, nullable=True)  # Average playtime in hours
    genres = Column(String, nullable=True)  # JSON string or comma-separated
    tags = Column(String, nullable=True)  # JSON string or comma-separated
    platforms = Column(String, nullable=True)  # JSON string or comma-separated
    developers = Column(String, nullable=True)  # JSON string or comma-separated
    publishers = Column(String, nullable=True)  # JSON string or comma-separated
    image_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, name={self.name})>"
