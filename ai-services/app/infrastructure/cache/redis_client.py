"""AgroVision AI — Redis client con fallback graceful."""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False


class CacheClient:
    """
    Wrapper de Redis con fallback silencioso a no-cache.
    Si Redis no está disponible el servicio funciona igual, sin caché.
    """

    def __init__(self, url: str, ttl: int = 3600) -> None:
        self._url    = url
        self._ttl    = ttl
        self._client: Any = None

    async def connect(self) -> None:
        if not _REDIS_AVAILABLE:
            logger.warning("redis-py no instalado — caché deshabilitado")
            return
        try:
            self._client = aioredis.from_url(self._url, decode_responses=True)
            await self._client.ping()
            logger.info("Redis conectado: %s", self._url)
        except Exception as e:
            logger.warning("Redis no disponible (%s) — continuando sin caché", e)
            self._client = None

    async def get(self, key: str) -> Optional[Any]:
        if not self._client:
            return None
        try:
            val = await self._client.get(key)
            return json.loads(val) if val else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self._client:
            return
        try:
            await self._client.setex(key, ttl or self._ttl, json.dumps(value))
        except Exception as e:
            logger.debug("Error escribiendo caché: %s", e)

    async def delete(self, key: str) -> None:
        if not self._client:
            return
        try:
            await self._client.delete(key)
        except Exception:
            pass

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()


_cache: Optional[CacheClient] = None


def get_cache() -> CacheClient:
    global _cache
    if _cache is None:
        from app.config.settings import get_settings
        s = get_settings()
        _cache = CacheClient(url=s.redis_url, ttl=s.cache_ttl_seconds)
    return _cache
