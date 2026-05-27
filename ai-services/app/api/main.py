"""
AgroVision AI — App factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.routers import health, eva, climate

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="""
AgroVision AI Services — Plataforma agroclimática para Colombia.

**Fuentes:**
- 🌾 EVA (datos.gov.co) — Evaluaciones Agropecuarias 2019-2024
- 🛰️ NASA POWER — Datos agroclimáticos históricos
- 🌤️ OpenWeather — Clima en tiempo real
- 🗺️ DANE DIVIPOLA — Georreferenciación oficial
        """,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(eva.router)
    app.include_router(climate.router)

    return app