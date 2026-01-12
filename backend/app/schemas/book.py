from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Base book schema."""
    google_books_id: str
    title: str
    authors: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    description: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[str] = None
    language: Optional[str] = None
    image_url: Optional[str] = None
    preview_link: Optional[str] = None


class BookCreate(BookBase):
    """Schema for creating a book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book."""
    title: Optional[str] = None
    authors: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[str] = None


class BookInDB(BookBase):
    """Schema for book in database."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Book(BookInDB):
    """Public book schema."""
    pass


class BookSearchResult(BaseModel):
    """Schema for book search results."""
    total_items: int
    items: List[Book]
