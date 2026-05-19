"use client";
import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Tabs } from "@/components/ui/Tabs";
import { ClimateAreaChart } from "@/components/features/charts/ClimateAreaChart";
import { useNasaData } from "@/hooks/useNasaData";
import { DEPARTMENTS, CLIMA_TABS, CLIMA_KEY } from "@/lib/constants";
import type { ClimaTab } from "@/types";

export function ClimaSection() {
  const [selectedRegion, setSelectedRegion] = useState("ANTIOQUIA");
  const [climaTab, setClimaTab] = useState<ClimaTab>("Temperatura");
  const { data: nasaData, stats, loading } = useNasaData(selectedRegion);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Region selector */}
      <Card>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.8rem", fontWeight: 500, color: "#a1a1aa", whiteSpace: "nowrap" }}>
            Departamento:
          </span>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {DEPARTMENTS.map((d) => (
              <button key={d} onClick={() => setSelectedRegion(d)} style={{
                padding: "0.35rem 0.85rem",
                borderRadius: 6,
                border: `1px solid ${selectedRegion === d ? "#18181b" : "#e8e5df"}`,
                background: selectedRegion === d ? "#18181b" : "transparent",
                color: selectedRegion === d ? "#ffffff" : "#52525b",
                fontSize: "0.75rem", fontFamily: "monospace", fontWeight: 500,
                cursor: "pointer", transition: "all 0.15s",
              }}>
                {d.split(" ")[0]}
              </button>
            ))}
          </div>
        </div>
      </Card>

      <Tabs items={CLIMA_TABS} active={climaTab} onChange={setClimaTab} />

      <Card>
        <SectionHeader
          title={`${climaTab} — ${selectedRegion}`}
          sub="Últimos 14 días · Fuente: NASA POWER"
          badge="NASA POWER"
        />
        <div style={{ height: 288 }}>
          {nasaData.length > 0 && !loading ? (
            <ClimateAreaChart data={nasaData} dataKey={CLIMA_KEY[climaTab]} tab={climaTab} />
          ) : (
            <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "#a1a1aa", fontSize: "0.85rem" }}>
              {loading ? "Cargando datos NASA POWER..." : "Sin datos disponibles"}
            </div>
          )}
        </div>
      </Card>

      {nasaData.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
          {[
            { label: "Temp. promedio",     value: `${stats.avgTemp.toFixed(1)}°C`,      icon: "🌡️", color: "#16a34a" },
            { label: "Precipitación total", value: `${stats.totalPrecip.toFixed(1)} mm`, icon: "🌧️", color: "#0891b2" },
            { label: "Humedad promedio",    value: `${stats.avgHumidity.toFixed(1)}%`,   icon: "💧", color: "#7c3aed" },
          ].map((s) => (
            <Card key={s.label}>
              <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{s.icon}</div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</div>
              <div style={{ fontSize: "0.72rem", color: "#a1a1aa", marginTop: "0.35rem" }}>{s.label} · 14 días</div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}