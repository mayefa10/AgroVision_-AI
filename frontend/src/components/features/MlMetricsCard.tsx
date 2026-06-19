"use client";

import { Card } from "@/components/ui/Card";
import { useMlMetrics } from "@/hooks/useMlmetrics";

const FEATURE_LABELS: Record<string, string> = {
  departamento_enc:  "Departamento",
  cultivo_enc:       "Cultivo",
  grupo_cultivo_enc: "Grupo de cultivo",
  area_sembrada:     "Área sembrada",
  anio:              "Año",
  periodo_num:       "Periodo",
};

function safeFixed(val: unknown, dec = 1): string {
  const n = Number(val);
  return isNaN(n) ? "—" : n.toFixed(dec);
}

/**
 * Tarjeta de métricas del modelo ML — colocar dentro de EscenariosSection.tsx
 * justo después del grid "ONI actual + predicción base".
 *
 * Uso:
 *   import { MlMetricsCard } from "@/components/features/MlMetricsCard";
 *   ...
 *   <MlMetricsCard />
 */
export function MlMetricsCard() {
  const { data, loading, error } = useMlMetrics();

  if (loading) {
    return (
      <Card>
        <div style={{ padding: "1.5rem", textAlign: "center", color: "#a1a1aa", fontSize: "0.82rem" }}>
          Cargando métricas del modelo...
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <div style={{ padding: "1.5rem", textAlign: "center", color: "#ef4444", fontSize: "0.82rem" }}>
          Error al cargar métricas: {error}
        </div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <div style={{ padding: "1.5rem", textAlign: "center" }}>
          <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>🤖</div>
          <div style={{ fontSize: "0.85rem", color: "#71717a", marginBottom: "0.25rem" }}>
            Modelo aún no entrenado
          </div>
          <div style={{ fontSize: "0.75rem", color: "#a1a1aa" }}>
            Llama a <code style={{ fontSize: "0.72rem" }}>POST /ml/train</code> para generar predicciones
          </div>
        </div>
      </Card>
    );
  }

  // R² en porcentaje para la barra visual
  const r2Pct = Math.max(0, Math.min(100, data.r2 * 100));
  const r2Color = data.r2 >= 0.7 ? "#16a34a" : data.r2 >= 0.5 ? "#f59e0b" : "#ef4444";

  // Ordenar features por importancia descendente
  const features = Object.entries(data.feature_importance)
    .sort((a, b) => b[1] - a[1])
    .filter(([, v]) => v > 0);

  const fechaEntrenamiento = new Date(data.trained_at).toLocaleString("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  });

  return (
    <Card>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "#a1a1aa",
            textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Modelo ML — Random Forest
          </div>
          <div style={{ fontSize: "0.72rem", color: "#a1a1aa", marginTop: "0.2rem" }}>
            Entrenado: {fechaEntrenamiento}
          </div>
        </div>
        <span style={{
          background: "#dcfce7", color: "#16a34a", border: "1px solid #bbf7d0",
          borderRadius: "100px", padding: "0.2rem 0.65rem",
          fontSize: "0.68rem", fontWeight: 700,
        }}>
          ✓ Entrenado
        </span>
      </div>

      {/* Métricas principales */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div style={{ background: "#fafafa", border: "1px solid #f0ede8", borderRadius: 10, padding: "1rem" }}>
          <div style={{ fontSize: "0.72rem", color: "#a1a1aa", marginBottom: "0.3rem" }}>
            MAE (error promedio)
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, fontFamily: "monospace", color: "#18181b" }}>
            ±{safeFixed(data.mae, 2)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "#a1a1aa" }}>t/ha de desviación</div>
        </div>

        <div style={{ background: "#fafafa", border: "1px solid #f0ede8", borderRadius: 10, padding: "1rem" }}>
          <div style={{ fontSize: "0.72rem", color: "#a1a1aa", marginBottom: "0.3rem" }}>
            R² (varianza explicada)
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, fontFamily: "monospace", color: r2Color }}>
            {safeFixed(r2Pct, 1)}%
          </div>
          <div style={{ height: 5, background: "#e8e5df", borderRadius: 99, marginTop: "0.4rem" }}>
            <div style={{ height: "100%", borderRadius: 99, width: `${r2Pct}%`, background: r2Color }} />
          </div>
        </div>
      </div>

      {/* Tamaño del dataset */}
      <div style={{ display: "flex", gap: "1.5rem", marginBottom: "1rem", fontSize: "0.78rem", color: "#52525b" }}>
        <span>📊 {data.registros_totales.toLocaleString("es-CO")} registros EVA</span>
        <span>🎓 {data.registros_entrenamiento.toLocaleString("es-CO")} entrenamiento</span>
        <span>🧪 {data.registros_test.toLocaleString("es-CO")} prueba</span>
      </div>

      {/* Importancia de variables */}
      {features.length > 0 && (
        <div>
          <div style={{ fontSize: "0.72rem", color: "#a1a1aa", textTransform: "uppercase",
            letterSpacing: "0.07em", marginBottom: "0.6rem" }}>
            Variables más influyentes
          </div>
          {features.map(([key, value]) => (
            <div key={key} style={{ marginBottom: "0.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.2rem" }}>
                <span style={{ fontSize: "0.78rem", color: "#374151" }}>
                  {FEATURE_LABELS[key] ?? key}
                </span>
                <span style={{ fontSize: "0.78rem", fontWeight: 700, fontFamily: "monospace", color: "#16a34a" }}>
                  {safeFixed(value * 100, 1)}%
                </span>
              </div>
              <div style={{ height: 5, background: "#e8e5df", borderRadius: 99 }}>
                <div style={{ height: "100%", borderRadius: 99, width: `${value * 100}%`, background: "#16a34a" }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}