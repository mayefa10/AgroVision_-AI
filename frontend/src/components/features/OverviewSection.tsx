"use client";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { RiskBadge } from "@/components/ui/Badge";
import { useRegions } from "@/hooks/useRegions";
import { useAlertas } from "@/hooks/useAlertas";
import { RiskBarChart } from "./charts/RiskBarChart";
import { RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { RiskLevel } from "@/types";

const TIPO_ICONS: Record<string, string> = {
  sequia: "🌵", inundacion: "🌊", helada: "❄️", estres_termico: "🌡️",
};

const SEVERIDAD_COLORS: Record<string, string> = {
  critica: "#ef4444", alta: "#f97316", media: "#f59e0b", baja: "#22c55e",
};

export function OverviewSection() {
  const { regions, riskCounts, loading } = useRegions();
  const { alertas, resumen: alertResumen } = useAlertas("NARINO");

  if (loading) return <div style={{ padding: "2rem", textAlign: "center", color: "#a1a1aa" }}>Cargando...</div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem" }}>
        <KpiCard label="Regiones" value={String(regions.length)} sub="Departamentos Colombia" icon="🗺️" />
        <KpiCard label="Alertas críticas" value={String(riskCounts.critical)} sub="Atención inmediata" color="#ef4444" icon="🚨" />
        <KpiCard label="Riesgo alto" value={String(riskCounts.high)} sub="Monitoreo activo" color="#f97316" icon="⚠️" />
        <KpiCard label="Condición normal" value={String(riskCounts.low)} sub="Sin alertas" icon="✅" />
      </div>

      {/* Charts */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
        <Card>
          <SectionHeader title="Riesgo por Región" sub="Variables climáticas actuales" />
          <div style={{ height: 224 }}>
            <RiskBarChart regions={regions} />
          </div>
        </Card>

        <Card>
          <SectionHeader title="Distribución de Riesgo" sub="Regiones por nivel" />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {(["critical","high","medium","low"] as RiskLevel[]).map(level => {
              const count = riskCounts[level];
              const pct = regions.length ? Math.round((count / regions.length) * 100) : 0;
              return (
                <div key={level}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <div style={{ width: 8, height: 8, borderRadius: 2, background: RISK_COLORS[level] }} />
                      <span style={{ fontSize: "0.82rem", fontWeight: 500 }}>{RISK_LABELS[level]}</span>
                    </div>
                    <span style={{ fontSize: "0.75rem", fontFamily: "monospace", color: "#a1a1aa" }}>{count} · {pct}%</span>
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
            {regions.slice(0, 6).map(r => (
              <div key={r.code} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.45rem 0", borderBottom: "1px solid #f0eeea" }}>
                <span style={{ fontSize: "0.82rem", fontWeight: 500 }}>{r.region}</span>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <span style={{ fontSize: "0.7rem", fontFamily: "monospace", color: "#a1a1aa" }}>{r.code}</span>
                  <RiskBadge level={r.risk} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Alertas recientes */}
      {alertas.length > 0 && (
        <Card>
          <SectionHeader title="Alertas Recientes" sub="Nariño · NASA POWER en tiempo real" badge="IA" />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {alertas.slice(0, 3).map(a => (
              <div key={a.id} style={{
                display: "flex", alignItems: "center", gap: "0.75rem",
                padding: "0.75rem", borderRadius: 8,
                background: SEVERIDAD_COLORS[a.severidad] + "10",
                border: `1px solid ${SEVERIDAD_COLORS[a.severidad]}25`,
              }}>
                <span style={{ fontSize: "1.25rem" }}>{TIPO_ICONS[a.tipo]}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "0.82rem", fontWeight: 600 }}>{a.titulo}</div>
                  <div style={{ fontSize: "0.72rem", color: "#a1a1aa", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {a.cultivos_afectados.join(", ")}
                  </div>
                </div>
                <span style={{
                  background: SEVERIDAD_COLORS[a.severidad], color: "#fff",
                  padding: "0.15rem 0.5rem", borderRadius: "100px",
                  fontSize: "0.65rem", fontWeight: 700, textTransform: "uppercase",
                  flexShrink: 0,
                }}>{a.severidad}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
