"""AgroVision AI — Utilidades de fecha."""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow_iso() -> str:
    """ISO 8601 del momento actual en UTC."""
    return datetime.now(timezone.utc).isoformat()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def date_range_params(days: int) -> tuple[str, str]:
    """Retorna (start_str, end_str) en formato YYYYMMDD para APIs NASA."""
    from datetime import timedelta
    end   = datetime.utcnow()
    start = end - timedelta(days=days)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def parse_periodo(p: object) -> int:
    """Convierte etiqueta de periodo textual a entero (0=anual, 1=primer sem, 2=segundo)."""
    if p is None:
        return 0
    s = str(p).upper()
    if "PRIMER" in s or s.strip().startswith("1"):
        return 1
    if "SEGUNDO" in s or s.strip().startswith("2"):
        return 2
    return 0
