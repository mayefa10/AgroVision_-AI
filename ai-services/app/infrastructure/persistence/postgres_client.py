"""
AgroVision AI — Cliente PostgreSQL para cache de datos externos.

Reutiliza las tablas `datasets` y `data_records` ya definidas en el
schema de Prisma (backend NestJS). FastAPI se conecta directamente
vía asyncpg — ver decisión de arquitectura: Opción A (conexión directa).

Patrón cache-aside:
  1. Buscar dataset por cache_key
  2. Si existe y no ha expirado (TTL) → devolver desde BD
  3. Si no existe o expiró → llamar a fetch_fn(), guardar, devolver
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, Optional

import asyncpg

logger = logging.getLogger(__name__)

# Misma URL que usa el backend NestJS — ambos comparten la BD `agrovision`
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/agrovision",
)

# TTL por tipo de fuente — cuánto tiempo es válido el cache antes de refrescar
TTL_HORAS: dict[str, float] = {
    "eva":         24.0,   # EVA se actualiza con poca frecuencia (mensual/anual)
    "nasa":        6.0,    # Clima histórico — refrescar cada 6h es suficiente
    "openweather": 1.0,    # Clima actual — cambia rápido, TTL corto
    "enso":        12.0,   # ONI/NOAA se actualiza mensualmente
}

DEFAULT_TTL_HORAS = 6.0

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Pool de conexiones singleton — se crea una sola vez por proceso."""
    global _pool
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=5,
                command_timeout=10,
            )
            logger.info("Pool PostgreSQL creado correctamente")
        except Exception as e:
            logger.error("No se pudo conectar a PostgreSQL: %s", e)
            raise
    return _pool


async def close_pool() -> None:
    """Cerrar el pool al apagar la aplicación (lifespan shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Pool PostgreSQL cerrado")


def _ttl_for(source: str) -> float:
    return TTL_HORAS.get(source, DEFAULT_TTL_HORAS)


async def get_cached(cache_key: str, source: str) -> Optional[dict | list]:
    """
    Busca un dataset por cache_key. Retorna el payload JSON si existe
    y no ha expirado según el TTL de la fuente. Si expiró o no existe,
    retorna None (cache miss).
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT d.id, d."fetchedAt", r.variables
                FROM datasets d
                JOIN data_records r ON r."datasetId" = d.id
                WHERE d.cachekey = $1
                ORDER BY r."createdAt" DESC
                LIMIT 1
                """,
                cache_key,
            )
    except Exception as e:
        # Si PostgreSQL no está disponible, no rompemos el flujo —
        # simplemente actuamos como si fuera cache miss.
        logger.warning("Error consultando cache PostgreSQL: %s — continuando sin cache", e)
        return None

    if row is None:
        return None

    fetched_at: datetime = row["fetchedAt"]
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)

    edad_horas = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600
    ttl = _ttl_for(source)

    if edad_horas > ttl:
        logger.debug("Cache expirado para %s (edad=%.1fh, ttl=%.1fh)", cache_key, edad_horas, ttl)
        return None

    logger.info("Cache HIT: %s (edad=%.1fh)", cache_key, edad_horas)
    variables = row["variables"]
    return json.loads(variables) if isinstance(variables, str) else variables


async def set_cached(
    cache_key: str,
    source: str,
    category: str,
    data: dict | list,
    region_id: Optional[str] = None,
) -> None:
    """
    Guarda (o actualiza) el resultado de una llamada a API externa en
    las tablas datasets/data_records. Upsert por cache_key.
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Upsert del dataset — uuid generado en SQL si es nuevo
                dataset_id = await conn.fetchval(
                    """
                    INSERT INTO datasets (id, name, source, category, cachekey, "regionId", "fetchedAt")
                    VALUES (gen_random_uuid(), $1, $2, $3::"DataCategory", $4, $5, now())
                    ON CONFLICT (cachekey)
                    DO UPDATE SET "fetchedAt" = now()
                    RETURNING id
                    """,
                    cache_key, source, category, cache_key, region_id,
                )

                # Limpiar registros viejos de este dataset antes de insertar el nuevo
                await conn.execute(
                    'DELETE FROM data_records WHERE "datasetId" = $1',
                    dataset_id,
                )
                await conn.execute(
                    """
                    INSERT INTO data_records (id, "datasetId", date, variables, "createdAt")
                    VALUES (gen_random_uuid(), $1, now(), $2::jsonb, now())
                    """,
                    dataset_id, json.dumps(data, default=str),
                )

        logger.info("Cache actualizado: %s", cache_key)
    except Exception as e:
        # Igual que en get_cached — un fallo de BD no debe tumbar la respuesta,
        # simplemente no se persiste el cache esta vez.
        logger.warning("Error guardando cache PostgreSQL: %s — continuando sin persistir", e)


async def get_or_fetch(
    cache_key: str,
    source: str,
    category: str,
    fetch_fn: Callable[[], Awaitable[dict | list]],
    region_id: Optional[str] = None,
) -> dict | list:
    """
    Patrón cache-aside completo:
      1. Intenta leer de PostgreSQL
      2. Si hay HIT → retorna directamente (sin tocar la API externa)
      3. Si hay MISS → ejecuta fetch_fn(), guarda el resultado, retorna

    Uso típico en un cliente:
        return await get_or_fetch(
            cache_key=f"eva:{departamento}:{cultivo or 'ALL'}",
            source="eva",
            category="AGRICULTURA",
            fetch_fn=lambda: self._fetch_real(departamento, cultivo),
        )
    """
    cached = await get_cached(cache_key, source)
    if cached is not None:
        return cached

    logger.info("Cache MISS: %s — llamando API externa", cache_key)
    data = await fetch_fn()

    # Solo persistimos si la respuesta fue exitosa
    if isinstance(data, dict) and data.get("success") is False:
        return data

    await set_cached(cache_key, source, category, data, region_id)
    return data