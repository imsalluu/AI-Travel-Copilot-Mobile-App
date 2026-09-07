import json
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MemoryCache:
    """In-memory cache fallback when Redis is not enabled or running."""
    def __init__(self):
        self._store = {}

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = value
        return True

    async def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    async def exists(self, key: str) -> bool:
        return key in self._store


class RedisService:
    def __init__(self):
        self.client = None
        self._memory_cache = MemoryCache()

    async def init_redis(self):
        if settings.REDIS_ENABLED:
            try:
                import redis.asyncio as aioredis
                self.client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.client.ping()
                logger.info("Redis connected successfully.")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis, using in-memory cache fallback: {e}")
                self.client = None
        else:
            self.client = None

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            try:
                return await self.client.get(key)
            except Exception:
                pass
        return await self._memory_cache.get(key)

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        if self.client:
            try:
                await self.client.set(key, value, ex=expire)
                return True
            except Exception:
                pass
        return await self._memory_cache.set(key, value, ex=expire)

    async def set_json(self, key: str, value: Any, expire: int = 3600) -> bool:
        return await self.set(key, json.dumps(value), expire=expire)

    async def delete(self, key: str) -> bool:
        if self.client:
            try:
                await self.client.delete(key)
                return True
            except Exception:
                pass
        return await self._memory_cache.delete(key)


redis_service = RedisService()
