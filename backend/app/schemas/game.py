from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GameBase(BaseModel):
    """Base game schema."""
    rawg_id: int  # ID único do jogo (gerado pela IA)
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    released: Optional[str] = None
    rating: Optional[float] = None
    ratings_count: Optional[int] = None
    metacritic: Optional[int] = None
    playtime: Optional[int] = None
    genres: Optional[str] = None
    tags: Optional[str] = None
    platforms: Optional[str] = None
    developers: Optional[str] = None
    publishers: Optional[str] = None
    image_url: Optional[str] = None
    website: Optional[str] = None


class GameCreate(GameBase):
    """Schema for creating a game."""
    pass


class GameUpdate(BaseModel):
    """Schema for updating a game."""
    name: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    genres: Optional[str] = None
    tags: Optional[str] = None


class GameInDB(GameBase):
    """Schema for game in database."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Game(GameInDB):
    """Public game schema."""
    pass
