import pytest
import respx
from httpx import Response
from unittest.mock import patch, MagicMock

from app.services.ai_game_generator import AIGameGenerator


@pytest.mark.unit
@pytest.mark.external_api
class TestHuggingFaceService:
    """Test Hugging Face API service for Llama 3.1 game generation."""

    @pytest.fixture
    def service(self):
        return AIGameGenerator()

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_success(self, mock_llama, service):
        """Test successful game generation via Llama."""
        mock_llama.return_value = """1. The Witcher 3: Wild Hunt (2015) - Rating: 4.8/5 - Genre: RPG - Epic fantasy
2. Skyrim (2011) - Rating: 4.7/5 - Genre: RPG - Open world adventure
3. Dragon Age (2009) - Rating: 4.5/5 - Genre: RPG - Fantasy RPG"""

        result = await service.generate_games(
            tags=["fantasy", "rpg"],
            book_title="Test Book",
            book_description="Test description",
            count=3
        )

        assert len(result) == 3
        assert result[0]["name"] == "The Witcher 3: Wild Hunt"
        assert result[0]["rating"] == 4.8
        assert result[0]["rawg_id"] is not None

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_filters_intro(self, mock_llama, service):
        """Test that intro lines are filtered."""
        mock_llama.return_value = """Here are 3 popular games:

1. Test Game (2020) - Rating: 4.5/5 - Genre: Action - Great game
2. Another Game (2021) - Rating: 4.3/5 - Genre: RPG - Fun game"""

        result = await service.generate_games(
            tags=["action"],
            book_title="Test",
            book_description="Test",
            count=2
        )

        # Should have 2 games, not include intro line
        assert len(result) == 2
        assert "Here are" not in result[0]["name"]

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_timeout(self, mock_llama, service):
        """Test handling of API timeout."""
        mock_llama.side_effect = Exception("Request timeout")

        with pytest.raises(Exception):
            await service.generate_games(
                tags=["fantasy"],
                book_title="Test",
                book_description="Test",
                count=5
            )

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_empty_response(self, mock_llama, service):
        """Test handling of empty Llama response."""
        mock_llama.return_value = ""

        with pytest.raises(ValueError, match="Llama returned empty response"):
            await service.generate_games(
                tags=["fantasy"],
                book_title="Test",
                book_description="Test",
                count=5
            )

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_markdown_cleaning(self, mock_llama, service):
        """Test that markdown is cleaned from responses."""
        mock_llama.return_value = "1. **The Last of Us** (2013) - Rating: 4.9/5 - Genre: Action - *Survival* game"

        result = await service.generate_games(
            tags=["survival"],
            book_title="Test",
            book_description="Test",
            count=1
        )

        assert len(result) == 1
        assert "**" not in result[0]["name"]
        assert "*" not in result[0]["description"]

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_validates_id_range(self, mock_llama, service):
        """Test that generated IDs are within PostgreSQL INTEGER range."""
        mock_llama.return_value = """1. Game A (2020) - Rating: 4.5/5 - Genre: Action - Test
2. Game B (2021) - Rating: 4.3/5 - Genre: RPG - Test
3. Game C (2022) - Rating: 4.7/5 - Genre: Strategy - Test"""

        result = await service.generate_games(
            tags=["action"],
            book_title="Test",
            book_description="Test",
            count=3
        )

        for game in result:
            assert game["rawg_id"] is not None
            assert 0 < game["rawg_id"] <= 2147483647  # PostgreSQL INTEGER max

    def test_unique_id_consistency(self, service):
        """Test that same name generates same ID."""
        id1 = service._generate_unique_id("Test Game")
        id2 = service._generate_unique_id("Test Game")
        id3 = service._generate_unique_id("Different Game")
        
        assert id1 == id2  # Same input = same output
        assert id1 != id3  # Different input = different output
