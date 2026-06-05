import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { AGENT_COLORS, GROUPS, LANGUAGE_COLORS, NUMERIC_METRICS } from '../lib/constants'
import { formatCompact, formatInt, formatDecimal } from '../lib/format'
import { useElementWidth } from '../hooks/useElementWidth'

const metricLabel = (key) => NUMERIC_METRICS.find((m) => m.key === key)?.label || key
const axisTick = { fontSize: 11, fill: '#64748b' }

function Sized({ height = 300, children }) {
  const [ref, width] = useElementWidth()
  return (
    <div ref={ref} className="w-full">
      {width > 0 && children(width, height)}
    </div>
  )
}

function TooltipBox({ active, payload, label, valueFmt = formatInt, suffix = '' }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded border border-slate-200 bg-white px-3 py-2 text-xs shadow">
      {label != null && <p className="mb-1 font-medium text-slate-700">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="flex items-center gap-1.5 text-slate-600">
          <span className="inline-block h-2 w-2 rounded-sm" style={{ background: p.color || p.fill }} />
          <span>{p.name}:</span>
          <span className="font-semibold tabular-nums">{valueFmt(p.value)}{suffix}</span>
        </p>
      ))}
    </div>
  )
}

const legendText = (value) => <span className="text-xs text-slate-500">{value}</span>

export function LanguageDonut({ data, height = 300 }) {
  const total = data.reduce((s, d) => s + d.count, 0)
  return (
    <Sized height={height}>
      {(w, h) => (
        <PieChart width={w} height={h}>
          <Pie data={data} dataKey="count" nameKey="name" innerRadius="55%" outerRadius="80%" paddingAngle={2} stroke="none">
            {data.map((d) => (
              <Cell key={d.name} fill={LANGUAGE_COLORS[d.name] || LANGUAGE_COLORS.Outras} />
            ))}
          </Pie>
          <Tooltip content={<TooltipBox valueFmt={(v) => `${formatInt(v)} PRs (${((v / total) * 100).toFixed(1)}%)`} />} />
          <Legend verticalAlign="bottom" height={36} formatter={legendText} />
        </PieChart>
      )}
    </Sized>
  )
}

export function AgentBar({ data, height = 300 }) {
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
          <CartesianGrid horizontal={false} strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis type="number" tickFormatter={formatCompact} tick={axisTick} />
          <YAxis type="category" dataKey="name" width={92} tick={axisTick} />
          <Tooltip cursor={{ fill: '#f8fafc' }} content={<TooltipBox valueFmt={formatInt} suffix=" PRs" />} />
          <Bar dataKey="count" name="PRs" radius={[0, 2, 2, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={AGENT_COLORS[d.name] || AGENT_COLORS.desconhecido} />
            ))}
          </Bar>
        </BarChart>
      )}
    </Sized>
  )
}

export function MedianByLanguage({ byLanguage, metricKey, height = 340 }) {
  const data = Object.entries(byLanguage).map(([name, scope]) => ({
    name,
    median: scope.metrics[metricKey]?.median ?? 0,
    mean: scope.metrics[metricKey]?.mean ?? 0,
  }))
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={data} margin={{ left: 4, right: 8 }}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="name" tick={axisTick} />
          <YAxis tickFormatter={formatCompact} tick={axisTick} />
          <Tooltip cursor={{ fill: '#f8fafc' }} content={<TooltipBox valueFmt={formatDecimal} />} />
          <Legend formatter={legendText} />
          <Bar dataKey="median" name={`Mediana — ${metricLabel(metricKey)}`} radius={[2, 2, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={LANGUAGE_COLORS[d.name] || LANGUAGE_COLORS.Outras} />
            ))}
          </Bar>
          <Bar dataKey="mean" name="Média" fill="#cbd5e1" radius={[2, 2, 0, 0]} />
        </BarChart>
      )}
    </Sized>
  )
}

export function MetricHistogram({ bins, color = '#1d4ed8', suffix = ' PRs', height = 300 }) {
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={bins} margin={{ left: 4, right: 8 }}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="label" tick={{ ...axisTick, fontSize: 10 }} interval={0} angle={-12} textAnchor="end" height={48} />
          <YAxis tickFormatter={formatCompact} tick={axisTick} />
          <Tooltip cursor={{ fill: '#f8fafc' }} content={<TooltipBox valueFmt={formatInt} suffix={suffix} />} />
          <Bar dataKey="count" name="PRs" fill={color} radius={[2, 2, 0, 0]} />
        </BarChart>
      )}
    </Sized>
  )
}

export function GroupComparison({ byGroup, metricKey, statistic = 'median', height = 300 }) {
  const data = Object.entries(GROUPS)
    .filter(([key]) => byGroup[key])
    .map(([key, meta]) => ({
      name: meta.label,
      value: byGroup[key].metrics[metricKey]?.[statistic] ?? 0,
      color: meta.color,
    }))
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={data} margin={{ left: 4, right: 8 }}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="name" tick={axisTick} />
          <YAxis tickFormatter={formatCompact} tick={axisTick} />
          <Tooltip cursor={{ fill: '#f8fafc' }} content={<TooltipBox valueFmt={formatDecimal} />} />
          <Bar dataKey="value" name={metricLabel(metricKey)} radius={[2, 2, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={d.color} />
            ))}
          </Bar>
        </BarChart>
      )}
    </Sized>
  )
}
