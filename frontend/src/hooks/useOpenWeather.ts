"use client";
import { useEffect, useState } from "react";
import { AI_URL } from "@/lib/constants";

export interface WeatherCondiciones {
  temperatura:       number;
  sensacion_termica: number;
  temperatura_max:   number;
  temperatura_min:   number;
  humedad:           number;
  presion:           number;
  descripcion:       string;
  nubosidad:         number;
  viento_velocidad:  number;
  visibilidad:       number;
}

export interface WeatherData {
  success:      boolean;
  ciudad:       string;
  departamento: string;
  condiciones:  WeatherCondiciones;
  coordenadas:  { lat: number; lng: number };
  fetched_at:   string;
}

export function useOpenWeather(departamento: string) {
  const [data, setData]       = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    if (!departamento) return;
    let mounted = true;
    setLoading(true);
    setError(null);

    fetch(`${AI_URL}/openweather/${encodeURIComponent(departamento)}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((json) => {
        if (!mounted) return;
        if (!json.success) throw new Error(json.message ?? "Sin datos");
        setData(json);
      })
      .catch((e) => { if (mounted) setError(e.message); })
      .finally(()  => { if (mounted) setLoading(false); });

    return () => { mounted = false; };
  }, [departamento]);

  return { data, loading, error };
}
