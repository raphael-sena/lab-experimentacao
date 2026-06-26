import { useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts'
import { API_COLORS, API_TYPES, ENDPOINT_LABEL } from '../lib/constants'
import { formatBytes, formatCompact, formatInt, formatMs } from '../lib/format'
import { useElementWidth } from '../hooks/useElementWidth'

const axisTick = { fontSize: 11, fill: '#a8a29e' }
const axisLine = { stroke: '#e7e5e4' }
const legendText = (value) => <span className="text-xs text-[var(--muted)]">{value}</span>
const visibleApis = (apiVisible) => API_TYPES.filter((a) => apiVisible[a])

function Sized({ height = 300, children }) {
  const [ref, width] = useElementWidth()
  return (
    <div ref={ref} className="w-full">
      {width > 0 && children(width, height)}
    </div>
  )
}

function TooltipBox({ active, payload, label, fmt = formatInt }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-md border bg-white px-3 py-2 text-xs shadow-sm" style={{ borderColor: 'var(--hairline)' }}>
      {label != null && <p className="mb-1 font-semibold text-[var(--ink)]">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="flex items-center gap-1.5 text-[var(--body)]">
          <span className="inline-block h-2 w-2 rounded-sm" style={{ background: p.color || p.fill }} />
          <span>{p.name}:</span>
          <span className="font-semibold tabular-nums">{fmt(p.value)}</span>
        </p>
      ))}
    </div>
  )
}

/** Barras agrupadas REST × GraphQL por endpoint, com hover cross-highlight. */
export function ApiComparisonBars({ cells, measure, stat = 'median', scale = 'linear', endpoints, apiVisible, height = 320 }) {
  const [hover, setHover] = useState(null)
  const data = endpoints.map((ep) => ({
    name: ep.label,
    REST: cells[ep.key].REST[measure][stat],
    GraphQL: cells[ep.key].GraphQL[measure][stat],
  }))
  const fmt = measure === 'size_bytes' ? formatBytes : formatMs
  const isLog = scale === 'log'
  const apis = visibleApis(apiVisible)
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={data} margin={{ left: 8, right: 8 }} barGap={4}>
          <CartesianGrid vertical={false} strokeDasharray="2 4" stroke="#eeece9" />
          <XAxis dataKey="name" tick={axisTick} axisLine={axisLine} tickLine={false} />
          <YAxis
            tickFormatter={measure === 'size_bytes' ? formatBytes : formatCompact}
            tick={axisTick}
            axisLine={false}
            tickLine={false}
            scale={isLog ? 'log' : 'auto'}
            domain={isLog ? [1, 'auto'] : [0, 'auto']}
            allowDataOverflow={isLog}
            width={64}
          />
          <Tooltip cursor={{ fill: 'rgba(28,25,23,0.04)' }} content={<TooltipBox fmt={fmt} />} />
          <Legend formatter={legendText} iconType="circle" iconSize={9} />
          {apis.map((api) => (
            <Bar key={api} dataKey={api} name={api} fill={API_COLORS[api]} radius={[3, 3, 0, 0]} isAnimationActive>
              {data.map((_, i) => (
                <Cell
                  key={i}
                  fillOpacity={hover === null || hover === i ? 1 : 0.28}
                  onMouseEnter={() => setHover(i)}
                  onMouseLeave={() => setHover(null)}
                />
              ))}
            </Bar>
          ))}
        </BarChart>
      )}
    </Sized>
  )
}

/** Tráfego total acumulado (bytes) por API — barra horizontal. */
export function TotalTrafficBars({ totalBytes, apiVisible, height = 150 }) {
  const data = visibleApis(apiVisible).map((api) => ({ name: api, value: totalBytes[api] }))
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={data} layout="vertical" margin={{ left: 4, right: 64 }}>
          <CartesianGrid horizontal={false} strokeDasharray="2 4" stroke="#eeece9" />
          <XAxis type="number" tickFormatter={formatBytes} tick={axisTick} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" width={68} tick={{ ...axisTick, fontWeight: 600, fill: '#57534e' }} axisLine={false} tickLine={false} />
          <Tooltip cursor={{ fill: 'rgba(28,25,23,0.04)' }} content={<TooltipBox fmt={formatBytes} />} />
          <Bar dataKey="value" name="Tráfego total" radius={[0, 4, 4, 0]} barSize={26} label={{ position: 'right', formatter: formatBytes, fontSize: 11, fill: '#57534e' }}>
            {data.map((d) => (
              <Cell key={d.name} fill={API_COLORS[d.name]} />
            ))}
          </Bar>
        </BarChart>
      )}
    </Sized>
  )
}

/** Histograma de latência por API (curvas de frequência). */
export function LatencyDistribution({ rows, apiVisible, bins = 18, height = 300 }) {
  const lat = rows.map((r) => r.latency_ms).filter(Number.isFinite)
  if (lat.length === 0) return null
  const min = Math.min(...lat)
  const max = Math.max(...lat)
  const width = (max - min) / bins || 1
  const data = Array.from({ length: bins }, (_, i) => ({
    center: min + (i + 0.5) * width,
    REST: 0,
    GraphQL: 0,
  }))
  for (const r of rows) {
    let idx = Math.floor((r.latency_ms - min) / width)
    if (idx >= bins) idx = bins - 1
    if (idx < 0) idx = 0
    data[idx][r.api_type] += 1
  }
  return (
    <Sized height={height}>
      {(w, h) => (
        <LineChart width={w} height={h} data={data} margin={{ left: 4, right: 8 }}>
          <CartesianGrid vertical={false} strokeDasharray="2 4" stroke="#eeece9" />
          <XAxis dataKey="center" type="number" domain={[min, max]} tickFormatter={(v) => Math.round(v)} tick={axisTick} axisLine={axisLine} tickLine={false} />
          <YAxis tickFormatter={formatCompact} tick={axisTick} axisLine={false} tickLine={false} width={36} />
          <Tooltip content={<TooltipBox label fmt={formatInt} />} labelFormatter={(v) => `≈ ${formatMs(v)}`} />
          <Legend formatter={legendText} iconType="plainline" iconSize={14} />
          {visibleApis(apiVisible).map((api) => (
            <Line key={api} type="monotone" dataKey={api} name={api} stroke={API_COLORS[api]} strokeWidth={2.2} dot={false} isAnimationActive />
          ))}
        </LineChart>
      )}
    </Sized>
  )
}

/** Dispersão latência × tamanho do payload, colorida por API (X em escala log). */
export function LatencySizeScatter({ rows, apiVisible, height = 320 }) {
  const series = visibleApis(apiVisible).map((api) => ({
    api,
    points: rows
      .filter((r) => r.api_type === api)
      .map((r) => ({ x: r.size_bytes, y: r.latency_ms, endpoint: ENDPOINT_LABEL[r.endpoint] })),
  }))
  return (
    <Sized height={height}>
      {(w, h) => (
        <ScatterChart width={w} height={h} margin={{ left: 8, right: 12, bottom: 10 }}>
          <CartesianGrid strokeDasharray="2 4" stroke="#eeece9" />
          <XAxis
            type="number"
            dataKey="x"
            name="Tamanho"
            scale="log"
            domain={[100, 'auto']}
            tickFormatter={formatBytes}
            tick={{ ...axisTick, fontSize: 10 }}
            axisLine={axisLine}
            tickLine={false}
            label={{ value: 'tamanho do payload (log)', position: 'insideBottom', offset: -4, fontSize: 10, fill: '#a8a29e' }}
          />
          <YAxis type="number" dataKey="y" name="Latência" tickFormatter={(v) => `${v}`} tick={axisTick} axisLine={false} tickLine={false} width={40} label={{ value: 'latência (ms)', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#a8a29e' }} />
          <ZAxis range={[30, 30]} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const p = payload[0].payload
              return (
                <div className="rounded-md border bg-white px-3 py-2 text-xs shadow-sm" style={{ borderColor: 'var(--hairline)' }}>
                  <p className="font-semibold text-[var(--ink)]">{p.endpoint}</p>
                  <p className="text-[var(--body)]">Latência: <span className="font-semibold">{formatMs(p.y)}</span></p>
                  <p className="text-[var(--body)]">Tamanho: <span className="font-semibold">{formatBytes(p.x)}</span></p>
                </div>
              )
            }}
          />
          <Legend formatter={legendText} iconType="circle" iconSize={9} />
          {series.map(({ api, points }) => (
            <Scatter key={api} name={api} data={points} fill={API_COLORS[api]} fillOpacity={0.5} />
          ))}
        </ScatterChart>
      )}
    </Sized>
  )
}
