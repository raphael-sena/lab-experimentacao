import { useLayoutEffect, useRef, useState } from 'react'
import { quantiles } from '../../lib/stats'

/** Largura responsiva via ResizeObserver. */
function useWidth() {
  const ref = useRef(null)
  const [width, setWidth] = useState(640)
  useLayoutEffect(() => {
    if (!ref.current) return
    const el = ref.current
    const update = () => setWidth(el.clientWidth || 640)
    update()
    const ro = new ResizeObserver(update)
    ro.observe(el)
    return () => ro.disconnect()
  }, [])
  return [ref, width]
}

const niceTop = (max) => {
  if (max <= 0) return 1
  const pow = Math.pow(10, Math.floor(Math.log10(max)))
  const n = max / pow
  const step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10
  return step * pow
}

// Jitter determinístico (estável entre renders) para espalhar os pontos.
const jitter = (i, n) => (n <= 1 ? 0 : ((i / (n - 1)) - 0.5) * 0.55)

/**
 * Box plot (resumo de cinco números) com os pontos individuais sobrepostos.
 * Ideal para amostras pequenas e assimétricas: mostra a MEDIANA (tendência
 * central) e, ao mesmo tempo, cada observação real.
 *
 * @param {{label:string,color:string,values:number[]}[]} groups
 * @param {string} yLabel  rótulo do eixo Y (medida exata)
 * @param {(v:number)=>string} formatY
 */
export function BoxPlot({ groups, yLabel, formatY = (v) => `${v}`, height = 340 }) {
  const [ref, width] = useWidth()
  const m = { top: 16, right: 20, bottom: 52, left: 64 }
  const innerW = Math.max(width - m.left - m.right, 10)
  const innerH = height - m.top - m.bottom

  const allValues = groups.flatMap((g) => g.values)
  const dataMax = allValues.length ? Math.max(...allValues) : 1
  const top = niceTop(dataMax * 1.1)
  const y = (v) => m.top + innerH - (v / top) * innerH
  const bandW = innerW / groups.length
  const boxW = Math.min(bandW * 0.42, 90)

  const ticks = Array.from({ length: 5 }, (_, i) => (top * i) / 4)

  return (
    <div ref={ref} className="w-full">
      <svg width={width} height={height} role="img" aria-label={yLabel}>
        {/* rótulo do eixo Y */}
        <text
          transform={`translate(16, ${m.top + innerH / 2}) rotate(-90)`}
          textAnchor="middle"
          className="fill-slate-500"
          fontSize="12"
          fontWeight="500"
        >
          {yLabel}
        </text>

        {/* grade + ticks Y */}
        {ticks.map((t, i) => (
          <g key={i}>
            <line x1={m.left} x2={m.left + innerW} y1={y(t)} y2={y(t)} stroke="#e2e8f0" strokeDasharray="3 3" />
            <text x={m.left - 8} y={y(t)} dy="0.32em" textAnchor="end" className="fill-slate-400" fontSize="11">
              {formatY(t)}
            </text>
          </g>
        ))}

        {groups.map((g, gi) => {
          const cx = m.left + bandW * (gi + 0.5)
          const s = quantiles(g.values)
          if (!s.n) {
            return (
              <text key={g.label} x={cx} y={m.top + innerH / 2} textAnchor="middle" className="fill-slate-400" fontSize="12">
                sem dados
              </text>
            )
          }
          return (
            <g key={g.label}>
              {/* whisker (min–max) */}
              <line x1={cx} x2={cx} y1={y(s.min)} y2={y(s.max)} stroke={g.color} strokeWidth="1.5" />
              <line x1={cx - boxW / 4} x2={cx + boxW / 4} y1={y(s.max)} y2={y(s.max)} stroke={g.color} strokeWidth="1.5" />
              <line x1={cx - boxW / 4} x2={cx + boxW / 4} y1={y(s.min)} y2={y(s.min)} stroke={g.color} strokeWidth="1.5" />

              {/* caixa (Q1–Q3) */}
              <rect
                x={cx - boxW / 2}
                y={y(s.q3)}
                width={boxW}
                height={Math.max(y(s.q1) - y(s.q3), 1)}
                fill={g.color}
                fillOpacity="0.15"
                stroke={g.color}
                strokeWidth="1.5"
                rx="3"
              />
              {/* mediana (tendência central) */}
              <line x1={cx - boxW / 2} x2={cx + boxW / 2} y1={y(s.median)} y2={y(s.median)} stroke={g.color} strokeWidth="3" />

              {/* pontos individuais */}
              {g.values.map((v, i) => (
                <circle
                  key={i}
                  cx={cx + jitter(i, g.values.length) * boxW}
                  cy={y(v)}
                  r="3.5"
                  fill={g.color}
                  fillOpacity="0.55"
                  stroke="white"
                  strokeWidth="0.75"
                />
              ))}

              {/* rótulo X: grupo + n + mediana */}
              <text x={cx} y={height - 30} textAnchor="middle" className="fill-slate-700 dark:fill-slate-200" fontSize="13" fontWeight="600">
                {g.label}
              </text>
              <text x={cx} y={height - 14} textAnchor="middle" className="fill-slate-400" fontSize="11">
                n = {s.n} · mediana {formatY(s.median)}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
