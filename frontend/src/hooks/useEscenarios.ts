"use client";
import { useEffect, useState, useCallback } from "react";
import { AI_URL } from "@/lib/constants";

export interface EscenarioImpacto {
  produccion_estimada:   number;
  riesgo_agricola:       string;
  riesgo_sequia?:        string;
  riesgo_inundacion?:    string;
  riesgo_fitosanitario?: string;
  riesgo_incendios?:     string;
}

export interface Escenario {
  nombre:            string;
  descripcion:       string;
  icono:             string;
  color:             string;
  condiciones:       { precipitacion_cambio: number; temperatura_cambio: number };
  impactos:          EscenarioImpacto;
  cultivos_criticos: string[];
  recomendaciones:   string[];
}

export interface EscenariosData {
  success:          boolean;
  departamento:     string;
  cultivo:          string;
  oni_actual:       number;
  escenario_activo: string | null;
  escenarios: {
    el_nino: Escenario;
    la_nina: Escenario;
  };
  clima_actual:    Record<string, number>;
  prediccion_base: { rendimiento_predicho: number; nivel: string } | null;
}

function normalizar(json: Record<string, unknown>): EscenariosData {
  const enso = (json.enso ?? {}) as Record<string, unknown>;
  return {
    success:          Boolean(json.success),
    departamento:     String(json.departamento ?? ""),
    cultivo:          String(json.cultivo ?? ""),
    oni_actual:       Number(enso.oni_actual ?? 0),
    escenario_activo: (enso.escenario_activo as string | null) ?? null,
    escenarios:       (enso.escenarios as EscenariosData["escenarios"]),
    clima_actual:     (json.clima_actual as Record<string, number>) ?? {},
    prediccion_base:  (json.prediccion_base as EscenariosData["prediccion_base"]) ?? null,
  };
}

export function useEscenarios(departamento: string, cultivo: string) {
  const [data, setData]       = useState<EscenariosData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  const fetchData = useCallback(async (signal: AbortSignal) => {
    // Estados iniciales dentro de la función async — no en el cuerpo del effect
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ departamento, cultivo });
      const r = await fetch(`${AI_URL}/escenarios?${params}`, { signal });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      setData(normalizar(json));
    } catch (e: unknown) {
      if ((e as Error).name === "AbortError") return; // cancelado — ignorar
      setError((e as Error).message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, [departamento, cultivo]);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [fetchData]);

  return { data, loading, error };
}