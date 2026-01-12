from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class UserBookBase(BaseModel):
    """Base schema for user books."""
    is_favorite: bool = False
    reading_status: str = Field(default="to_read", pattern="^(to_read|reading|finished)$")
    personal_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class UserBookCreate(BaseModel):
    """Schema for adding book to library."""
    book_id: int


class UserBookUpdate(BaseModel):
    """Schema for updating library book metadata."""
    is_favorite: Optional[bool] = None
    reading_status: Optional[str] = Field(None, pattern="^(to_read|reading|finished)$")
    personal_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class UserBookInDB(UserBookBase):
    """Schema for user book in database."""
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBook(UserBookInDB):
    """Public user book schema."""
    pass


# Import here to avoid circular dependency
from app.schemas.book import Book


class UserBookWithBook(UserBookInDB):
    """User book with nested book details."""
    book: Book

    class Config:
        from_attributes = True
