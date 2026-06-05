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
const axisTick = { fontSize: 12, fill: '#64748b' }

/**
 * Wrapper que mede a largura e renderiza o gráfico com dimensões EXPLÍCITAS
 * (largura/altura em px), garantindo fidelidade na exportação em PDF.
 */
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
    <div className="rounded-lg border border-slate-200 bg-white/95 px-3 py-2 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-800/95">
      {label != null && <p className="mb-1 font-medium text-slate-700 dark:text-slate-200">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
          <span className="inline-block h-2 w-2 rounded-full" style={{ background: p.color || p.fill }} />
          <span>{p.name}:</span>
          <span className="font-semibold tabular-nums">{valueFmt(p.value)}{suffix}</span>
        </p>
      ))}
    </div>
  )
}

const legendText = (value) => <span className="text-xs text-slate-600 dark:text-slate-300">{value}</span>

/** Donut da distribuição de PRs por linguagem. */
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

/** Barras horizontais: nº de PRs por agente de IA (fingerprint). */
export function AgentBar({ data, height = 300 }) {
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
          <CartesianGrid horizontal={false} strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis type="number" tickFormatter={formatCompact} tick={axisTick} />
          <YAxis type="category" dataKey="name" width={92} tick={axisTick} />
          <Tooltip cursor={{ fill: '#f1f5f9' }} content={<TooltipBox valueFmt={formatInt} suffix=" PRs" />} />
          <Bar dataKey="count" name="PRs" radius={[0, 6, 6, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={AGENT_COLORS[d.name] || AGENT_COLORS.desconhecido} />
            ))}
          </Bar>
        </BarChart>
      )}
    </Sized>
  )
}

/** Barras agrupadas: mediana de uma métrica por linguagem. */
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
          <Tooltip cursor={{ fill: '#f1f5f9' }} content={<TooltipBox valueFmt={formatDecimal} />} />
          <Legend formatter={legendText} />
          <Bar dataKey="median" name={`Mediana — ${metricLabel(metricKey)}`} radius={[6, 6, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={LANGUAGE_COLORS[d.name] || LANGUAGE_COLORS.Outras} />
            ))}
          </Bar>
          <Bar dataKey="mean" name="Média" fill="#cbd5e1" radius={[6, 6, 0, 0]} />
        </BarChart>
      )}
    </Sized>
  )
}

/** Histograma de uma métrica (distribuição de forma). */
export function MetricHistogram({ bins, color = '#6366f1', suffix = ' PRs', height = 300 }) {
  return (
    <Sized height={height}>
      {(w, h) => (
        <BarChart width={w} height={h} data={bins} margin={{ left: 4, right: 8 }}>
          <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="label" tick={{ ...axisTick, fontSize: 11 }} interval={0} angle={-12} textAnchor="end" height={48} />
          <YAxis tickFormatter={formatCompact} tick={axisTick} />
          <Tooltip cursor={{ fill: '#f1f5f9' }} content={<TooltipBox valueFmt={formatInt} suffix={suffix} />} />
          <Bar dataKey="count" name="PRs" fill={color} radius={[6, 6, 0, 0]} />
        </BarChart>
      )}
    </Sized>
  )
}

/** Barras comparando os dois grupos do estudo numa métrica. */
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
          <Tooltip cursor={{ fill: '#f1f5f9' }} content={<TooltipBox valueFmt={formatDecimal} />} />
          <Bar dataKey="value" name={metricLabel(metricKey)} radius={[6, 6, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={d.color} />
            ))}
          </Bar>
        </BarChart>
      )}
    </Sized>
  )
}
