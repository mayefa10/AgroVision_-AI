"use client";
import { useEffect, useState } from "react";
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
  nombre:           string;
  descripcion:      string;
  icono:            string;
  color:            string;
  condiciones:      { precipitacion_cambio: number; temperatura_cambio: number };
  impactos:         EscenarioImpacto;
  cultivos_criticos: string[];
  recomendaciones:  string[];
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
  clima_actual:     Record<string, number>;
  prediccion_base:  { rendimiento_predicho: number; nivel: string } | null;
}

export function useEscenarios(departamento: string, cultivo: string) {
  const [data, setData]       = useState<EscenariosData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);

    const params = new URLSearchParams({ departamento, cultivo });
    fetch(`${AI_URL}/escenarios?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((json) => { if (mounted) setData(json); })
      .catch((e)   => { if (mounted) setError(e.message); })
      .finally(()  => { if (mounted) setLoading(false); });

    return () => { mounted = false; };
  }, [departamento, cultivo]);

  return { data, loading, error };
}
