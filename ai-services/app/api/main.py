"""AgroVision AI — Factory de la aplicación FastAPI."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    alerts_router,
    climate_router,
    dane_router,
    etl_router,
    eva_router,
    health_router,
    ml_router,
    predictions_router,
)
from app.api.routers.enso        import enso_router
from app.api.routers.openweather import openweather_router
from app.api.routers.escenarios  import escenarios_router
from app.config.logging_config import setup_logging
from app.config.settings import get_settings
from app.infrastructure.cache.redis_client import get_cache
from app.infrastructure.persistence.postgres_client import close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y limpieza al arrancar/apagar el servidor."""
    s = get_settings()
    setup_logging(s.log_level)
    cache = get_cache()
    await cache.connect()
    yield
    await close_pool()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title="AgroVision AI",
        description="Plataforma de IA para Agricultura y Desarrollo Sostenible en Colombia",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers base ──────────────────────────────────────
    for router in [
        health_router,
        predictions_router,
        alerts_router,
        climate_router,
        eva_router,
        dane_router,
        ml_router,
        etl_router,
    ]:
        app.include_router(router)

    # ── Routers nuevos (fuera del loop — 1 vez cada uno) ─
    app.include_router(enso_router)
    app.include_router(openweather_router)
    app.include_router(escenarios_router)

    return app