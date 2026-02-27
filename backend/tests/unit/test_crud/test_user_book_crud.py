"""Unit tests for User Book CRUD operations."""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.crud import user_book as crud_user_book
from app.models.user_book import UserBook
from app.schemas.user_book import UserBookCreate, UserBookUpdate


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_user_books():
    """Sample user book records."""
    return [
        UserBook(
            id=1,
            user_id=1,
            book_id=1,
            is_favorite=True,
            reading_status="reading",
            personal_rating=5,
            notes="Great book!",
        ),
        UserBook(
            id=2,
            user_id=1,
            book_id=2,
            is_favorite=False,
            reading_status="to_read",
            personal_rating=None,
            notes=None,
        ),
        UserBook(
            id=3,
            user_id=1,
            book_id=3,
            is_favorite=False,
            reading_status="finished",
            personal_rating=4,
            notes="Good read",
        ),
    ]


@pytest.mark.unit
class TestUserBookCRUD:
    """Test user book CRUD operations."""

    def test_get_user_books_all(self, mock_db, sample_user_books):
        """Test getting all user books."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_user_books
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_books(mock_db, user_id=1)
        
        assert len(result) == 3
        assert result == sample_user_books

    def test_get_user_books_favorite_only(self, mock_db, sample_user_books):
        """Test filtering by favorite only."""
        favorites = [b for b in sample_user_books if b.is_favorite]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = favorites
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_books(
            mock_db, user_id=1, favorite_only=True
        )
        
        assert len(result) == 1
        assert result[0].is_favorite == True

    def test_get_user_books_by_status(self, mock_db, sample_user_books):
        """Test filtering by reading status."""
        reading = [b for b in sample_user_books if b.reading_status == "reading"]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = reading
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_books(
            mock_db, user_id=1, reading_status="reading"
        )
        
        assert len(result) == 1
        assert result[0].reading_status == "reading"

    def test_get_user_books_pagination(self, mock_db, sample_user_books):
        """Test pagination."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_user_books[:2]
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_books(
            mock_db, user_id=1, skip=0, limit=2
        )
        
        assert len(result) == 2

    def test_get_user_book(self, mock_db, sample_user_books):
        """Test getting specific user book."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_user_books[0]
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_book(mock_db, user_id=1, book_id=1)
        
        assert result == sample_user_books[0]
        assert result.book_id == 1

    def test_get_user_book_not_found(self, mock_db):
        """Test getting non-existent user book."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_book(mock_db, user_id=1, book_id=999)
        
        assert result is None

    def test_get_user_book_by_id(self, mock_db, sample_user_books):
        """Test getting user book by ID with ownership check."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_user_books[0]
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.get_user_book_by_id(
            mock_db, user_book_id=1, user_id=1
        )
        
        assert result == sample_user_books[0]
        assert result.id == 1

    def test_add_to_library_new(self, mock_db):
        """Test adding new book to library."""
        # Mock that book doesn't exist yet
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_db.query.return_value = mock_query
        
        new_user_book = UserBook(id=1, user_id=1, book_id=1)
        
        # Mock the add/commit/refresh cycle
        def refresh_side_effect(obj):
            obj.id = 1
        
        mock_db.refresh.side_effect = refresh_side_effect
        
        # Patch UserBook constructor to return our mock
        with patch('app.crud.user_book.UserBook', return_value=new_user_book):
            result = crud_user_book.add_to_library(mock_db, user_id=1, book_id=1)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.user_id == 1
        assert result.book_id == 1

    def test_add_to_library_existing(self, mock_db, sample_user_books):
        """Test adding book that already exists returns existing."""
        existing_book = sample_user_books[0]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_book
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.add_to_library(mock_db, user_id=1, book_id=1)
        
        assert result == existing_book
        # Should not call add/commit since it already exists
        mock_db.add.assert_not_called()

    def test_update_user_book(self, mock_db, sample_user_books):
        """Test updating user book metadata."""
        existing_book = sample_user_books[0]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_book
        
        mock_db.query.return_value = mock_query
        
        update_data = UserBookUpdate(
            is_favorite=False,
            reading_status="finished",
            personal_rating=4,
            notes="Updated notes",
        )
        
        result = crud_user_book.update_user_book(
            mock_db, user_id=1, book_id=1, update_data=update_data
        )
        
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None

    def test_update_user_book_not_found(self, mock_db):
        """Test updating non-existent user book."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_db.query.return_value = mock_query
        
        update_data = UserBookUpdate(is_favorite=True)
        
        result = crud_user_book.update_user_book(
            mock_db, user_id=1, book_id=999, update_data=update_data
        )
        
        assert result is None
        mock_db.commit.assert_not_called()

    def test_update_user_book_partial(self, mock_db, sample_user_books):
        """Test partial update (only some fields)."""
        existing_book = sample_user_books[0]
        original_notes = existing_book.notes
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_book
        
        mock_db.query.return_value = mock_query
        
        # Only update favorite, leave others unchanged
        update_data = UserBookUpdate(is_favorite=False)
        
        result = crud_user_book.update_user_book(
            mock_db, user_id=1, book_id=1, update_data=update_data
        )
        
        mock_db.commit.assert_called_once()
        assert result is not None

    def test_remove_from_library_success(self, mock_db):
        """Test removing book from library."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 1  # 1 row deleted
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.remove_from_library(mock_db, user_id=1, book_id=1)
        
        assert result == True
        mock_db.commit.assert_called_once()

    def test_remove_from_library_not_found(self, mock_db):
        """Test removing non-existent book."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 0  # No rows deleted
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.remove_from_library(mock_db, user_id=1, book_id=999)
        
        assert result == False
        mock_db.commit.assert_called_once()

    def test_count_user_books(self, mock_db):
        """Test counting user books."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.count_user_books(mock_db, user_id=1)
        
        assert result == 3

    def test_count_user_books_empty(self, mock_db):
        """Test counting when library is empty."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_book.count_user_books(mock_db, user_id=1)
        
        assert result == 0
