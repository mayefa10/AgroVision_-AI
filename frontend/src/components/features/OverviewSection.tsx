"use client";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { RiskBadge } from "@/components/ui/Badge";
import { useRegions } from "@/hooks/useRegions";
import { RiskBarChart } from "./charts/RiskBarChart";
import { RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { RiskLevel } from "@/types";

export function OverviewSection() {
  const { regions, riskCounts, loading } = useRegions();

  if (loading) return (
    <div style={{ padding: "2rem", textAlign: "center", color: "#a1a1aa" }}>Cargando...</div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem", width: "100%", minWidth: 0 }}>

      {/* KPIs — 2 cols en mobile, 4 en desktop */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(2, 1fr)",
        gap: "0.75rem",
      }}>
        <KpiCard label="Regiones" value={String(regions.length)} sub="Departamentos" icon="🗺️" />
        <KpiCard label="Crítico" value={String(riskCounts.critical)} sub="Atención inmediata" color="#ef4444" icon="🚨" />
        <KpiCard label="Riesgo alto" value={String(riskCounts.high)} sub="Monitoreo activo" color="#f97316" icon="⚠️" />
        <KpiCard label="Normal" value={String(riskCounts.low)} sub="Sin alertas" icon="✅" />
      </div>

      {/* Charts — 1 col en mobile, 2 en desktop */}
      <Card style={{ width: "100%", minWidth: 0, overflow: "hidden" }}>
        <SectionHeader title="Riesgo por Región" sub="Variables climáticas actuales" />
        <div style={{ height: 200, width: "100%" }}>
          <RiskBarChart regions={regions} />
        </div>
      </Card>

      <Card style={{ width: "100%", minWidth: 0 }}>
        <SectionHeader title="Distribución de Riesgo" sub="Regiones por nivel" />
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {(["critical", "high", "medium", "low"] as RiskLevel[]).map((level) => {
            const count = riskCounts[level];
            const pct = regions.length ? Math.round((count / regions.length) * 100) : 0;
            return (
              <div key={level}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <div style={{ width: 8, height: 8, borderRadius: 2, background: RISK_COLORS[level], flexShrink: 0 }} />
                    <span style={{ fontSize: "0.82rem", fontWeight: 500 }}>{RISK_LABELS[level]}</span>
                  </div>
                  <span style={{ fontSize: "0.75rem", fontFamily: "monospace", color: "#a1a1aa" }}>
                    {count} · {pct}%
                  </span>
                </div>
                <div style={{ height: 6, borderRadius: 3, background: "#f0eeea", overflow: "hidden" }}>
                  <div style={{ height: "100%", borderRadius: 3, background: RISK_COLORS[level], width: `${pct}%`, transition: "width 1s ease" }} />
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ marginTop: "1.25rem" }}>
          <div style={{ fontSize: "0.65rem", fontFamily: "monospace", textTransform: "uppercase", letterSpacing: "0.1em", color: "#a1a1aa", marginBottom: "0.5rem" }}>
            Detalle por región
          </div>
          {regions.slice(0, 6).map((r) => (
            <div key={r.code} style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: "0.45rem 0", borderBottom: "1px solid #f0eeea",
            }}>
              <span style={{ fontSize: "0.82rem", fontWeight: 500 }}>{r.region}</span>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexShrink: 0 }}>
                <span style={{ fontSize: "0.7rem", fontFamily: "monospace", color: "#a1a1aa" }}>{r.code}</span>
                <RiskBadge level={r.risk} />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}