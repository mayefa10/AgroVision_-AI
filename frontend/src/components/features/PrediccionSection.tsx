"use client";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Button } from "@/components/ui/Button";
import { usePrediction } from "@/hooks/usePrediction";
import { RISK_BG, RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { RiskLevel } from "@/types";

const PARAMS = [
  { label: "Región",            value: "Antioquia · 05001" },
  { label: "Tipo de predicción", value: "Sequía" },
  { label: "Temperatura",       value: "31°C" },
  { label: "Humedad",           value: "42%" },
  { label: "Precipitación",     value: "4.5 mm" },
  { label: "Altitud",           value: "800 m" },
];

const RISK_ICONS: Record<RiskLevel, string> = {
  critical: "🚨", high: "⚠️", medium: "⚡", low: "✅",
};

const INFO_CARDS = [
  { icon: "🌾", title: "EVA Dataset",    desc: "Rendimiento histórico por cultivo y municipio — Ministerio de Agricultura" },
  { icon: "🛰️", title: "NASA POWER",    desc: "Variables agroclimáticas históricas correlacionadas con producción" },
  { icon: "🗺️", title: "DANE DIVIPOLA", desc: "Georreferenciación oficial para joins espaciales con EVA" },
];

export function PrediccionSection() {
  const { result, loading, execute } = usePrediction();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        {/* Params */}
        <Card>
          <SectionHeader title="Modelo de Predicción" sub="Riesgo climático por variables ambientales" />
          <div style={{ marginBottom: "1.5rem" }}>
            {PARAMS.map(({ label, value }) => (
              <div key={label} style={{
                display: "flex", justifyContent: "space-between",
                padding: "0.6rem 0", borderBottom: "1px solid #f0eeea", fontSize: "0.85rem",
              }}>
                <span style={{ color: "#a1a1aa" }}>{label}</span>
                <span style={{ fontFamily: "monospace", fontWeight: 600, color: "#18181b" }}>{value}</span>
              </div>
            ))}
          </div>
          <Button size="lg" isLoading={loading} onClick={() => execute()}>
            🤖 Ejecutar predicción
          </Button>
        </Card>

        {/* Result */}
        <Card>
          <SectionHeader title="Resultado" sub="Salida del modelo ML" />
          {result ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div style={{
                background: RISK_BG[result.risk],
                borderRadius: 10, padding: "1.5rem", textAlign: "center",
              }}>
                <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
                  {RISK_ICONS[result.risk]}
                </div>
                <div style={{
                  fontSize: "1.75rem", fontWeight: 800,
                  color: RISK_COLORS[result.risk],
                  textTransform: "uppercase", letterSpacing: "0.04em",
                }}>
                  {RISK_LABELS[result.risk]}
                </div>
                <div style={{ fontSize: "0.8rem", color: "#52525b", marginTop: "0.4rem" }}>
                  Nivel de riesgo de sequía
                </div>
              </div>

              {[
                { label: "Confianza", value: `${Math.round(result.confidence * 100)}%` },
                { label: "Tipo",      value: result.prediction_type },
                { label: "Región",    value: result.region_code },
              ].map(({ label, value }) => (
                <div key={label} style={{
                  display: "flex", justifyContent: "space-between",
                  padding: "0.5rem 0", borderBottom: "1px solid #f0eeea", fontSize: "0.85rem",
                }}>
                  <span style={{ color: "#a1a1aa" }}>{label}</span>
                  <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{value}</span>
                </div>
              ))}

              <div style={{
                background: "#f8f7f4", borderRadius: 8,
                padding: "0.85rem", fontSize: "0.8rem",
                lineHeight: 1.6, color: "#52525b", fontStyle: "italic",
              }}>
                "{result.message}"
              </div>
            </div>
          ) : (
            <div style={{
              height: 280, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              color: "#a1a1aa", gap: "0.75rem",
            }}>
              <div style={{ fontSize: "3rem" }}>🤖</div>
              <p style={{ fontSize: "0.85rem", textAlign: "center", lineHeight: 1.6 }}>
                Configura los parámetros y ejecuta<br />la predicción para ver resultados.
              </p>
            </div>
          )}
        </Card>
      </div>

      {/* Info cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
        {INFO_CARDS.map((item) => (
          <Card key={item.title}>
            <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{item.icon}</div>
            <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>{item.title}</div>
            <div style={{ fontSize: "0.75rem", color: "#a1a1aa", lineHeight: 1.6 }}>{item.desc}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}