"use client";
import { useState, useEffect } from "react";
import { AI_URL } from "@/lib/constants";

export interface Alerta {
  id: string;
  tipo: "sequia" | "inundacion" | "helada" | "estres_termico";
  severidad: "critica" | "alta" | "media" | "baja";
  departamento: string;
  titulo: string;
  mensaje: string;
  cultivos_afectados: string[];
  variables: Record<string, number>;
  recomendacion: string;
  score: number;
  fecha: string;
  activa: boolean;
}

export function useAlertas(departamento?: string) {
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [loading, setLoading] = useState(true);
  const [resumen, setResumen] = useState({ criticas: 0, altas: 0, medias: 0 });

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    const url = departamento
      ? `${AI_URL}/alertas/${departamento}`
      : `${AI_URL}/alertas`;

    fetch(url)
      .then(r => r.json())
      .then(res => {
        if (!mounted) return;
        const data = res.alertas || [];
        setAlertas(data);
        setResumen({
          criticas: data.filter((a: Alerta) => a.severidad === "critica").length,
          altas:    data.filter((a: Alerta) => a.severidad === "alta").length,
          medias:   data.filter((a: Alerta) => a.severidad === "media").length,
        });
      })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [departamento]);

  return { alertas, loading, resumen };
}
