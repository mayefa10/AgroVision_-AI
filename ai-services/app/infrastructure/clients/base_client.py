"""AgroVision AI — Cliente HTTP base."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class BaseHttpClient:
    """
    Cliente HTTP asíncrono reutilizable.
    Todas las llamadas externas heredan de aquí para tener
    timeout, logging y manejo de errores uniformes.
    """

    def __init__(self, base_url: str = "", timeout: float = 30.0) -> None:
        self.base_url = base_url
        self.timeout  = timeout

    async def get(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Any:
        full_url = f"{self.base_url}{url}" if self.base_url else url
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(full_url, params=params, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("HTTP %s en %s: %s", e.response.status_code, full_url, e)
            raise
        except httpx.RequestError as e:
            logger.error("Error de red en %s: %s", full_url, e)
            raise

    async def get_safe(
        self,
        url: str,
        params: Optional[dict] = None,
        default: Any = None,
    ) -> Any:
        """Versión que no propaga excepciones — retorna `default` en error."""
        try:
            return await self.get(url, params=params)
        except Exception as e:
            logger.warning("get_safe falló para %s: %s", url, e)
            return default
