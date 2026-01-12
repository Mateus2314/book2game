import json
from typing import Any, Optional

import redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()


class CacheService:
    """
    Redis cache service with TTL, hit rate tracking, and graceful fallback.
    
    Key Features:
    - TTL 24h padrão para dados de APIs externas
    - Hit rate tracking para métricas
    - Graceful degradation se Redis falhar
    - Comandos: GET (recuperar), SET (armazenar), EXPIRE (definir TTL)
    """

    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("Redis connection established successfully")
        except RedisError as e:
            logger.warning(f"Redis connection failed: {e}. Cache will be disabled.")
            self.redis_client = None
            self.available = False

        # Metrics
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/Redis unavailable
        """
        if not self.available or self.redis_client is None:
            self.misses += 1
            return None

        try:
            value = self.redis_client.get(key)
            if value is not None:
                self.hits += 1
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                self.misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            self.misses += 1
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 24h from settings)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available or self.redis_client is None:
            return False

        if ttl is None:
            ttl = settings.REDIS_CACHE_TTL

        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except (RedisError, TypeError) as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.available or self.redis_client is None:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except RedisError as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set new TTL for existing key."""
        if not self.available or self.redis_client is None:
            return False

        try:
            self.redis_client.expire(key, ttl)
            logger.debug(f"Cache EXPIRE: {key} (TTL: {ttl}s)")
            return True
        except RedisError as e:
            logger.error(f"Cache EXPIRE error for key {key}: {e}")
            return False

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(self.hits / total, 2)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "available": self.available,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.get_hit_rate(),
        }

    def clear_stats(self):
        """Reset statistics."""
        self.hits = 0
        self.misses = 0


# Singleton instance
cache_service = CacheService()
