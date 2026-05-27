"""Configuración de la aplicación."""
import os

class Settings:
    APP_NAME:    str = "AgroVision AI Services"
    VERSION:     str = "0.3.0"
    ENV:         str = os.getenv("ENV", "development")
    PORT:        int = int(os.getenv("PORT", 8000))
    OW_API_KEY:  str = os.getenv("OPENWEATHER_API_KEY", "")
    DATASETS_PATH: str = os.getenv("DATASETS_PATH", "/app/datasets")

settings = Settings()