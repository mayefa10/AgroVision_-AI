"""Re-export del cliente Redis desde su ubicación canónica."""
from app.infrastructure.cache.redis_client import CacheClient, get_cache

__all__ = ["CacheClient", "get_cache"]
