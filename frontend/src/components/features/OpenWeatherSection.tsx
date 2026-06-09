"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { useOpenWeather } from "@/hooks/useOpenWeather";
import { DEPARTMENTS } from "@/lib/constants";

function toTitleCase(s: string) {
  return s.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}

const WIND_DIR = (deg: number) => {
  const dirs = ["N","NE","E","SE","S","SO","O","NO"];
  return dirs[Math.round(deg / 45) % 8] ?? "—";
};

export function OpenWeatherSection() {
  const [departamento, setDepartamento] = useState("ANTIOQUIA");
  const { data, loading, error }        = useOpenWeather(departamento);
  const c = data?.condiciones;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

      {/* Selector */}
      <Card>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.8rem", fontWeight: 500, color: "#a1a1aa", whiteSpace: "nowrap" }}>
            Departamento:
          </span>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {DEPARTMENTS.map((d) => (
              <button
                key={d}
                onClick={() => setDepartamento(d)}
                style={{
                  padding: "0.35rem 0.85rem", borderRadius: 6,
                  border:     `1px solid ${departamento === d ? "#18181b" : "#e8e5df"}`,
                  background: departamento === d ? "#18181b" : "transparent",
                  color:      departamento === d ? "#fff" : "#52525b",
                  fontSize: "0.75rem", fontFamily: "monospace",
                  fontWeight: 500, cursor: "pointer", transition: "all 0.15s",
                }}
              >
                {d.split(" ")[0]}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Tarjeta principal */}
      <Card>
        <SectionHeader
          title={`Clima actual — ${toTitleCase(departamento)}`}
          sub={`${data?.ciudad ?? "—"} · OpenWeather · Tiempo real`}
          badge="OpenWeather"
        />

        {loading && (
          <div style={{ padding: "3rem", textAlign: "center", color: "#a1a1aa" }}>
            Cargando datos OpenWeather...
          </div>
        )}

        {error && (
          <div style={{ padding: "2rem", textAlign: "center" }}>
            <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>⚠️</div>
            <div style={{ fontSize: "0.85rem", color: "#ef4444" }}>
              {error.includes("API_KEY") || error.includes("401")
                ? "OpenWeather API key no configurada. Agrega OPENWEATHER_API_KEY en .env"
                : `Error: ${error}`}
            </div>
          </div>
        )}

        {!loading && !error && c && (
          <>
            {/* Temperatura principal */}
            <div style={{ textAlign: "center", padding: "1.5rem 0 1rem" }}>
              <div style={{ fontSize: "4rem", fontWeight: 800, lineHeight: 1, color: "#18181b" }}>
                {c.temperatura.toFixed(1)}°C
              </div>
              <div style={{ fontSize: "1rem", color: "#71717a", marginTop: "0.4rem", textTransform: "capitalize" }}>
                {c.descripcion}
              </div>
              <div style={{ fontSize: "0.8rem", color: "#a1a1aa", marginTop: "0.25rem" }}>
                Sensación térmica: {c.sensacion_termica.toFixed(1)}°C
              </div>
            </div>

            {/* Grid de métricas */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
              gap: "0.75rem",
              marginTop: "0.5rem",
            }}>
              {[
                { icon: "🌡️", label: "Máx / Mín",      value: `${c.temperatura_max.toFixed(1)}° / ${c.temperatura_min.toFixed(1)}°` },
                { icon: "💧", label: "Humedad",          value: `${c.humedad}%` },
                { icon: "🌬️", label: "Viento",           value: `${c.viento_velocidad.toFixed(1)} m/s` },
                { icon: "☁️", label: "Nubosidad",        value: `${c.nubosidad}%` },
                { icon: "🔵", label: "Presión",          value: `${c.presion} hPa` },
                { icon: "👁️", label: "Visibilidad",      value: `${(c.visibilidad / 1000).toFixed(1)} km` },
              ].map((m) => (
                <div
                  key={m.label}
                  style={{
                    background: "#fafafa", border: "1px solid #f0ede8",
                    borderRadius: 10, padding: "0.85rem 1rem",
                  }}
                >
                  <div style={{ fontSize: "1.3rem", marginBottom: "0.35rem" }}>{m.icon}</div>
                  <div style={{ fontSize: "1rem", fontWeight: 700, color: "#18181b" }}>{m.value}</div>
                  <div style={{ fontSize: "0.7rem", color: "#a1a1aa", marginTop: "0.2rem" }}>{m.label}</div>
                </div>
              ))}
            </div>

            {/* Coords */}
            <div style={{ marginTop: "1rem", fontSize: "0.72rem", color: "#a1a1aa", fontFamily: "monospace", textAlign: "right" }}>
              {data?.coordenadas.lat.toFixed(4)}°N · {data?.coordenadas.lng.toFixed(4)}°W ·{" "}
              {data?.fetched_at ? new Date(data.fetched_at).toLocaleTimeString("es-CO") : ""}
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
