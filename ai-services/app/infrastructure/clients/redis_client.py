"""Re-export del cliente Redis desde su ubicación canónica."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from app.infrastructure.cache.redis_client import CacheClient, get_cache

__all__ = ["CacheClient", "get_cache"]
