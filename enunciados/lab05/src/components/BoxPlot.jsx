import { useState } from 'react'
import { API_COLORS, API_TYPES } from '../lib/constants'
import { formatBytes, formatMs } from '../lib/format'
import { useElementWidth } from '../hooks/useElementWidth'

/**
 * Boxplot comparativo (mín · P25 · mediana · P75 · máx) em SVG puro, a partir
 * das estatísticas já calculadas em `cells`. Honra o filtro global (endpoints
 * e séries) e garante fidelidade total na exportação em PDF.
 */
export function BoxPlot({ cells, measure, scale = 'linear', endpoints, apiVisible, height = 360 }) {
  const [ref, width] = useElementWidth()
  const [hover, setHover] = useState(null)
  const fmt = measure === 'size_bytes' ? formatBytes : formatMs
  const isLog = scale === 'log'
  const apis = API_TYPES.filter((a) => apiVisible[a])

  const M = { top: 18, right: 16, bottom: 38, left: 66 }
  const innerW = Math.max(width - M.left - M.right, 10)
  const innerH = height - M.top - M.bottom

  let lo = Infinity
  let hi = -Infinity
  for (const ep of endpoints) {
    for (const api of apis) {
      const s = cells[ep.key][api][measure]
      if (Number.isFinite(s.min)) lo = Math.min(lo, s.min)
      if (Number.isFinite(s.max)) hi = Math.max(hi, s.max)
    }
  }
  if (!Number.isFinite(lo)) {
    lo = 0
    hi = 1
  }
  if (isLog) lo = Math.max(lo, 1)
  const pad = (hi - lo) * 0.06 || 1
  const dMin = isLog ? lo : Math.max(0, lo - pad)
  const dMax = hi + pad

  const y = (v) => {
    const clamped = isLog ? Math.max(v, 1) : v
    const t = isLog
      ? (Math.log10(clamped) - Math.log10(dMin)) / (Math.log10(dMax) - Math.log10(dMin))
      : (clamped - dMin) / (dMax - dMin)
    return M.top + innerH - t * innerH
  }

  const ticks = isLog ? logTicks(dMin, dMax) : linTicks(dMin, dMax, 5)
  const groupW = innerW / Math.max(endpoints.length, 1)
  const boxW = Math.min(groupW / (apis.length + 1.4), 48)

  return (
    <div ref={ref} className="w-full">
      {width > 0 && (
        <svg width={width} height={height} role="img">
          {ticks.map((t) => (
            <g key={t}>
              <line x1={M.left} x2={width - M.right} y1={y(t)} y2={y(t)} stroke="#eeece9" strokeDasharray="2 4" />
              <text x={M.left - 8} y={y(t)} textAnchor="end" dominantBaseline="middle" fontSize="10" fill="#a8a29e">
                {fmt(t)}
              </text>
            </g>
          ))}

          {endpoints.map((ep, gi) => {
            const gx = M.left + gi * groupW
            return (
              <g key={ep.key}>
                <text x={gx + groupW / 2} y={height - 12} textAnchor="middle" fontSize="11" fill="#57534e" fontWeight="600">
                  {ep.label}
                </text>
                {apis.map((api, ai) => {
                  const s = cells[ep.key][api][measure]
                  if (!Number.isFinite(s.median)) return null
                  const cx = gx + groupW / 2 + (ai - (apis.length - 1) / 2) * (boxW + 8)
                  const color = API_COLORS[api]
                  const isHover = hover && hover.ep === ep.key && hover.api === api
                  return (
                    <g
                      key={api}
                      onMouseEnter={() => setHover({ ep: ep.key, api, s, x: cx, label: ep.label })}
                      onMouseLeave={() => setHover(null)}
                      style={{ cursor: 'pointer' }}
                    >
                      <line x1={cx} x2={cx} y1={y(s.max)} y2={y(s.p75)} stroke={color} strokeWidth="1.5" />
                      <line x1={cx} x2={cx} y1={y(s.p25)} y2={y(s.min)} stroke={color} strokeWidth="1.5" />
                      <line x1={cx - boxW / 4} x2={cx + boxW / 4} y1={y(s.max)} y2={y(s.max)} stroke={color} strokeWidth="1.5" />
                      <line x1={cx - boxW / 4} x2={cx + boxW / 4} y1={y(s.min)} y2={y(s.min)} stroke={color} strokeWidth="1.5" />
                      <rect
                        x={cx - boxW / 2}
                        y={y(s.p75)}
                        width={boxW}
                        height={Math.max(y(s.p25) - y(s.p75), 1)}
                        fill={color}
                        fillOpacity={isHover ? 0.34 : 0.16}
                        stroke={color}
                        strokeWidth="1.5"
                        rx="2"
                      />
                      <line x1={cx - boxW / 2} x2={cx + boxW / 2} y1={y(s.median)} y2={y(s.median)} stroke={color} strokeWidth="2.5" />
                    </g>
                  )
                })}
              </g>
            )
          })}

          {hover && (
            <g pointerEvents="none">
              <rect x={Math.min(hover.x + 10, width - 150)} y={M.top} width="142" height="86" rx="6" fill="#fff" stroke="#e7e5e4" />
              <text x={Math.min(hover.x + 10, width - 150) + 9} y={M.top + 16} fontSize="10" fontWeight="700" fill={API_COLORS[hover.api]}>
                {hover.api} · {hover.label}
              </text>
              {[
                ['Máx', hover.s.max],
                ['P75', hover.s.p75],
                ['Mediana', hover.s.median],
                ['P25', hover.s.p25],
                ['Mín', hover.s.min],
              ].map(([k, v], i) => (
                <text key={k} x={Math.min(hover.x + 10, width - 150) + 9} y={M.top + 31 + i * 11} fontSize="9.5" fill="#57534e">
                  {k}: <tspan fontWeight="600">{fmt(v)}</tspan>
                </text>
              ))}
            </g>
          )}
        </svg>
      )}

      <div className="mt-1 flex items-center justify-center gap-4">
        {apis.map((api) => (
          <span key={api} className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
            <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: API_COLORS[api] }} />
            {api}
          </span>
        ))}
      </div>
    </div>
  )
}

function linTicks(min, max, n) {
  const step = (max - min) / n
  return Array.from({ length: n + 1 }, (_, i) => min + i * step)
}

function logTicks(min, max) {
  const out = []
  let e = Math.floor(Math.log10(min))
  const top = Math.ceil(Math.log10(max))
  for (; e <= top; e++) {
    const v = 10 ** e
    if (v >= min && v <= max) out.push(v)
  }
  return out.length ? out : [min, max]
}
