import pytest
from unittest.mock import Mock, patch

from app.services.cache_service import CacheService


@pytest.mark.unit
class TestCacheService:
    """Test Redis cache service."""

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_initialization_success(self, mock_redis):
        """Test successful Redis connection."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        
        assert cache.available is True
        assert cache.redis_client == mock_client

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_initialization_failure(self, mock_redis):
        """Test Redis connection failure with graceful degradation."""
        from redis.exceptions import RedisError
        mock_redis.side_effect = RedisError("Connection failed")
        
        cache = CacheService()
        
        assert cache.available is False
        assert cache.redis_client is None

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_get_hit(self, mock_redis):
        """Test cache GET with hit."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = '{"key": "value"}'
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        result = cache.get("test_key")
        
        assert result == {"key": "value"}
        assert cache.hits == 1
        assert cache.misses == 0

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_get_miss(self, mock_redis):
        """Test cache GET with miss."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        result = cache.get("test_key")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_set(self, mock_redis):
        """Test cache SET."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        result = cache.set("test_key", {"data": "value"}, ttl=3600)
        
        assert result is True
        mock_client.setex.assert_called_once()

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_set_unavailable(self, mock_redis):
        """Test cache SET when Redis unavailable."""
        from redis.exceptions import RedisError
        mock_redis.side_effect = RedisError("Connection failed")
        
        cache = CacheService()
        result = cache.set("test_key", {"data": "value"})
        
        assert result is False

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_delete(self, mock_redis):
        """Test cache DELETE."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        result = cache.delete("test_key")
        
        assert result is True
        mock_client.delete.assert_called_once_with("test_key")

    @patch('app.services.cache_service.redis.from_url')
    def test_cache_expire(self, mock_redis):
        """Test cache EXPIRE."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        result = cache.expire("test_key", 7200)
        
        assert result is True
        mock_client.expire.assert_called_once_with("test_key", 7200)

    @patch('app.services.cache_service.redis.from_url')
    def test_hit_rate_calculation(self, mock_redis):
        """Test hit rate calculation."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        cache.hits = 8
        cache.misses = 2
        
        hit_rate = cache.get_hit_rate()
        
        assert hit_rate == 0.8

    @patch('app.services.cache_service.redis.from_url')
    def test_get_stats(self, mock_redis):
        """Test cache statistics."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = CacheService()
        cache.hits = 10
        cache.misses = 5
        
        stats = cache.get_stats()
        
        assert stats["available"] is True
        assert stats["hits"] == 10
        assert stats["misses"] == 5
        assert stats["hit_rate"] == 0.67
