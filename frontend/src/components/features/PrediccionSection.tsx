"use client";
import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Button } from "@/components/ui/Button";
import { usePrediction } from "@/hooks/usePrediction";
import { useMlModel } from "@/hooks/useMlModel";
import { RISK_BG, RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { RiskLevel } from "@/types";

const RISK_ICONS: Record<RiskLevel, string> = {
  critical: "🚨", high: "⚠️", medium: "⚡", low: "✅",
};

const NIVEL_COLORS: Record<string, string> = {
  excelente: "#16a34a", bueno: "#22c55e",
  regular: "#f59e0b",   bajo: "#ef4444",
};

const CULTIVOS = ["MAIZ","CAFE","ARROZ","PAPA","AGUACATE","FRIJOL","CAÑA DE AZUCAR","SOYA"];
const GRUPOS: Record<string, string> = {
  "MAIZ": "CEREALES Y LEGUMINOSAS", "CAFE": "BEBIDAS Y ESTIMULANTES",
  "ARROZ": "CEREALES Y LEGUMINOSAS", "PAPA": "TUBERCULOS Y PLATANOS",
  "AGUACATE": "FRUTALES", "FRIJOL": "CEREALES Y LEGUMINOSAS",
  "CAÑA DE AZUCAR": "OTROS CULTIVOS TRANSITORIOS", "SOYA": "CEREALES Y LEGUMINOSAS",
};

export function PrediccionSection() {
  const { result, loading, execute } = usePrediction();
  const { result: mlResult, trainResult, loading: mlLoading, training, predict, train } = useMlModel();

  const [mlForm, setMlForm] = useState({
    departamento: "ANTIOQUIA",
    cultivo: "MAIZ",
    area_sembrada: 100,
    anio: 2024,
    periodo: 1,
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

      {/* Fila 1: Predicción riesgo + resultado */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <Card>
          <SectionHeader title="Predicción de Riesgo Climático" sub="Modelo heurístico por variables ambientales" />
          {[
            ["Región", "Antioquia · 05001"],
            ["Tipo", "Sequía"],
            ["Temperatura", "31°C"],
            ["Humedad", "42%"],
            ["Precipitación", "4.5 mm"],
            ["Altitud", "800 m"],
          ].map(([l, v]) => (
            <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: "1px solid #f0eeea", fontSize: "0.85rem" }}>
              <span style={{ color: "#a1a1aa" }}>{l}</span>
              <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{v}</span>
            </div>
          ))}
          <div style={{ marginTop: "1.25rem" }}>
            <Button size="lg" isLoading={loading} onClick={() => execute()}>
              🤖 Ejecutar predicción de riesgo
            </Button>
          </div>
        </Card>

        <Card>
          <SectionHeader title="Resultado — Riesgo Climático" sub="Salida del modelo" />
          {result ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
              <div style={{ padding: "1.25rem", background: RISK_BG[result.risk], borderRadius: 10, textAlign: "center" }}>
                <div style={{ fontSize: "2rem", marginBottom: "0.35rem" }}>{RISK_ICONS[result.risk]}</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 800, color: RISK_COLORS[result.risk], textTransform: "uppercase" }}>
                  {RISK_LABELS[result.risk]}
                </div>
                <div style={{ fontSize: "0.78rem", color: "#52525b", marginTop: "0.3rem" }}>Riesgo de sequía</div>
              </div>
              {[["Confianza", `${Math.round(result.confidence * 100)}%`], ["Tipo", result.prediction_type], ["Región", result.region_code]].map(([l, v]) => (
                <div key={l} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", padding: "0.4rem 0", borderBottom: "1px solid #f0eeea" }}>
                  <span style={{ color: "#a1a1aa" }}>{l}</span>
                  <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
              <div style={{ padding: "0.75rem", background: "#f8f7f4", borderRadius: 8, fontSize: "0.78rem", color: "#52525b", fontStyle: "italic" }}>
                "{result.message}"
              </div>
            </div>
          ) : (
            <div style={{ height: 200, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#a1a1aa", gap: "0.5rem" }}>
              <div style={{ fontSize: "2.5rem" }}>🤖</div>
              <p style={{ fontSize: "0.82rem", textAlign: "center" }}>Ejecuta la predicción de riesgo para ver resultados.</p>
            </div>
          )}
        </Card>
      </div>

      {/* Fila 2: ML Real */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <Card>
          <SectionHeader title="Predicción de Rendimiento Agrícola" sub="Random Forest entrenado con datos EVA reales" badge="ML REAL" />

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1rem" }}>
            {/* Departamento */}
            <div>
              <label style={{ fontSize: "0.75rem", color: "#a1a1aa", display: "block", marginBottom: "0.3rem" }}>Departamento</label>
              <select value={mlForm.departamento} onChange={e => setMlForm(f => ({ ...f, departamento: e.target.value }))} style={{
                width: "100%", padding: "0.5rem 0.75rem", borderRadius: 6,
                border: "1px solid #e8e5df", fontSize: "0.82rem",
                fontFamily: "inherit", background: "#fff", cursor: "pointer",
              }}>
                {["ANTIOQUIA","CUNDINAMARCA","VALLE DEL CAUCA","TOLIMA","META","BOYACA","NARINO","SANTANDER"].map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Cultivo */}
            <div>
              <label style={{ fontSize: "0.75rem", color: "#a1a1aa", display: "block", marginBottom: "0.3rem" }}>Cultivo</label>
              <select value={mlForm.cultivo} onChange={e => setMlForm(f => ({ ...f, cultivo: e.target.value }))} style={{
                width: "100%", padding: "0.5rem 0.75rem", borderRadius: 6,
                border: "1px solid #e8e5df", fontSize: "0.82rem",
                fontFamily: "inherit", background: "#fff", cursor: "pointer",
              }}>
                {CULTIVOS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            {/* Área */}
            <div>
              <label style={{ fontSize: "0.75rem", color: "#a1a1aa", display: "block", marginBottom: "0.3rem" }}>
                Área sembrada (ha): {mlForm.area_sembrada}
              </label>
              <input type="range" min={10} max={500} step={10}
                value={mlForm.area_sembrada}
                onChange={e => setMlForm(f => ({ ...f, area_sembrada: Number(e.target.value) }))}
                style={{ width: "100%", accentColor: "#16a34a" }}
              />
            </div>

            {/* Año */}
            <div>
              <label style={{ fontSize: "0.75rem", color: "#a1a1aa", display: "block", marginBottom: "0.3rem" }}>Año</label>
              <select value={mlForm.anio} onChange={e => setMlForm(f => ({ ...f, anio: Number(e.target.value) }))} style={{
                width: "100%", padding: "0.5rem 0.75rem", borderRadius: 6,
                border: "1px solid #e8e5df", fontSize: "0.82rem",
                fontFamily: "inherit", background: "#fff",
              }}>
                {[2024, 2023, 2022, 2021].map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <Button size="lg" isLoading={mlLoading} onClick={() => predict({
              departamento: mlForm.departamento,
              cultivo: mlForm.cultivo,
              grupo_cultivo: GRUPOS[mlForm.cultivo] || "OTROS",
              area_sembrada: mlForm.area_sembrada,
              anio: mlForm.anio,
              periodo: mlForm.periodo,
            })}>
              🌾 Predecir rendimiento
            </Button>
            <Button size="md" variant="ghost" isLoading={training} onClick={train}>
              🔄 Reentrenar modelo con datos EVA
            </Button>
          </div>
        </Card>

        <Card>
          <SectionHeader title="Resultado — Rendimiento" sub="Predicción con Random Forest" />

          {mlResult ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
              <div style={{
                padding: "1.5rem", borderRadius: 10, textAlign: "center",
                background: (NIVEL_COLORS[mlResult.nivel] || "#16a34a") + "15",
                border: `1px solid ${(NIVEL_COLORS[mlResult.nivel] || "#16a34a")}30`,
              }}>
                <div style={{ fontSize: "2.5rem", marginBottom: "0.4rem" }}>
                  {mlResult.nivel === "excelente" ? "🏆" : mlResult.nivel === "bueno" ? "✅" : mlResult.nivel === "regular" ? "⚡" : "⚠️"}
                </div>
                <div style={{ fontSize: "2.5rem", fontWeight: 800, color: NIVEL_COLORS[mlResult.nivel] || "#16a34a", lineHeight: 1 }}>
                  {mlResult.rendimiento_predicho}
                </div>
                <div style={{ fontSize: "0.82rem", color: "#52525b", marginTop: "0.3rem" }}>
                  toneladas / hectárea · nivel <strong>{mlResult.nivel}</strong>
                </div>
              </div>

              {[
                ["Cultivo",     mlResult.cultivo],
                ["Departamento", mlResult.departamento],
                ["Año",         String(mlResult.anio)],
                ["Área",        `${mlResult.area_sembrada} ha`],
              ].map(([l, v]) => (
                <div key={l} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", padding: "0.4rem 0", borderBottom: "1px solid #f0eeea" }}>
                  <span style={{ color: "#a1a1aa" }}>{l}</span>
                  <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ height: 200, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#a1a1aa", gap: "0.5rem" }}>
              <div style={{ fontSize: "2.5rem" }}>🌾</div>
              <p style={{ fontSize: "0.82rem", textAlign: "center" }}>Selecciona cultivo y departamento para predecir el rendimiento.</p>
            </div>
          )}

          {/* Métricas del modelo */}
          {trainResult && (
            <div style={{ marginTop: "1rem", padding: "0.85rem", background: "#f8f7f4", borderRadius: 8 }}>
              <div style={{ fontSize: "0.65rem", fontFamily: "monospace", textTransform: "uppercase", letterSpacing: "0.1em", color: "#a1a1aa", marginBottom: "0.5rem" }}>
                Métricas del modelo
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.5rem" }}>
                {[
                  ["R²", trainResult.r2.toFixed(3)],
                  ["MAE", `${trainResult.mae.toFixed(2)} t/ha`],
                  ["Registros", trainResult.registros_entrenamiento],
                ].map(([l, v]) => (
                  <div key={String(l)} style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "1rem", fontWeight: 700, color: "#16a34a" }}>{v}</div>
                    <div style={{ fontSize: "0.65rem", color: "#a1a1aa" }}>{l}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Info sources */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
        {[
          { icon: "🌾", title: "EVA Dataset", desc: "4,516 registros reales · Ministerio de Agricultura · 2019-2024" },
          { icon: "🛰️", title: "NASA POWER", desc: "Variables agroclimáticas históricas correlacionadas con producción" },
          { icon: "🤖", title: "Random Forest", desc: `R²=0.661 · MAE=5.32 t/ha · 200 árboles · datos abiertos` },
        ].map(item => (
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
