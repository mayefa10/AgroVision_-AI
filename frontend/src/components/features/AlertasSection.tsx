"use client";
import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { useAlertas } from "@/hooks/useAlertas";

const TIPO_ICONS: Record<string, string> = {
  sequia:        "🌵",
  inundacion:    "🌊",
  helada:        "❄️",
  estres_termico:"🌡️",
};

const SEVERIDAD_COLORS: Record<string, string> = {
  critica: "#ef4444",
  alta:    "#f97316",
  media:   "#f59e0b",
  baja:    "#22c55e",
};

const SEVERIDAD_BG: Record<string, string> = {
  critica: "#fee2e2",
  alta:    "#ffedd5",
  media:   "#fef3c7",
  baja:    "#dcfce7",
};

const DEPTS = ["ANTIOQUIA","CUNDINAMARCA","NARINO","TOLIMA","META","BOYACA","CORDOBA","SANTANDER","HUILA","VALLE DEL CAUCA"];

export function AlertasSection() {
  const [dept, setDept] = useState<string | undefined>(undefined);
  const { alertas, loading, resumen } = useAlertas(dept);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

      {/* Resumen cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "1rem" }}>
        {[
          { label: "Críticas",  value: resumen.criticas, color: "#ef4444", icon: "🚨" },
          { label: "Altas",     value: resumen.altas,    color: "#f97316", icon: "⚠️" },
          { label: "Medias",    value: resumen.medias,   color: "#f59e0b", icon: "⚡" },
          { label: "Total",     value: alertas.length,   color: "#16a34a", icon: "📋" },
        ].map(s => (
          <Card key={s.label}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: "0.75rem", color: "#a1a1aa" }}>{s.label}</span>
              <span style={{ fontSize: "1.1rem" }}>{s.icon}</span>
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 700, color: s.color, lineHeight: 1, margin: "0.4rem 0" }}>
              {s.value}
            </div>
          </Card>
        ))}
      </div>

      {/* Filtro departamento */}
      <Card style={{ padding: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.8rem", color: "#a1a1aa", fontWeight: 500 }}>Departamento:</span>
          <button onClick={() => setDept(undefined)} style={{
            padding: "0.35rem 0.85rem", borderRadius: 6, fontSize: "0.75rem",
            fontFamily: "monospace", cursor: "pointer", transition: "all 0.15s",
            border: `1px solid ${!dept ? "#18181b" : "#e8e5df"}`,
            background: !dept ? "#18181b" : "transparent",
            color: !dept ? "#fff" : "#52525b",
          }}>Todos</button>
          {DEPTS.map(d => (
            <button key={d} onClick={() => setDept(d)} style={{
              padding: "0.35rem 0.85rem", borderRadius: 6, fontSize: "0.75rem",
              fontFamily: "monospace", cursor: "pointer", transition: "all 0.15s",
              border: `1px solid ${dept === d ? "#18181b" : "#e8e5df"}`,
              background: dept === d ? "#18181b" : "transparent",
              color: dept === d ? "#fff" : "#52525b",
            }}>{d.split(" ")[0]}</button>
          ))}
        </div>
      </Card>

      {/* Lista alertas */}
      <Card>
        <SectionHeader
          title="Alertas Activas"
          sub={dept ? `${dept} · datos NASA POWER en tiempo real` : "Nacional · datos NASA POWER en tiempo real"}
          badge="IA"
        />
        {loading ? (
          <div style={{ padding: "3rem", textAlign: "center", color: "#a1a1aa" }}>
            Analizando condiciones climáticas...
          </div>
        ) : alertas.length === 0 ? (
          <div style={{ padding: "3rem", textAlign: "center" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>✅</div>
            <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>Sin alertas activas</div>
            <div style={{ fontSize: "0.82rem", color: "#a1a1aa" }}>
              Las condiciones climáticas están dentro de los rangos normales.
            </div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {alertas.map(alerta => (
              <div key={alerta.id} style={{
                border: `1px solid ${SEVERIDAD_COLORS[alerta.severidad]}30`,
                borderLeft: `4px solid ${SEVERIDAD_COLORS[alerta.severidad]}`,
                borderRadius: 10, padding: "1.25rem",
                background: SEVERIDAD_BG[alerta.severidad] + "40",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <span style={{ fontSize: "1.4rem" }}>{TIPO_ICONS[alerta.tipo]}</span>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: "0.9rem" }}>{alerta.titulo}</div>
                      <div style={{ fontSize: "0.72rem", fontFamily: "monospace", color: "#a1a1aa" }}>{alerta.id}</div>
                    </div>
                  </div>
                  <span style={{
                    background: SEVERIDAD_COLORS[alerta.severidad],
                    color: "#fff", padding: "0.2rem 0.65rem",
                    borderRadius: "100px", fontSize: "0.68rem",
                    fontWeight: 700, textTransform: "uppercase",
                    letterSpacing: "0.06em", flexShrink: 0,
                  }}>
                    {alerta.severidad}
                  </span>
                </div>

                <p style={{ fontSize: "0.82rem", color: "#52525b", lineHeight: 1.6, marginBottom: "0.75rem" }}>
                  {alerta.mensaje}
                </p>

                <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
                  {Object.entries(alerta.variables).map(([k, v]) => (
                    <div key={k} style={{ fontSize: "0.75rem" }}>
                      <span style={{ color: "#a1a1aa", textTransform: "capitalize" }}>{k.replace(/_/g, " ")}: </span>
                      <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{Number(v).toFixed(1)}</span>
                    </div>
                  ))}
                </div>

                {alerta.cultivos_afectados.length > 0 && (
                  <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
                    {alerta.cultivos_afectados.map(c => (
                      <span key={c} style={{
                        background: "#f5f4f0", border: "1px solid #e8e5df",
                        borderRadius: "100px", padding: "0.15rem 0.6rem",
                        fontSize: "0.7rem", fontWeight: 500,
                      }}>🌾 {c}</span>
                    ))}
                  </div>
                )}

                <div style={{
                  background: "rgba(255,255,255,0.7)", borderRadius: 6,
                  padding: "0.6rem 0.85rem", fontSize: "0.78rem",
                  color: "#52525b", borderLeft: `3px solid ${SEVERIDAD_COLORS[alerta.severidad]}`,
                }}>
                  💡 {alerta.recomendacion}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
