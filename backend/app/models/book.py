from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.core.database import Base


class Book(Base):
    """Book model with Google Books API data."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    google_books_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=True)  # JSON string or comma-separated
    publisher = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    isbn_10 = Column(String, nullable=True)
    isbn_13 = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)
    categories = Column(String, nullable=True)  # JSON string or comma-separated
    language = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    preview_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title={self.title})>"
