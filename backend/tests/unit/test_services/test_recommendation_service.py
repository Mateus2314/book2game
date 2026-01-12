"""Unit tests for Recommendation Service."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from app.services.recommendation_service import RecommendationService


@pytest.mark.unit
class TestRecommendationService:
    """Test recommendation service logic."""

    @pytest.fixture
    def service(self):
        """Create recommendation service instance."""
        return RecommendationService()

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_book_data(self):
        """Mock book data from Google Books."""
        return {
            "id": "book123",
            "volumeInfo": {
                "title": "Harry Potter and the Philosopher's Stone",
                "authors": ["J.K. Rowling"],
                "description": "A young wizard discovers his magical heritage",
                "categories": ["Fiction", "Fantasy", "Young Adult"],
                "publishedDate": "1997",
                "averageRating": 4.7
            }
        }

    def test_map_genres_to_tags_fantasy(self, service):
        """Test mapping fantasy book to game tags."""
        book_features = {
            "genres": ["Fantasy", "Fiction"],
            "title": "Harry Potter",
            "description": "Magic and wizards"
        }
        
        tags = service.map_genres_to_tags(book_features)
        
        # Verifica que tags relacionadas a fantasy foram geradas
        fantasy_related = ["fantasy", "magic", "spells", "wizards"]
        assert any(tag in tags for tag in fantasy_related), f"Expected fantasy-related tags, got {tags}"
        assert len(tags) >= 2

    def test_map_genres_to_tags_scifi(self, service):
        """Test mapping sci-fi book to game tags."""
        book_features = {
            "genres": ["Science Fiction"],
            "title": "The Martian",
            "description": "Space survival story"
        }
        
        tags = service.map_genres_to_tags(book_features)
        
        # Aceita qualquer tag relacionada a sci-fi
        scifi_related = ["sci-fi", "space", "survival", "story-rich"]
        assert any(tag in tags for tag in scifi_related), f"Expected sci-fi related tags, got {tags}"
        assert len(tags) >= 2

    def test_map_genres_to_tags_romance(self, service):
        """Test mapping romance book to game tags."""
        book_features = {
            "genres": ["Romance", "Fiction"],
            "title": "Pride and Prejudice",
            "description": "Love story"
        }
        
        tags = service.map_genres_to_tags(book_features)
        
        # Aceita qualquer tag relacionada a romance/love/story
        romance_related = ["romance", "love", "story", "story-rich", "dating-sim"]
        assert any(tag in tags for tag in romance_related), f"Expected romance related tags, got {tags}"
        assert len(tags) >= 2

    def test_map_genres_to_tags_fallback(self, service):
        """Test fallback tags for unknown genres."""
        book_features = {
            "genres": ["Unknown Genre"],
            "title": "Test Book",
            "description": "A book"
        }
        
        tags = service.map_genres_to_tags(book_features)
        
        # Should return default tags
        assert len(tags) >= 3
        assert "adventure" in tags or "story-rich" in tags

    def test_calculate_similarity_score_high(self, service):
        """Test similarity calculation with high match."""
        book_features = {
            "genres": ["Fantasy", "Adventure"],
            "themes": ["magic", "quest"]
        }
        
        game = {
            "genres": "RPG, Fantasy",
            "tags": ["fantasy", "magic", "adventure", "quest"],
            "rating": 4.8,
            "metacritic": 95
        }
        
        matched_tags = ["fantasy", "magic", "adventure"]
        score = service.calculate_similarity_score(game, book_features, matched_tags)
        
        assert score > 0.5  # High similarity
        assert score <= 1.0

    def test_calculate_similarity_score_low(self, service):
        """Test similarity calculation with low match."""
        book_features = {
            "genres": ["Romance", "Drama"],
            "themes": ["love", "relationships"]
        }
        
        game = {
            "genres": "Shooter, Action",
            "tags": ["fps", "combat", "war"],
            "rating": 4.5,
            "metacritic": 85
        }
        
        matched_tags = []  # Nenhuma tag combinou
        score = service.calculate_similarity_score(game, book_features, matched_tags)
        
        assert score < 0.6  # Low similarity (mostly from rating)

    def test_calculate_similarity_score_none_values(self, service):
        """Test similarity with None values."""
        book_features = {
            "genres": ["Fantasy"],
            "themes": []
        }
        
        game = {
            "genres": None,
            "tags": None,
            "rating": None,
            "metacritic": None
        }
        
        matched_tags = []
        # Should not crash
        score = service.calculate_similarity_score(game, book_features, matched_tags)
        assert score >= 0.0
        assert score <= 1.0

    def test_calculate_similarity_score_empty_game(self, service):
        """Test similarity with empty game data."""
        book_features = {
            "genres": ["Fantasy"],
            "themes": ["magic"]
        }
        
        game = {
            "genres": "",
            "tags": [],
            "rating": 0,
            "metacritic": 0
        }
        
        matched_tags = []
        score = service.calculate_similarity_score(game, book_features, matched_tags)
        assert score >= 0.0

    @pytest.mark.asyncio
    @patch('app.services.recommendation_service.google_books_service.get_details')
    @patch('app.services.recommendation_service.ai_game_generator.generate_games')
    async def test_generate_recommendation_success(
        self,
        mock_generate_games,
        mock_get_details,
        service,
        mock_db,
        mock_book_data
    ):
        """Test successful recommendation generation."""
        # Mock Google Books API
        mock_get_details.return_value = mock_book_data
        
        # Mock AI game generation
        mock_generate_games.return_value = [
            {
                "id": 1,
                "rawg_id": 123456,
                "name": "Hogwarts Legacy",
                "rating": 4.5,
                "genres": "RPG, Fantasy",
                "tags": "fantasy,magic,adventure",
                "description": "A magical adventure",
                "released": "2023-01-01"
            },
            {
                "id": 2,
                "rawg_id": 789012,
                "name": "The Witcher 3",
                "rating": 4.8,
                "genres": "RPG, Fantasy",
                "tags": "fantasy,rpg,open-world",
                "description": "Epic fantasy RPG",
                "released": "2015-05-01"
            }
        ]
        
        # Mock database operations
        mock_db_book = MagicMock()
        mock_db_book.id = 1
        mock_db_book.google_books_id = "book123"
        
        # Mock CRUD operations
        with patch('app.services.recommendation_service.crud_book') as mock_crud_book, \
             patch('app.services.recommendation_service.crud_game') as mock_crud_game, \
             patch('app.services.recommendation_service.crud_recommendation') as mock_crud_rec:
            
            mock_crud_book.get.return_value = mock_db_book
            # Mock para retornar jogos diferentes a cada chamada
            mock_game_1 = MagicMock()
            mock_game_1.id = 1
            mock_game_2 = MagicMock()
            mock_game_2.id = 2
            mock_crud_game.get_or_create_game.side_effect = [mock_game_1, mock_game_2]
            mock_crud_rec.create_recommendation.return_value = MagicMock(id=1)
            
            result = await service.generate_recommendation(
                db=mock_db,
                user_id=1,
                book_id=1
            )
            
            assert result is not None
            assert "recommendation" in result
            assert "games" in result
            assert len(result["games"]) >= 1  # Pelo menos 1 jogo válido

    @pytest.mark.asyncio
    async def test_generate_recommendation_book_not_found(
        self,
        service,
        mock_db
    ):
        """Test recommendation with non-existent book."""
        with patch('app.services.recommendation_service.crud_book') as mock_crud_book:
            mock_crud_book.get.return_value = None
            
            with pytest.raises(ValueError, match="Book not found"):
                await service.generate_recommendation(
                    db=mock_db,
                    user_id=1,
                    book_id=999
                )

    @pytest.mark.asyncio
    @patch('app.services.recommendation_service.cache_service.get')
    @patch('app.services.recommendation_service.ai_game_generator.generate_games')
    @patch('app.services.recommendation_service.google_books_service.get_details')
    async def test_generate_recommendation_no_games(
        self,
        mock_get_details,
        mock_generate_games,
        mock_cache_get,
        service,
        mock_db,
        mock_book_data
    ):
        """Test recommendation when no games can be generated."""
        # Mock cache retorna None (cache miss)
        mock_cache_get.return_value = None
        
        # Mock book from database
        mock_db_book = MagicMock()
        mock_db_book.id = 1
        mock_db_book.google_books_id = "book123"
        
        # Mock Google Books API
        mock_get_details.return_value = mock_book_data
        
        # Mock AI returns empty list
        mock_generate_games.return_value = []
        
        with patch('app.services.recommendation_service.crud_book') as mock_crud_book:
            mock_crud_book.get_book.return_value = mock_db_book
            
            with pytest.raises(ValueError, match="Could not find suitable games"):
                await service.generate_recommendation(
                    db=mock_db,
                    user_id=1,
                    book_id=1
                )

    @pytest.mark.asyncio
    @patch('app.services.recommendation_service.google_books_service.get_details')
    @patch('app.services.recommendation_service.ai_game_generator.generate_games')
    async def test_generate_recommendation_filters_invalid_games(
        self,
        mock_generate_games,
        mock_get_details,
        service,
        mock_db,
        mock_book_data
    ):
        """Test that games with invalid rawg_id are filtered."""
        mock_get_details.return_value = mock_book_data
        
        # Mock games with one invalid (no rawg_id)
        mock_generate_games.return_value = [
            {
                "id": 1,
                "rawg_id": 123456,
                "name": "Valid Game",
                "rating": 4.5,
                "genres": "RPG",
                "tags": "rpg",
                "description": "Valid",
                "released": "2023-01-01"
            },
            {
                "id": 2,
                "rawg_id": None,  # Invalid
                "name": "Invalid Game",
                "rating": 4.0,
                "genres": "Action",
                "tags": "action",
                "description": "Invalid",
                "released": "2023-01-01"
            }
        ]
        
        mock_db_book = MagicMock()
        mock_db_book.id = 1
        mock_db_book.google_books_id = "book123"
        
        with patch('app.services.recommendation_service.crud_book') as mock_crud_book, \
             patch('app.services.recommendation_service.crud_game') as mock_crud_game, \
             patch('app.services.recommendation_service.crud_recommendation') as mock_crud_rec:
            
            mock_crud_book.get.return_value = mock_db_book
            mock_crud_game.get_or_create_game.return_value = MagicMock()
            mock_crud_rec.create_recommendation.return_value = MagicMock(id=1)
            
            result = await service.generate_recommendation(
                db=mock_db,
                user_id=1,
                book_id=1
            )
            
            # Should only have 1 valid game
            assert len(result["games"]) == 1
            assert result["games"][0]["game_id"] == 1
