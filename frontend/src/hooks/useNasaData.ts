"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { NasaDay } from "@/types";

export function useNasaData(region: string) {
  const [data, setData] = useState<NasaDay[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    api.clima.getNasaData(region)
      .then((res) => {
        if (mounted) {
          // Filtrar valores -999 de NASA POWER
          const clean = (res.data || [])
            .slice(-14)
            .filter(d => d.temperatura > -100);
          setData(clean);
        }
      })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [region]);

  const stats = {
    avgTemp: data.length ? data.reduce((a, b) => a + b.temperatura, 0) / data.length : 0,
    totalPrecip: data.reduce((a, b) => a + b.precipitacion, 0),
    avgHumidity: data.length ? data.reduce((a, b) => a + b.humedad, 0) / data.length : 0,
  };

  return { data, stats, loading };
}