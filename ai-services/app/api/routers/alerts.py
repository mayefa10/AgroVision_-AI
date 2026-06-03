"""AgroVision AI — Router alertas."""
from __future__ import annotations

from fastapi import APIRouter

from services.alert_service import get_alertas_departamento, get_alertas_nacional

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("")
async def alertas_nacional():
    """Genera alertas para todos los departamentos monitoreados."""
    return await get_alertas_nacional()


@router.get("/{departamento}")
async def alertas_departamento(departamento: str):
    """Genera alertas para un departamento específico."""
    return await get_alertas_departamento(departamento)
