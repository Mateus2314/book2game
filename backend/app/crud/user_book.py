from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.user_book import UserBook
from app.schemas.user_book import UserBookCreate, UserBookUpdate


def get_user_books(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    favorite_only: bool = False,
    reading_status: Optional[str] = None,
) -> List[UserBook]:
    """
    Get user's library with optional filters.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        favorite_only: Filter only favorites
        reading_status: Filter by reading status (to_read, reading, finished)
    
    Returns:
        List of UserBook instances
    """
    query = db.query(UserBook).filter(UserBook.user_id == user_id)
    
    if favorite_only:
        query = query.filter(UserBook.is_favorite == True)
    
    if reading_status:
        query = query.filter(UserBook.reading_status == reading_status)
    
    return query.order_by(UserBook.created_at.desc()).offset(skip).limit(limit).all()


def get_user_book(db: Session, user_id: int, book_id: int) -> Optional[UserBook]:
    """
    Get specific book from user's library.
    
    Args:
        db: Database session
        user_id: User ID
        book_id: Book ID
    
    Returns:
        UserBook instance or None
    """
    return (
        db.query(UserBook)
        .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
        .first()
    )


def get_user_book_by_id(db: Session, user_book_id: int, user_id: int) -> Optional[UserBook]:
    """
    Get user book by ID with ownership verification.
    
    Args:
        db: Database session
        user_book_id: UserBook ID
        user_id: User ID (for ownership verification)
    
    Returns:
        UserBook instance or None
    """
    return (
        db.query(UserBook)
        .filter(UserBook.id == user_book_id, UserBook.user_id == user_id)
        .first()
    )


def add_to_library(db: Session, user_id: int, book_id: int) -> UserBook:
    """
    Add book to user's library.
    
    If book already exists in library, returns existing record.
    
    Args:
        db: Database session
        user_id: User ID
        book_id: Book ID
    
    Returns:
        UserBook instance
    """
    # Check if already exists
    existing = get_user_book(db, user_id, book_id)
    if existing:
        return existing
    
    # Create new entry
    user_book = UserBook(user_id=user_id, book_id=book_id)
    db.add(user_book)
    db.commit()
    db.refresh(user_book)
    return user_book


def update_user_book(
    db: Session,
    user_id: int,
    book_id: int,
    update_data: UserBookUpdate,
) -> Optional[UserBook]:
    """
    Update user book metadata.
    
    Args:
        db: Database session
        user_id: User ID
        book_id: Book ID
        update_data: Update data
    
    Returns:
        Updated UserBook or None if not found
    """
    user_book = get_user_book(db, user_id, book_id)
    if not user_book:
        return None
    
    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user_book, field, value)
    
    db.commit()
    db.refresh(user_book)
    return user_book


def remove_from_library(db: Session, user_id: int, book_id: int) -> bool:
    """
    Remove book from user's library.
    
    Args:
        db: Database session
        user_id: User ID
        book_id: Book ID
    
    Returns:
        True if deleted, False if not found
    """
    result = (
        db.query(UserBook)
        .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
        .delete()
    )
    db.commit()
    return result > 0


def count_user_books(db: Session, user_id: int) -> int:
    """
    Count total books in user's library.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Number of books
    """
    return db.query(UserBook).filter(UserBook.user_id == user_id).count()
