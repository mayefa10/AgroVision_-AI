"""AgroVision AI — Dependencias de FastAPI (Depends)."""
# Copyright (C) 2026 July Mayerly Quintero Farfán
from __future__ import annotations

from app.config.settings import Settings, get_settings
from app.infrastructure.cache.redis_client import CacheClient, get_cache


def settings_dep() -> Settings:
    return get_settings()


def cache_dep() -> CacheClient:
    return get_cache()
