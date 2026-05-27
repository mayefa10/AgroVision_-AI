from app.infrastructure.clients.base_client import BaseClient
from app.config.constants import NASA_POWER_URL
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class NASAClient(BaseClient):
    def __init__(self):
        super().__init__(NASA_POWER_URL, timeout=60)

    async def fetch_daily(self, lat: float, lng: float, days: int = 30, departamento: str = None) -> dict:
        end   = datetime.utcnow()
        start = end - timedelta(days=days)
        params = {
            "parameters": "T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M",
            "community": "AG",
            "longitude": lng, "latitude": lat,
            "start": start.strftime("%Y%m%d"),
            "end":   end.strftime("%Y%m%d"),
            "format": "JSON",
        }
        raw = await self.get(params=params)
        if not raw:
            return {"success": False, "data": []}

        props = raw.get("properties", {}).get("parameter", {})
        dates = list(props.get("T2M", {}).keys())
        records = []
        for d in dates:
            t = props.get("T2M", {}).get(d, -999)
            p = props.get("PRECTOTCORR", {}).get(d, -999)
            h = props.get("RH2M", {}).get(d, -999)
            r = props.get("ALLSKY_SFC_SW_DWN", {}).get(d, -999)
            w = props.get("WS2M", {}).get(d, -999)
            if t > -100:
                records.append({
                    "fecha": d,
                    "temperatura":    round(t, 2),
                    "precipitacion":  round(p, 2) if p > -100 else 0,
                    "humedad":        round(h, 2) if h > -100 else 0,
                    "radiacion_solar":round(r, 2) if r > -100 else 0,
                    "viento":         round(w, 2) if w > -100 else 0,
                })

        df = pd.DataFrame(records)
        stats = {}
        if not df.empty:
            stats = {
                "temperatura_promedio": round(df["temperatura"].mean(), 2),
                "temperatura_max":      round(df["temperatura"].max(), 2),
                "temperatura_min":      round(df["temperatura"].min(), 2),
                "precipitacion_total":  round(df["precipitacion"].sum(), 2),
                "humedad_promedio":     round(df["humedad"].mean(), 2),
                "dias_sin_lluvia":      int((df["precipitacion"] < 1).sum()),
            }

        return {
            "success": True,
            "source": "NASA POWER",
            "departamento": departamento,
            "coordenadas": {"lat": lat, "lng": lng},
            "estadisticas": stats,
            "data": records,
            "fetched_at": datetime.utcnow().isoformat(),
        }

nasa_client = NASAClient()