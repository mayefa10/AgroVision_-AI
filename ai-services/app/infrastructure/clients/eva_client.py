from app.infrastructure.clients.base_client import BaseClient
from app.config.constants import SOCRATA_BASE, EVA_2019_2024
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class EVAClient(BaseClient):
    def __init__(self):
        super().__init__(f"{SOCRATA_BASE}/{EVA_2019_2024}.json", timeout=60)

    async def fetch(self, departamento=None, cultivo=None, anio=None, limit=500) -> dict:
        where = []
        if departamento:
            where.append(f"upper(departamento)='{departamento.upper()}'")
        if cultivo:
            where.append(f"upper(cultivo)='{cultivo.upper()}'")
        if anio:
            where.append(f"a_o={anio}")

        params = {"$limit": limit, "$order": "a_o DESC"}
        if where:
            params["$where"] = " AND ".join(where)

        data = await self.get(params=params)
        if not isinstance(data, list):
            return {"success": False, "data": []}

        df = pd.DataFrame(data)
        if df.empty:
            return {"success": True, "total_registros": 0, "data": []}

        for col in ["area_sembrada", "area_cosechada", "produccion", "rendimiento"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return {
            "success": True,
            "total_registros": len(df),
            "data": df.fillna(0).to_dict(orient="records"),
        }

eva_client = EVAClient()