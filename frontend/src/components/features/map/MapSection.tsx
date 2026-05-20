"use client";
import { useState } from "react";
import dynamic from "next/dynamic";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { RiskBadge } from "@/components/ui/Badge";
import { useRegions } from "@/hooks/useRegions";
import { RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { Region, RiskLevel } from "@/types";

// Carga dinámica — Leaflet no funciona en SSR
const ColombiaMap = dynamic(
  () => import("./ColombiaMap").then((m) => ({ default: m.ColombiaMap })),
  {
    ssr: false,
    loading: () => (
      <div style={{
        width: "100%", height: "100%",
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "#f8f7f4", borderRadius: 12, color: "#a1a1aa", fontSize: "0.85rem",
      }}>
        Cargando mapa...
      </div>
    ),
  }
);

export function MapSection() {
  const { regions, riskCounts, loading } = useRegions();
  const [selected, setSelected] = useState<Region | null>(null);
  const [filter, setFilter] = useState<RiskLevel | "all">("all");

  const filtered = filter === "all" ? regions : regions.filter(r => r.risk === filter);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

      {/* Filtros */}
      <Card style={{ padding: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.8rem", fontWeight: 500, color: "#a1a1aa" }}>Filtrar:</span>
          {(["all", "critical", "high", "medium", "low"] as const).map((level) => (
            <button key={level} onClick={() => setFilter(level)} style={{
              padding: "0.35rem 0.85rem",
              borderRadius: 6,
              border: `1px solid ${filter === level ? "#18181b" : "#e8e5df"}`,
              background: filter === level ? "#18181b" : "transparent",
              color: filter === level ? "#fff" : "#52525b",
              fontSize: "0.75rem", fontFamily: "monospace", fontWeight: 500,
              cursor: "pointer", transition: "all 0.15s",
            }}>
              {level === "all" ? "Todos" : RISK_LABELS[level]}
              {level !== "all" && (
                <span style={{
                  marginLeft: "0.35rem",
                  background: RISK_COLORS[level],
                  color: "#fff",
                  borderRadius: "100px",
                  padding: "0 0.35rem",
                  fontSize: "0.65rem",
                }}>
                  {riskCounts[level]}
                </span>
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* Map + Panel */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1rem" }}>

        {/* Mapa */}
        <Card style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ height: 520, position: "relative" }}>
            {!loading && (
              <ColombiaMap
                regions={filtered}
                onRegionClick={setSelected}
              />
            )}
            {/* Legend */}
            <div style={{
              position: "absolute", bottom: 16, left: 16, zIndex: 1000,
              background: "rgba(255,255,255,0.95)",
              borderRadius: 10, padding: "0.75rem 1rem",
              border: "1px solid #e8e5df",
              boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
            }}>
              <div style={{ fontSize: "0.65rem", fontFamily: "monospace", textTransform: "uppercase", letterSpacing: "0.1em", color: "#a1a1aa", marginBottom: "0.5rem" }}>
                Nivel de riesgo
              </div>
              {(["critical","high","medium","low"] as RiskLevel[]).map(level => (
                <div key={level} style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.3rem" }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: RISK_COLORS[level] }} />
                  <span style={{ fontSize: "0.75rem", color: "#52525b" }}>{RISK_LABELS[level]}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Panel lateral */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {/* Región seleccionada */}
          <Card>
            <SectionHeader title="Región seleccionada" sub="Click en un marcador" />
            {selected ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div style={{
                  padding: "1rem", borderRadius: 8,
                  background: RISK_COLORS[selected.risk] + "15",
                  border: `1px solid ${RISK_COLORS[selected.risk]}30`,
                  textAlign: "center",
                }}>
                  <div style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "0.4rem" }}>{selected.region}</div>
                  <RiskBadge level={selected.risk} />
                </div>
                {[
                  { label: "Código DANE", value: selected.code },
                  { label: "Latitud",     value: selected.lat.toFixed(4) },
                  { label: "Longitud",    value: selected.lng.toFixed(4) },
                ].map(({ label, value }) => (
                  <div key={label} style={{
                    display: "flex", justifyContent: "space-between",
                    fontSize: "0.82rem", padding: "0.4rem 0",
                    borderBottom: "1px solid #f0eeea",
                  }}>
                    <span style={{ color: "#a1a1aa" }}>{label}</span>
                    <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: "center", color: "#a1a1aa", fontSize: "0.82rem", padding: "1rem 0" }}>
                <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>🗺️</div>
                Selecciona un departamento en el mapa
              </div>
            )}
          </Card>

          {/* Resumen */}
          <Card>
            <SectionHeader title="Resumen" sub={`${filtered.length} regiones`} />
            {(["critical","high","medium","low"] as RiskLevel[]).map(level => {
              const count = regions.filter(r => r.risk === level).length;
              if (count === 0) return null;
              return (
                <div key={level} style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  padding: "0.5rem 0", borderBottom: "1px solid #f0eeea",
                  cursor: "pointer",
                }} onClick={() => setFilter(level)}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: RISK_COLORS[level] }} />
                    <span style={{ fontSize: "0.82rem", fontWeight: 500 }}>{RISK_LABELS[level]}</span>
                  </div>
                  <span style={{
                    fontFamily: "monospace", fontSize: "0.78rem",
                    background: RISK_COLORS[level] + "20",
                    color: RISK_COLORS[level],
                    padding: "0.15rem 0.5rem", borderRadius: 4, fontWeight: 600,
                  }}>{count}</span>
                </div>
              );
            })}
          </Card>
        </div>
      </div>

      {/* Lista mobile */}
      <Card style={{ display: "none" }} className="map-mobile-list">
        <SectionHeader title="Regiones" sub="Toca para ver detalle" />
        {filtered.map(r => (
          <div key={r.code} onClick={() => setSelected(r)} style={{
            display: "flex", justifyContent: "space-between", alignItems: "center",
            padding: "0.6rem 0", borderBottom: "1px solid #f0eeea", cursor: "pointer",
          }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>{r.region}</span>
            <RiskBadge level={r.risk} />
          </div>
        ))}
      </Card>
    </div>
  );
}