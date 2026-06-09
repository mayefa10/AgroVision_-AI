"use client";
import { useEffect, useState } from "react";
import { AI_URL } from "@/lib/constants";

export interface EnsoActual {
  fase:       string;
  intensidad: string;
  oni_index:  number;
  season:     string;
  anio:       number;
  color:      string;
  tendencia:  string;
}

export interface EnsoImpacto {
  precipitacion:      string;
  temperatura:        string;
  riesgo_sequia:      string;
  riesgo_inundacion:  string;
  cultivos_riesgo:    string[];
  recomendacion:      string;
  alerta:             string;
}

export interface OniRecord {
  season:     string;
  anio:       number;
  oni_index:  number;
  fase:       string;
  intensidad: string;
  color:      string;
}

export interface EnsoData {
  success:          boolean;
  estado_actual:    EnsoActual;
  probabilidades:   { el_nino: number; la_nina: number; neutro: number };
  impacto_colombia: EnsoImpacto;
  historico_oni:    OniRecord[];
}

export function useEnsoData() {
  const [data, setData]       = useState<EnsoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetch(`${AI_URL}/enso`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((json) => { if (mounted) setData(json); })
      .catch((e)   => { if (mounted) setError(e.message); })
      .finally(()  => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  return { data, loading, error };
}
