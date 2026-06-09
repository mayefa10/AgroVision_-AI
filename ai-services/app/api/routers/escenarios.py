# ── Escenarios IA Router ──────────────────────────────────
import asyncio
from app.infrastructure.clients.noaa_client import noaa_client
from app.infrastructure.clients.nasa_client import NasaClient
from app.config.constants import DEPARTAMENTOS
from app.ml.inference.predictor import predict_rendimiento, model_is_trained

escenarios_router = APIRouter(prefix="/escenarios", tags=["Escenarios IA"])


@escenarios_router.get("")
async def escenarios_ia(
    departamento: str = Query("ANTIOQUIA"),
    cultivo:      str = Query("MAIZ"),
):
    """
    Escenarios predictivos IA combinando:
      - ONI actual (NOAA)
      - NASA POWER (clima reciente)
      - Modelo ML de rendimiento
    """
    

    dept_upper = departamento.upper()
    cult_upper = cultivo.upper()
    info = DEPARTAMENTOS.get(dept_upper, {"lat": 4.711, "lng": -74.072})

    # Obtener datos en paralelo
    enso_data, nasa_data = await asyncio.gather(
        noaa_client.fetch_escenarios(dept_upper, cult_upper),
        NasaClient().fetch_daily(info["lat"], info["lng"], days=30, departamento=dept_upper),
    )

    # Predicción ML base si el modelo está entrenado
    prediccion_base = None
    if model_is_trained():
        prediccion_base = predict_rendimiento(
            departamento=dept_upper,
            cultivo=cult_upper,
            grupo_cultivo="CEREALES Y LEGUMINOSAS",
            area_sembrada=100.0,
            anio=2024,
            periodo=1,
        )

    # Enriquecer escenarios con clima actual
    clima_stats = nasa_data.get("estadisticas", {}) if nasa_data.get("success") else {}

    return {
        "success":        True,
        "departamento":   dept_upper,
        "cultivo":        cult_upper,
        "clima_actual":   clima_stats,
        "enso":           enso_data,
        "prediccion_base": prediccion_base,
        "fetched_at":     __import__("app.utils.dates", fromlist=["utcnow_iso"]).utcnow_iso()
        if False else __import__("datetime").datetime.utcnow().isoformat(),
    }
