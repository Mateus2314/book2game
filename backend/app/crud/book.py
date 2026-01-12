from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def get_book(db: Session, book_id: int) -> Optional[Book]:
    """Get book by ID."""
    return db.query(Book).filter(Book.id == book_id).first()


def get_book_by_google_id(db: Session, google_books_id: str) -> Optional[Book]:
    """Get book by Google Books ID."""
    return db.query(Book).filter(Book.google_books_id == google_books_id).first()


def create_book(db: Session, book_in: BookCreate) -> Book:
    """Create new book."""
    db_book = Book(**book_in.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book: Book, book_in: BookUpdate) -> Book:
    """Update book."""
    update_data = book_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(book, field, value)
    
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_or_create_book(db: Session, book_in: BookCreate) -> Book:
    """Get existing book or create new one."""
    existing_book = get_book_by_google_id(db, book_in.google_books_id)
    if existing_book:
        return existing_book
    return create_book(db, book_in)
