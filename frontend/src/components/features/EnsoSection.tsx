'use client';

import { useEnsoData } from '@/hooks/useEnsoData';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts';

const FASE_ICON: Record<string, string> = {
  'El Nino': '☀️',
  'La Nina': '🌊',
  Neutro: '🌤️',
};

const INTENSIDAD_LABEL: Record<string, string> = {
  muy_fuerte: 'Muy fuerte',
  fuerte: 'Fuerte',
  moderado: 'Moderado',
  debil: 'Débil',
  neutro: 'Neutro',
};

const TENDENCIA_ICON: Record<string, string> = {
  intensificando: '↑',
  debilitando: '↓',
  estable: '→',
};

export function EnsoSection() {
  const { data, loading, error } = useEnsoData();

  if (loading) {
    return (
      <Card>
        <div style={{ padding: '3rem', textAlign: 'center', color: '#a1a1aa' }}>
          Conectando con NOAA/CPC...
        </div>
      </Card>
    );
  }

  if (error || !data?.success) {
    return (
      <Card>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠️</div>
          <div style={{ fontSize: '0.85rem', color: '#ef4444' }}>
            Error al conectar con NOAA: {error ?? 'Sin datos'}
          </div>
        </div>
      </Card>
    );
  }

  const {
    estado_actual: e,
    probabilidades: p,
    impacto_colombia: imp,
    historico_oni: hist,
  } = data;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* ── Estado actual ── */}
      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}
      >
        {/* Card principal ENSO */}
        <Card>
          <SectionHeader
            title="Monitor ENSO"
            sub="Oceanic Niño Index · NOAA/CPC · Tiempo real"
            badge="NOAA"
          />
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1.5rem',
              marginTop: '1rem',
            }}
          >
            <div style={{ fontSize: '3.5rem' }}>
              {FASE_ICON[e.fase] ?? '🌤️'}
            </div>
            <div>
              <div
                style={{
                  fontSize: '1.6rem',
                  fontWeight: 800,
                  color: e.color,
                  lineHeight: 1,
                }}
              >
                {e.fase}
              </div>
              <div
                style={{
                  fontSize: '0.82rem',
                  color: '#71717a',
                  marginTop: '0.25rem',
                }}
              >
                {INTENSIDAD_LABEL[e.intensidad]} · {e.season} {e.anio}
              </div>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  marginTop: '0.5rem',
                  fontSize: '0.78rem',
                  color:
                    e.tendencia === 'intensificando'
                      ? '#ef4444'
                      : e.tendencia === 'debilitando'
                        ? '#16a34a'
                        : '#71717a',
                }}
              >
                <span style={{ fontSize: '1rem' }}>
                  {TENDENCIA_ICON[e.tendencia]}
                </span>
                Tendencia: {e.tendencia}
              </div>
            </div>
          </div>

          {/* ONI badge */}
          <div
            style={{
              marginTop: '1.25rem',
              display: 'inline-flex',
              alignItems: 'baseline',
              gap: '0.4rem',
            }}
          >
            <span
              style={{
                fontSize: '0.72rem',
                color: '#a1a1aa',
                fontFamily: 'monospace',
              }}
            >
              ONI Index
            </span>
            <span
              style={{
                fontSize: '2rem',
                fontWeight: 700,
                fontFamily: 'monospace',
                color:
                  e.oni_index > 0
                    ? '#ef4444'
                    : e.oni_index < 0
                      ? '#3b82f6'
                      : '#16a34a',
              }}
            >
              {e.oni_index > 0 ? '+' : ''}
              {e.oni_index.toFixed(2)}
            </span>
            <span style={{ fontSize: '0.72rem', color: '#a1a1aa' }}>°C</span>
          </div>
        </Card>

        {/* Probabilidades */}
        <Card>
          <div
            style={{
              fontSize: '0.78rem',
              fontWeight: 600,
              color: '#a1a1aa',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: '1rem',
            }}
          >
            Probabilidades próx. trimestre
          </div>
          {[
            {
              label: 'El Niño',
              value: p.el_nino,
              color: '#ef4444',
              icon: '☀️',
            },
            { label: 'Neutro', value: p.neutro, color: '#16a34a', icon: '🌤️' },
            {
              label: 'La Niña',
              value: p.la_nina,
              color: '#3b82f6',
              icon: '🌊',
            },
          ].map((item) => (
            <div key={item.label} style={{ marginBottom: '0.75rem' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '0.3rem',
                }}
              >
                <span
                  style={{
                    fontSize: '0.82rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                  }}
                >
                  {item.icon} {item.label}
                </span>
                <span
                  style={{
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    fontFamily: 'monospace',
                    color: item.color,
                  }}
                >
                  {item.value}%
                </span>
              </div>
              <div
                style={{ height: 6, background: '#f0ede8', borderRadius: 99 }}
              >
                <div
                  style={{
                    height: '100%',
                    borderRadius: 99,
                    width: `${item.value}%`,
                    background: item.color,
                    transition: 'width 0.6s ease',
                  }}
                />
              </div>
            </div>
          ))}
        </Card>
      </div>

      {/* ── Impacto Colombia ── */}
      <Card>
        <div
          style={{
            fontSize: '0.78rem',
            fontWeight: 600,
            color: '#a1a1aa',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '0.75rem',
          }}
        >
          Impacto esperado en Colombia
        </div>
        <div
          style={{
            background: '#fffbeb',
            border: '1px solid #fde68a',
            borderLeft: `4px solid ${e.color}`,
            borderRadius: 10,
            padding: '1rem 1.25rem',
            marginBottom: '1rem',
          }}
        >
          <div
            style={{
              fontSize: '0.9rem',
              fontWeight: 600,
              marginBottom: '0.25rem',
            }}
          >
            {imp.alerta}
          </div>
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '0.75rem',
          }}
        >
          {[
            { icon: '🌧️', label: 'Precipitación', value: imp.precipitacion },
            { icon: '🌡️', label: 'Temperatura', value: imp.temperatura },
            { icon: '🌵', label: 'Riesgo sequía', value: imp.riesgo_sequia },
            {
              icon: '🌊',
              label: 'Riesgo inund.',
              value: imp.riesgo_inundacion,
            },
          ].map((m) => (
            <div
              key={m.label}
              style={{
                background: '#fafafa',
                border: '1px solid #f0ede8',
                borderRadius: 8,
                padding: '0.75rem',
              }}
            >
              <div
                style={{
                  fontSize: '0.72rem',
                  color: '#a1a1aa',
                  marginBottom: '0.2rem',
                }}
              >
                {m.icon} {m.label}
              </div>
              <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>
                {m.value}
              </div>
            </div>
          ))}
        </div>
        <div
          style={{
            marginTop: '0.75rem',
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: 8,
            padding: '0.75rem 1rem',
            fontSize: '0.82rem',
            color: '#166534',
          }}
        >
          💡 {imp.recomendacion}
        </div>
        {imp.cultivos_riesgo.length > 0 && (
          <div
            style={{
              display: 'flex',
              gap: '0.35rem',
              flexWrap: 'wrap',
              marginTop: '0.75rem',
            }}
          >
            <span style={{ fontSize: '0.72rem', color: '#a1a1aa' }}>
              Cultivos en riesgo:
            </span>
            {imp.cultivos_riesgo.map((c) => (
              <span
                key={c}
                style={{
                  background: '#fef3c7',
                  border: '1px solid #fde68a',
                  borderRadius: '100px',
                  padding: '0.15rem 0.6rem',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                }}
              >
                🌾 {c}
              </span>
            ))}
          </div>
        )}
      </Card>

      {/* ── Gráfica ONI histórico ── */}
      {hist.length > 0 && (
        <Card>
          <SectionHeader
            title="Índice ONI histórico"
            sub="Últimos 3 años · NOAA/CPC"
            badge="ONI"
          />
          <div style={{ height: 220, marginTop: '1rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={hist}
                margin={{ top: 5, right: 10, left: -20, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="oniPos" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="oniNeg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0ede8" />
                <XAxis
                  dataKey="season"
                  tick={{ fontSize: 10, fontFamily: 'monospace' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  domain={[-3, 3]}
                />
                <Tooltip
                  formatter={(v) => {
                    const value = Number(v ?? 0);
                    return [
                      `${value > 0 ? '+' : ''}${value.toFixed(2)}°C`,
                      'ONI',
                    ];
                  }}
                />
                <ReferenceLine
                  y={0.5}
                  stroke="#ef4444"
                  strokeDasharray="4 3"
                  strokeWidth={1}
                  label={{
                    value: 'El Niño',
                    position: 'right',
                    fontSize: 9,
                    fill: '#ef4444',
                  }}
                />
                <ReferenceLine
                  y={-0.5}
                  stroke="#3b82f6"
                  strokeDasharray="4 3"
                  strokeWidth={1}
                  label={{
                    value: 'La Niña',
                    position: 'right',
                    fontSize: 9,
                    fill: '#3b82f6',
                  }}
                />
                <ReferenceLine y={0} stroke="#d1d5db" strokeWidth={1} />
                <Area
                  type="monotone"
                  dataKey="oni_index"
                  stroke={e.color}
                  strokeWidth={2}
                  fill={e.oni_index >= 0 ? 'url(#oniPos)' : 'url(#oniNeg)'}
                  dot={{ r: 3, fill: e.color }}
                  activeDot={{ r: 5 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}
    </div>
  );
}
