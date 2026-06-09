"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { useEscenarios } from "@/hooks/useEscenarios";
import { DEPARTMENTS } from "@/lib/constants";

const CULTIVOS = ["MAIZ","ARROZ","PAPA","CAFE","FRIJOL","YUCA","CACAO","SORGO","SOYA"];

function toTitleCase(s: string) {
  return s.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}

function Badge({ value, color }: { value: string; color: string }) {
  return (
    <span style={{
      background: color + "20", color, border: `1px solid ${color}40`,
      borderRadius: "100px", padding: "0.2rem 0.65rem",
      fontSize: "0.72rem", fontWeight: 700,
    }}>{value}</span>
  );
}

export function EscenariosSection() {
  const [departamento, setDepartamento] = useState("ANTIOQUIA");
  const [cultivo, setCultivo]           = useState("MAIZ");

  const { data, loading, error } = useEscenarios(departamento, cultivo);

  const escActive = data?.escenario_activo;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

      {/* ── Encabezado ── */}
      <Card>
        <SectionHeader
          title="Escenarios Predictivos IA"
          sub="NOAA ENSO · NASA POWER · Modelo ML · Datos abiertos"
          badge="IA"
        />

        {/* Filtros */}
        <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap", marginTop: "1rem" }}>
          <div>
            <label htmlFor="esc-depto" style={{ fontSize: "0.72rem", color: "#a1a1aa",
              textTransform: "uppercase", letterSpacing: "0.08em", display: "block", marginBottom: "0.4rem" }}>
              Departamento
            </label>
            <select
              id="esc-depto"
              name="esc-depto"
              aria-label="Seleccionar departamento"
              value={departamento}
              onChange={(e) => setDepartamento(e.target.value)}
              style={{
                background: "#18181b", border: "1px solid #3f3f46",
                borderRadius: 8, padding: "0.4rem 0.85rem",
                color: "#fff", fontSize: "0.82rem", cursor: "pointer",
              }}
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>{toTitleCase(d)}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="esc-cultivo" style={{ fontSize: "0.72rem", color: "#a1a1aa",
              textTransform: "uppercase", letterSpacing: "0.08em", display: "block", marginBottom: "0.4rem" }}>
              Cultivo
            </label>
            <select
              id="esc-cultivo"
              name="esc-cultivo"
              aria-label="Seleccionar cultivo"
              value={cultivo}
              onChange={(e) => setCultivo(e.target.value)}
              style={{
                background: "#18181b", border: "1px solid #3f3f46",
                borderRadius: 8, padding: "0.4rem 0.85rem",
                color: "#fff", fontSize: "0.82rem", cursor: "pointer",
              }}
            >
              {CULTIVOS.map((c) => (
                <option key={c} value={c}>{toTitleCase(c)}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {loading && (
        <Card>
          <div style={{ padding: "3rem", textAlign: "center", color: "#a1a1aa" }}>
            Generando escenarios con IA...
          </div>
        </Card>
      )}

      {error && (
        <Card>
          <div style={{ padding: "2rem", textAlign: "center", color: "#ef4444", fontSize: "0.85rem" }}>
            Error: {error}
          </div>
        </Card>
      )}

      {data && !loading && (
        <>
          {/* ── ONI actual + predicción base ── */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <Card>
              <div style={{ fontSize: "0.72rem", color: "#a1a1aa", textTransform: "uppercase",
                letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                ONI actual (NOAA)
              </div>
              <div style={{ fontSize: "2.5rem", fontWeight: 800, fontFamily: "monospace",
                color: data.oni_actual > 0 ? "#ef4444" : data.oni_actual < 0 ? "#3b82f6" : "#16a34a",
              }}>
                {data.oni_actual > 0 ? "+" : ""}{data.oni_actual.toFixed(2)}°C
              </div>
              <div style={{ fontSize: "0.78rem", color: "#71717a", marginTop: "0.25rem" }}>
                {escActive
                  ? `⚡ Escenario activo: ${escActive === "El Nino" ? "El Niño ☀️" : "La Niña 🌊"}`
                  : "✅ Condiciones neutras actualmente"}
              </div>
            </Card>

            <Card>
              <div style={{ fontSize: "0.72rem", color: "#a1a1aa", textTransform: "uppercase",
                letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                Rendimiento base ML · {toTitleCase(cultivo)}
              </div>
              {data.prediccion_base ? (
                <>
                  <div style={{ fontSize: "2.5rem", fontWeight: 800, fontFamily: "monospace", color: "#16a34a" }}>
                    {data.prediccion_base.rendimiento_predicho} t/ha
                  </div>
                  <div style={{ fontSize: "0.78rem", color: "#71717a", marginTop: "0.25rem" }}>
                    Nivel: {data.prediccion_base.nivel} · Sin evento ENSO
                  </div>
                </>
              ) : (
                <div style={{ fontSize: "0.82rem", color: "#a1a1aa", paddingTop: "0.5rem" }}>
                  Entrena el modelo primero en{" "}
                  <code style={{ fontSize: "0.78rem" }}>POST /ml/train</code>
                </div>
              )}
            </Card>
          </div>

          {/* ── Escenarios El Niño / La Niña ── */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            {(["el_nino", "la_nina"] as const).map((key) => {
              const esc       = data.escenarios[key];
              const isActive  = (key === "el_nino" && escActive === "El Nino")
                             || (key === "la_nina" && escActive === "La Nina");

              return (
                <Card key={key} style={{
                  border: isActive ? `2px solid ${esc.color}` : undefined,
                  position: "relative",
                }}>
                  {isActive && (
                    <div style={{
                      position: "absolute", top: -10, left: 16,
                      background: esc.color, color: "#fff",
                      borderRadius: "100px", padding: "0.15rem 0.75rem",
                      fontSize: "0.68rem", fontWeight: 700, letterSpacing: "0.06em",
                    }}>
                      ACTIVO AHORA
                    </div>
                  )}

                  {/* Header */}
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
                    <div style={{ fontSize: "2.5rem" }}>{esc.icono}</div>
                    <div>
                      <div style={{ fontSize: "1.1rem", fontWeight: 800, color: esc.color }}>
                        Escenario {esc.nombre}
                      </div>
                      <div style={{ fontSize: "0.75rem", color: "#71717a" }}>{esc.descripcion}</div>
                    </div>
                  </div>

                  {/* Condiciones */}
                  <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
                    <div style={{
                      background: "#fafafa", border: "1px solid #f0ede8",
                      borderRadius: 8, padding: "0.5rem 0.85rem", fontSize: "0.82rem",
                    }}>
                      🌧️ Lluvia{" "}
                      <strong style={{ color: esc.color }}>
                        {esc.condiciones.precipitacion_cambio > 0 ? "+" : ""}
                        {esc.condiciones.precipitacion_cambio}%
                      </strong>
                    </div>
                    <div style={{
                      background: "#fafafa", border: "1px solid #f0ede8",
                      borderRadius: 8, padding: "0.5rem 0.85rem", fontSize: "0.82rem",
                    }}>
                      🌡️ Temp{" "}
                      <strong style={{ color: esc.color }}>
                        {esc.condiciones.temperatura_cambio > 0 ? "+" : ""}
                        {esc.condiciones.temperatura_cambio}°C
                      </strong>
                    </div>
                  </div>

                  {/* Impactos */}
                  <div style={{ marginBottom: "0.75rem" }}>
                    <div style={{ fontSize: "0.72rem", color: "#a1a1aa",
                      textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.5rem" }}>
                      Impacto estimado
                    </div>
                    <div style={{
                      fontSize: "1.8rem", fontWeight: 800, color: esc.color,
                      fontFamily: "monospace", lineHeight: 1,
                    }}>
                      {esc.impactos.produccion_estimada > 0 ? "+" : ""}
                      {esc.impactos.produccion_estimada}%
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "#71717a" }}>
                      Producción estimada · {toTitleCase(cultivo)}
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.6rem" }}>
                      <Badge value={`Riesgo: ${esc.impactos.riesgo_agricola}`} color={esc.color} />
                      {esc.impactos.riesgo_sequia && (
                        <Badge value={`Sequía: ${esc.impactos.riesgo_sequia}`} color="#f97316" />
                      )}
                      {esc.impactos.riesgo_inundacion && (
                        <Badge value={`Inund: ${esc.impactos.riesgo_inundacion}`} color="#3b82f6" />
                      )}
                    </div>
                  </div>

                  {/* Cultivos críticos */}
                  <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
                    {esc.cultivos_criticos.map((c) => (
                      <span key={c} style={{
                        background: esc.color + "15", border: `1px solid ${esc.color}30`,
                        borderRadius: "100px", padding: "0.15rem 0.55rem",
                        fontSize: "0.68rem", fontWeight: 600, color: esc.color,
                      }}>🌾 {c}</span>
                    ))}
                  </div>

                  {/* Recomendaciones */}
                  <div style={{
                    background: "#f8fafc", border: "1px solid #e2e8f0",
                    borderRadius: 8, padding: "0.75rem",
                  }}>
                    <div style={{ fontSize: "0.68rem", fontWeight: 700, color: "#64748b",
                      textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.4rem" }}>
                      Recomendaciones
                    </div>
                    {esc.recomendaciones.map((r, i) => (
                      <div key={i} style={{
                        display: "flex", gap: "0.5rem", fontSize: "0.78rem",
                        color: "#374151", marginBottom: "0.3rem",
                      }}>
                        <span style={{ color: esc.color, flexShrink: 0 }}>→</span>
                        {r}
                      </div>
                    ))}
                  </div>
                </Card>
              );
            })}
          </div>

          {/* ── Clima actual como contexto ── */}
          {Object.keys(data.clima_actual).length > 0 && (
            <Card>
              <div style={{ fontSize: "0.72rem", color: "#a1a1aa", textTransform: "uppercase",
                letterSpacing: "0.08em", marginBottom: "0.75rem" }}>
                Clima actual — {toTitleCase(departamento)} · NASA POWER (últimos 30 días)
              </div>
              <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
                {[
                  { label: "Temp. prom",   value: `${data.clima_actual.temperatura_promedio?.toFixed(1) ?? "—"}°C`, icon: "🌡️" },
                  { label: "Precip. prom", value: `${data.clima_actual.precipitacion_promedio?.toFixed(1) ?? "—"} mm/día`, icon: "🌧️" },
                  { label: "Humedad",      value: `${data.clima_actual.humedad_promedio?.toFixed(1) ?? "—"}%`, icon: "💧" },
                  { label: "Días secos",   value: `${data.clima_actual.dias_sin_lluvia ?? "—"}`, icon: "☀️" },
                ].map((m) => (
                  <div key={m.label}>
                    <div style={{ fontSize: "0.72rem", color: "#a1a1aa" }}>{m.icon} {m.label}</div>
                    <div style={{ fontSize: "1rem", fontWeight: 700, fontFamily: "monospace" }}>{m.value}</div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
