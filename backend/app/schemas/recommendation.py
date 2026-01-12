from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationGame(BaseModel):
    """Schema for a game in a recommendation."""
    game_id: int
    score: float = Field(..., ge=0.0, le=1.0)


class RecommendationBase(BaseModel):
    """Base recommendation schema."""
    user_id: int
    book_id: int
    games: str  # JSON string
    ai_generated: bool = True
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_time_ms: Optional[int] = None


class RecommendationCreate(BaseModel):
    """Schema for creating a recommendation."""
    book_id: int


class RecommendationInDB(RecommendationBase):
    """Schema for recommendation in database."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Recommendation(RecommendationInDB):
    """Public recommendation schema."""
    pass


class RecommendationResponse(BaseModel):
    """Schema for recommendation response with parsed games."""
    id: int
    user_id: int
    book_id: int
    games: List[RecommendationGame]
    ai_generated: bool
    similarity_score: Optional[float]
    processing_time_ms: Optional[int]
    created_at: datetime
