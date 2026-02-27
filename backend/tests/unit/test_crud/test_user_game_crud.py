"""Unit tests for User Game CRUD operations."""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.crud import user_game as crud_user_game
from app.models.user_game import UserGame
from app.schemas.user_game import UserGameCreate, UserGameUpdate


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_user_games():
    """Sample user game records."""
    return [
        UserGame(
            id=1,
            user_id=1,
            game_id=1,
            is_favorite=True,
            play_status="playing",
            personal_rating=5,
            notes="Amazing game!",
            hours_played=42,
        ),
        UserGame(
            id=2,
            user_id=1,
            game_id=2,
            is_favorite=False,
            play_status="to_play",
            personal_rating=None,
            notes=None,
            hours_played=0,
        ),
        UserGame(
            id=3,
            user_id=1,
            game_id=3,
            is_favorite=False,
            play_status="completed",
            personal_rating=4,
            notes="Good game",
            hours_played=120,
        ),
    ]


@pytest.mark.unit
class TestUserGameCRUD:
    """Test user game CRUD operations."""

    def test_get_user_games_all(self, mock_db, sample_user_games):
        """Test getting all user games."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_user_games
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_games(mock_db, user_id=1)
        
        assert len(result) == 3
        assert result == sample_user_games

    def test_get_user_games_favorite_only(self, mock_db, sample_user_games):
        """Test filtering by favorite only."""
        favorites = [g for g in sample_user_games if g.is_favorite]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = favorites
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_games(
            mock_db, user_id=1, favorite_only=True
        )
        
        assert len(result) == 1
        assert result[0].is_favorite == True

    def test_get_user_games_by_status(self, mock_db, sample_user_games):
        """Test filtering by play status."""
        playing = [g for g in sample_user_games if g.play_status == "playing"]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = playing
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_games(
            mock_db, user_id=1, play_status="playing"
        )
        
        assert len(result) == 1
        assert result[0].play_status == "playing"

    def test_get_user_games_pagination(self, mock_db, sample_user_games):
        """Test pagination."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_user_games[:2]
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_games(
            mock_db, user_id=1, skip=0, limit=2
        )
        
        assert len(result) == 2

    def test_get_user_game(self, mock_db, sample_user_games):
        """Test getting specific user game."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_user_games[0]
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_game(mock_db, user_id=1, game_id=1)
        
        assert result == sample_user_games[0]
        assert result.game_id == 1

    def test_get_user_game_not_found(self, mock_db):
        """Test getting non-existent user game."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_game(mock_db, user_id=1, game_id=999)
        
        assert result is None

    def test_get_user_game_by_id(self, mock_db, sample_user_games):
        """Test getting user game by ID with ownership check."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_user_games[0]
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_game_by_id(
            mock_db, user_game_id=1, user_id=1
        )
        
        assert result == sample_user_games[0]
        assert result.id == 1

    def test_add_to_library_new(self, mock_db):
        """Test adding new game to library."""
        # Mock that game doesn't exist yet
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_db.query.return_value = mock_query
        
        new_user_game = UserGame(id=1, user_id=1, game_id=1)
        
        # Mock the add/commit/refresh cycle
        def refresh_side_effect(obj):
            obj.id = 1
        
        mock_db.refresh.side_effect = refresh_side_effect
        
        # Patch UserGame constructor to return our mock
        with patch('app.crud.user_game.UserGame', return_value=new_user_game):
            result = crud_user_game.add_to_library(mock_db, user_id=1, game_id=1)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.user_id == 1
        assert result.game_id == 1

    def test_add_to_library_existing(self, mock_db, sample_user_games):
        """Test adding game that already exists returns existing."""
        existing_game = sample_user_games[0]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_game
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.add_to_library(mock_db, user_id=1, game_id=1)
        
        assert result == existing_game
        # Should not call add/commit since it already exists
        mock_db.add.assert_not_called()

    def test_update_user_game(self, mock_db, sample_user_games):
        """Test updating user game metadata including hours_played."""
        existing_game = sample_user_games[0]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_game
        
        mock_db.query.return_value = mock_query
        
        update_data = UserGameUpdate(
            is_favorite=False,
            play_status="completed",
            personal_rating=4,
            notes="Updated notes",
            hours_played=100,
        )
        
        result = crud_user_game.update_user_game(
            mock_db, user_id=1, game_id=1, update_data=update_data
        )
        
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None

    def test_update_user_game_not_found(self, mock_db):
        """Test updating non-existent user game."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_db.query.return_value = mock_query
        
        update_data = UserGameUpdate(is_favorite=True)
        
        result = crud_user_game.update_user_game(
            mock_db, user_id=1, game_id=999, update_data=update_data
        )
        
        assert result is None
        mock_db.commit.assert_not_called()

    def test_update_user_game_partial(self, mock_db, sample_user_games):
        """Test partial update (only some fields)."""
        existing_game = sample_user_games[0]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_game
        
        mock_db.query.return_value = mock_query
        
        # Only update hours_played, leave others unchanged
        update_data = UserGameUpdate(hours_played=50)
        
        result = crud_user_game.update_user_game(
            mock_db, user_id=1, game_id=1, update_data=update_data
        )
        
        mock_db.commit.assert_called_once()
        assert result is not None

    def test_update_user_game_hours_played(self, mock_db, sample_user_games):
        """Test updating hours_played specifically."""
        existing_game = sample_user_games[0]
        original_hours = existing_game.hours_played
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_game
        
        mock_db.query.return_value = mock_query
        
        update_data = UserGameUpdate(hours_played=original_hours + 10)
        
        result = crud_user_game.update_user_game(
            mock_db, user_id=1, game_id=1, update_data=update_data
        )
        
        mock_db.commit.assert_called_once()
        assert result is not None

    def test_remove_from_library_success(self, mock_db):
        """Test removing game from library."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 1  # 1 row deleted
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.remove_from_library(mock_db, user_id=1, game_id=1)
        
        assert result == True
        mock_db.commit.assert_called_once()

    def test_remove_from_library_not_found(self, mock_db):
        """Test removing non-existent game."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 0  # No rows deleted
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.remove_from_library(mock_db, user_id=1, game_id=999)
        
        assert result == False
        mock_db.commit.assert_called_once()

    def test_count_user_games(self, mock_db):
        """Test counting user games."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.count_user_games(mock_db, user_id=1)
        
        assert result == 3

    def test_count_user_games_empty(self, mock_db):
        """Test counting when library is empty."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.count_user_games(mock_db, user_id=1)
        
        assert result == 0

    def test_get_user_games_completed_only(self, mock_db, sample_user_games):
        """Test filtering by completed status."""
        completed = [g for g in sample_user_games if g.play_status == "completed"]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = completed
        
        mock_db.query.return_value = mock_query
        
        result = crud_user_game.get_user_games(
            mock_db, user_id=1, play_status="completed"
        )
        
        assert len(result) == 1
        assert result[0].play_status == "completed"
        assert result[0].hours_played == 120
