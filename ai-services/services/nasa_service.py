import requests
from datetime import datetime, timedelta

# Coordenadas simples iniciales
DEPARTAMENTOS = {
    "ANTIOQUIA": {"lat": 6.2518, "lon": -75.5636},
    "CUNDINAMARCA": {"lat": 4.7110, "lon": -74.0721},
    "VALLE": {"lat": 3.4516, "lon": -76.5320},
    "BOYACA": {"lat": 5.4545, "lon": -73.3620},
}

NASA_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def get_nasa_climate(departamento: str, days: int = 30):

    departamento = departamento.upper()

    if departamento not in DEPARTAMENTOS:
        return {"error": "Departamento no soportado"}

    coords = DEPARTAMENTOS[departamento]

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")

    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M",
        "community": "AG",
        "longitude": coords["lon"],
        "latitude": coords["lat"],
        "start": start,
        "end": end,
        "format": "JSON",
    }

    response = requests.get(NASA_BASE_URL, params=params)

    data = response.json()

    climate = data["properties"]["parameter"]

    temperatures = list(climate["T2M"].values())
    precipitation = list(climate["PRECTOTCORR"].values())
    humidity = list(climate["RH2M"].values())

    result = {
        "departamento": departamento,
        "coordinates": coords,
        "days": days,
        "climate": {
            "temperature_avg": round(sum(temperatures) / len(temperatures), 2),
            "precipitation_total": round(sum(precipitation), 2),
            "humidity_avg": round(sum(humidity) / len(humidity), 2),
        },
    }

    return result