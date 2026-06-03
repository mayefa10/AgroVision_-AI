"""
AgroVision AI — Settings.
Centraliza todas las variables de entorno con validación via pydantic-settings.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "AgroVision AI"
    env: str = "development"
    port: int = 8000
    log_level: str = "INFO"

    # APIs externas
    openweather_api_key: str = ""

    # Redis (cache)
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 3600

    # Modelo ML
    model_dir: str = "/app/models"

    # Datasets
    datasets_dir: str = "/app/datasets"

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def has_openweather(self) -> bool:
        return bool(self.openweather_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instancia única de settings — leída una sola vez."""
    return Settings()
