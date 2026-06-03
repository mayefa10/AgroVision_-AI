"""Tests de integración — Pipeline EVA + alertas (end-to-end con mocks)."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from services.alert_service import evaluar_alertas, get_alertas_departamento
from app.etl.cleaners.eva_cleaner import clean_eva


# ── EVA cleaner ───────────────────────────────────────────

def test_clean_eva_elimina_rendimiento_cero(mock_eva_response):
    df = pd.DataFrame(mock_eva_response)
    df = df.rename(columns={"a_o": "anio", "rea_sembrada": "area_sembrada",
                             "producci_n": "produccion", "rea_cosechada": "area_cosechada"})
    # Agregar una fila con rendimiento 0 (debe eliminarse)
    bad_row = df.iloc[0].copy()
    bad_row["rendimiento"] = "0"
    df = pd.concat([df, pd.DataFrame([bad_row])], ignore_index=True)

    clean = clean_eva(df)
    assert (pd.to_numeric(clean["rendimiento"], errors="coerce") > 0).all()


def test_clean_eva_normaliza_texto(mock_eva_response):
    df = pd.DataFrame(mock_eva_response)
    df = df.rename(columns={"a_o": "anio", "rea_sembrada": "area_sembrada",
                             "producci_n": "produccion", "rea_cosechada": "area_cosechada"})
    df.loc[0, "departamento"] = "  antioquia  "
    clean = clean_eva(df)
    assert clean.loc[clean["departamento"].notna(), "departamento"].str.isupper().all()


# ── Alert service ─────────────────────────────────────────

def test_evaluar_alertas_sequia(sample_clima_stats):
    alertas = evaluar_alertas("ANTIOQUIA", sample_clima_stats, ["MAIZ", "PAPA"])
    tipos = [a["tipo"] for a in alertas]
    # Con humedad 35 y prec 3 y 8 días secos → debe disparar sequía
    assert "sequia" in tipos


def test_evaluar_alertas_inundacion(sample_clima_inundacion):
    alertas = evaluar_alertas("META", sample_clima_inundacion, ["ARROZ", "MAIZ"])
    tipos = [a["tipo"] for a in alertas]
    assert "inundacion" in tipos


def test_evaluar_alertas_estructura(sample_clima_stats):
    alertas = evaluar_alertas("BOYACA", sample_clima_stats, ["PAPA"])
    for alerta in alertas:
        assert "id" in alerta
        assert "tipo" in alerta
        assert "severidad" in alerta
        assert "score" in alerta
        assert alerta["activa"] is True


@pytest.mark.asyncio
async def test_get_alertas_departamento_invalido():
    result = await get_alertas_departamento("DEPARTAMENTO_INVALIDO")
    assert result["success"] is False


@pytest.mark.asyncio
async def test_get_alertas_departamento_valido(sample_clima_stats):
    nasa_response = {
        "success":      True,
        "estadisticas": sample_clima_stats,
    }
    with patch(
        "services.alert_service._nasa.fetch_daily",
        AsyncMock(return_value=nasa_response),
    ):
        result = await get_alertas_departamento("ANTIOQUIA")

    assert result["success"] is True
    assert "alertas" in result
    assert "clima_actual" in result
