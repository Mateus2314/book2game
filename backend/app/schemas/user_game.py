from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class UserGameBase(BaseModel):
    """Base schema for user games."""
    is_favorite: bool = False
    play_status: str = Field(default="to_play", pattern="^(to_play|playing|completed)$")
    personal_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    hours_played: Optional[int] = Field(None, ge=0)


class UserGameCreate(BaseModel):
    """Schema for adding game to library."""
    game_id: int


class UserGameUpdate(BaseModel):
    """Schema for updating library game metadata."""
    is_favorite: Optional[bool] = None
    play_status: Optional[str] = Field(None, pattern="^(to_play|playing|completed)$")
    personal_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    hours_played: Optional[int] = Field(None, ge=0)


class UserGameInDB(UserGameBase):
    """Schema for user game in database."""
    id: int
    user_id: int
    game_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserGame(UserGameInDB):
    """Public user game schema."""
    pass


# Import here to avoid circular dependency
from app.schemas.game import Game


class UserGameWithGame(UserGameInDB):
    """User game with nested game details."""
    game: Game

    class Config:
        from_attributes = True
