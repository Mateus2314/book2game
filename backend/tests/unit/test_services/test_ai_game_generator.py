"""Unit tests for AI Game Generator service."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.ai_game_generator import AIGameGenerator


@pytest.mark.unit
class TestAIGameGenerator:
    """Test AI Game Generator with Llama 3.1."""

    @pytest.fixture
    def service(self):
        """Create AI game generator service instance."""
        return AIGameGenerator()

    def test_generate_unique_id_consistency(self, service):
        """Test that same name generates same ID."""
        name1 = "The Witcher 3"
        name2 = "The Witcher 3"
        name3 = "Cyberpunk 2077"
        
        id1 = service._generate_unique_id(name1)
        id2 = service._generate_unique_id(name2)
        id3 = service._generate_unique_id(name3)
        
        # Same name = same ID
        assert id1 == id2
        
        # Different name = different ID
        assert id1 != id3
        
        # IDs within PostgreSQL INTEGER range
        assert 0 < id1 <= 2147483647
        assert 0 < id3 <= 2147483647

    def test_clean_markdown_bold(self, service):
        """Test cleaning bold markdown."""
        text = "**Baldur's Gate 3**"
        cleaned = service._clean_markdown(text)
        assert cleaned == "Baldur's Gate 3"

    def test_clean_markdown_italic(self, service):
        """Test cleaning italic markdown."""
        text = "*Epic Adventure*"
        cleaned = service._clean_markdown(text)
        assert cleaned == "Epic Adventure"

    def test_clean_markdown_mixed(self, service):
        """Test cleaning mixed markdown."""
        text = "**The _Last_ of Us**"
        cleaned = service._clean_markdown(text)
        assert cleaned == "The Last of Us"

    def test_clean_markdown_none(self, service):
        """Test cleaning text without markdown."""
        text = "Red Dead Redemption 2"
        cleaned = service._clean_markdown(text)
        assert cleaned == "Red Dead Redemption 2"

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_success(self, mock_llama, service):
        """Test successful game generation from Llama."""
        mock_llama.return_value = """1. The Witcher 3: Wild Hunt (2015) - Rating: 4.8/5 - Genre: RPG - Epic fantasy adventure
2. Skyrim (2011) - Rating: 4.7/5 - Genre: RPG - Open world fantasy
3. Dragon Age: Origins (2009) - Rating: 4.5/5 - Genre: RPG - Dark fantasy story
4. Mass Effect 2 (2010) - Rating: 4.6/5 - Genre: Action RPG - Space opera adventure
5. BioShock Infinite (2013) - Rating: 4.4/5 - Genre: FPS - Story-rich shooter"""
        
        tags = ["fantasy", "rpg", "open-world"]
        games = await service.generate_games(tags, "Test Book", "Test description", count=5)
        
        assert len(games) == 5
        assert games[0]["name"] == "The Witcher 3: Wild Hunt"
        assert games[0]["rating"] == 4.8
        assert games[0]["genres"] == "RPG"
        assert games[0]["rawg_id"] is not None
        assert games[0]["rawg_id"] <= 2147483647

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_filters_intro_lines(self, mock_llama, service):
        """Test that intro lines are filtered out."""
        mock_llama.return_value = """Here are 5 popular video games about fantasy:

1. The Witcher 3 (2015) - Rating: 4.8/5 - Genre: RPG - Epic adventure
2. Skyrim (2011) - Rating: 4.7/5 - Genre: RPG - Open world"""
        
        games = await service.generate_games(["fantasy"], "Test", "Test", count=2)
        
        # Should have 2 games, not 3 (intro line filtered)
        assert len(games) == 2
        assert games[0]["name"] == "The Witcher 3"
        assert "Here are" not in games[0]["name"]

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_handles_markdown(self, mock_llama, service):
        """Test that markdown is cleaned from game names."""
        mock_llama.return_value = "1. **The Last of Us** (2013) - Rating: 4.9/5 - Genre: Action - Survival horror"
        
        games = await service.generate_games(["survival"], "Test", "Test", count=1)
        
        assert len(games) == 1
        assert games[0]["name"] == "The Last of Us"
        assert "**" not in games[0]["name"]

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_validates_rawg_id(self, mock_llama, service):
        """Test that all games have valid rawg_id."""
        mock_llama.return_value = """1. Game One (2020) - Rating: 4.5/5 - Genre: Action - Great game
2. Game Two (2021) - Rating: 4.3/5 - Genre: RPG - Another game"""
        
        games = await service.generate_games(["action"], "Test", "Test", count=2)
        
        for game in games:
            assert game["rawg_id"] is not None
            assert isinstance(game["rawg_id"], int)
            assert 0 < game["rawg_id"] <= 2147483647

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_calculates_metrics(self, mock_llama, service):
        """Test that ratings_count and metacritic are calculated."""
        mock_llama.return_value = "1. Test Game (2020) - Rating: 4.5/5 - Genre: Action - Test"
        
        games = await service.generate_games(["action"], "Test", "Test", count=1)
        
        game = games[0]
        assert game["rating"] == 4.5
        assert game["ratings_count"] == int(4.5 * 50000)  # rating * 50000
        assert game["metacritic"] == int(4.5 * 20)  # rating * 20

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_sets_none_for_optional_fields(self, mock_llama, service):
        """Test that optional fields are None."""
        mock_llama.return_value = "1. Test Game (2020) - Rating: 4.5/5 - Genre: Action - Test"
        
        games = await service.generate_games(["action"], "Test", "Test", count=1)
        
        game = games[0]
        # These fields should be None (not fake data)
        assert game["platforms"] is None
        assert game["developers"] is None
        assert game["publishers"] is None
        assert game["playtime"] is None
        assert game["image_url"] is None

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_api_error(self, mock_llama, service):
        """Test handling of API errors."""
        mock_llama.side_effect = Exception("API unavailable")
        
        with pytest.raises(Exception):
            await service.generate_games(["fantasy"], "Test", "Test", count=5)

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_empty_response(self, mock_llama, service):
        """Test handling of empty Llama response."""
        mock_llama.return_value = ""
        
        with pytest.raises(ValueError, match="Llama returned empty response"):
            await service.generate_games(["fantasy"], "Test", "Test", count=5)

    @pytest.mark.asyncio
    @patch('app.services.external.huggingface_service.generate_text_with_llama')
    async def test_generate_games_invalid_format(self, mock_llama, service):
        """Test handling of invalid Llama format."""
        mock_llama.return_value = "This is not a valid game list format at all"
        
        with pytest.raises(ValueError, match="Failed to generate"):
            await service.generate_games(["fantasy"], "Test", "Test", count=5)

    def test_create_game_from_llama_data_complete(self, service):
        """Test creating game with complete data."""
        
        game = service._create_game_from_llama_data(
            name="Test Game",
            year="2020",
            rating=4.5,
            genre="RPG",
            description="A great RPG game",
            tags=["rpg", "fantasy"],
            index=0
        )
        
        assert game["name"] == "Test Game"
        assert game["released"] == "2020-01-01"
        assert game["rating"] == 4.5
        assert game["genres"] == "RPG"
        assert game["description"] == "A great RPG game"
        assert game["tags"] == "rpg, fantasy"
        assert game["rawg_id"] is not None

    def test_create_game_from_real_name_fallback(self, service):
        """Test fallback method for creating game from name only."""
        game = service._create_game_from_real_name("Fallback Game", ["action"], 0)
        
        assert game["name"] == "Fallback Game"
        assert "id" in game
        assert game["tags"] == "action"
        assert game["rating"] >= 3.5  # Min realistic rating
        assert game["rating"] <= 5.0  # Max rating
        # Year can vary (2015-2022 range), just check it exists
        assert "released" in game
        assert "20" in game["released"]  # Contains 20xx year
