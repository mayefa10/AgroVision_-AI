"""
AgroVision AI — Entry point.
Punto de entrada único: crea la app y arranca uvicorn.
Los módulos legacy (alertas.py, data_pipeline.py, etc.) se mantienen
como referencia pero toda la lógica vive en app/.
"""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import os

import uvicorn

from app.api.main import create_app

app = create_app()

if __name__ == "__main__":
    from app.config.settings import get_settings
    s = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=s.port,
        reload=not s.is_production,
        log_level=s.log_level.lower(),
    )
