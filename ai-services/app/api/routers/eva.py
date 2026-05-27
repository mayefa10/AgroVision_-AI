from fastapi import APIRouter, Query
from typing import Optional
from app.infrastructure.clients.eva_client import eva_client

router = APIRouter(prefix="/eva", tags=["EVA"])

@router.get("/data")
async def eva_data(
    departamento: Optional[str] = Query(None, example="ANTIOQUIA"),
    cultivo:      Optional[str] = Query(None, example="MAIZ"),
    anio:         Optional[int] = Query(None, example=2023),
    limit:        int           = Query(500, le=5000),
):
    """Datos EVA con filtros. Fuente: datos.gov.co"""
    return await eva_client.fetch(departamento=departamento, cultivo=cultivo, anio=anio, limit=limit)

@router.get("/cultivos")
async def eva_cultivos(departamento: Optional[str] = Query(None)):
    result = await eva_client.fetch(departamento=departamento, limit=5000)
    if not result.get("success"):
        return result
    cultivos = list({r.get("cultivo", "") for r in result.get("data", []) if r.get("cultivo")})
    return {"success": True, "total": len(cultivos), "cultivos": sorted(cultivos)}