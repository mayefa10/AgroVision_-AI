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

  if (loading) return <div style={{ padding: "2rem", textAlign: "center", color: "#a1a1aa" }}>Cargando...</div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>

      {/* KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem" }}>
        <KpiCard label="Regiones monitoreadas" value={String(regions.length)} sub="Departamentos Colombia" icon="🗺️" />
        <KpiCard label="Alertas críticas" value={String(riskCounts.critical)} sub="Requieren atención inmediata" color="#ef4444" icon="🚨" />
        <KpiCard label="Riesgo alto" value={String(riskCounts.high)} sub="Monitoreo activo" color="#f97316" icon="⚠️" />
        <KpiCard label="Condición normal" value={String(riskCounts.low)} sub="Sin alertas activas" icon="✅" />
      </div>

      {/* Charts */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <Card>
          <SectionHeader title="Nivel de Riesgo por Región" sub="Basado en variables climáticas actuales" />
          <div style={{ height: "224px" }}>
            <RiskBarChart regions={regions} />
          </div>
        </Card>

        <Card>
          <SectionHeader title="Distribución de Riesgo" sub="Total de regiones por nivel" />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "0.5rem" }}>
            {(["critical", "high", "medium", "low"] as RiskLevel[]).map((level) => {
              const count = riskCounts[level];
              const pct = regions.length ? Math.round((count / regions.length) * 100) : 0;
              return (
                <div key={level}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <div style={{ width: 8, height: 8, borderRadius: 2, backgroundColor: RISK_COLORS[level] }} />
                      <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>{RISK_LABELS[level]}</span>
                    </div>
                    <span style={{ fontSize: "0.78rem", fontFamily: "monospace", color: "#a1a1aa" }}>
                      {count} regiones · {pct}%
                    </span>
                  </div>
                  <div style={{ height: 6, borderRadius: 3, backgroundColor: "#f5f4f0", overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 3, backgroundColor: RISK_COLORS[level], width: `${pct}%`, transition: "width 1s ease" }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: "1.5rem" }}>
            <div style={{ fontSize: "0.65rem", fontFamily: "monospace", textTransform: "uppercase", letterSpacing: "0.1em", color: "#a1a1aa", marginBottom: "0.5rem" }}>
              Detalle por región
            </div>
            {regions.slice(0, 6).map((r) => (
              <div key={r.code} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0", borderBottom: "1px solid #f0eeea" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>{r.region}</span>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ fontSize: "0.7rem", fontFamily: "monospace", color: "#a1a1aa" }}>{r.code}</span>
                  <RiskBadge level={r.risk} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}