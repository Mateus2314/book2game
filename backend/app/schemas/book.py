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
    # Sempre expor authors e categories como array
    authors: Optional[List[str]] = None
    categories: Optional[List[str]] = None

    # Removido from_orm: use model_validate(obj, from_attributes=True) no endpoint

    @classmethod
    def _to_list(cls, v):
        if v is None or v == '':
            return []
        if isinstance(v, str):
            return [i.strip() for i in v.split(',') if i.strip()]
        if isinstance(v, list):
            return v
        return []

    from pydantic import field_validator
    @field_validator('authors', mode='before')
    def authors_validator(cls, v):
        return cls._to_list(v)

    @field_validator('categories', mode='before')
    def categories_validator(cls, v):
        return cls._to_list(v)




class BookSearchResult(BaseModel):
    """Schema for book search results."""
    total_items: int
    items: List[Book]
