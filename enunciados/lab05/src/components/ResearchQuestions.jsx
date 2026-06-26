import { ALPHA } from '../lib/constants'
import { formatDecimal2, formatMeasure, formatPercent, formatPValue } from '../lib/format'
import { Badge, Card } from './ui/primitives'

const RQ_CONFIG = {
  latency_ms: {
    h0: 'H₀: latência(GraphQL) ≥ latência(REST)',
    h1: 'H₁: latência(GraphQL) < latência(REST)',
    winLabel: 'GraphQL mais rápido',
    failLabel: 'Sem evidência',
  },
  size_bytes: {
    h0: 'H₀: tamanho(GraphQL) ≥ tamanho(REST)',
    h1: 'H₁: tamanho(GraphQL) < tamanho(REST)',
    winLabel: 'GraphQL menor',
    failLabel: 'Sem evidência',
  },
}

function TestCard({ endpoint, measure, cells, test }) {
  const cfg = RQ_CONFIG[measure]
  const g = cells[endpoint.key].GraphQL[measure]
  const r = cells[endpoint.key].REST[measure]
  const win = test.significant
  return (
    <Card className="fade-up p-5" hover>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: endpoint.color }} />
          <h4 className="text-sm font-semibold text-[var(--ink)]">{endpoint.label}</h4>
        </div>
        <Badge color={win ? 'green' : 'amber'}>{win ? cfg.winLabel : cfg.failLabel}</Badge>
      </div>

      <div className="mt-4 flex items-end gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-[var(--faint)]">Redução (mediana)</p>
          <p className={'display text-3xl tabular-nums ' + (win ? 'text-emerald-700' : 'text-[var(--muted)]')}>
            {formatPercent(test.reduction)}
          </p>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-x-3 gap-y-2 border-t pt-3 text-sm" style={{ borderColor: 'var(--hairline)' }}>
        <Stat label="GraphQL" value={formatMeasure(measure, g.median)} color="#0F766E" />
        <Stat label="REST" value={formatMeasure(measure, r.median)} color="#C0392B" />
        <Stat label="Cliff's δ" value={`${formatDecimal2(test.delta)}`} sub={test.magnitude} />
        <Stat label="p-valor" value={formatPValue(test.p)} sub={win ? 'rejeita H₀' : 'não rejeita H₀'} subColor={win ? '#047857' : '#b45309'} />
      </div>
    </Card>
  )
}

function Stat({ label, value, sub, color, subColor }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-wide text-[var(--faint)]">{label}</p>
      <p className="font-semibold tabular-nums" style={{ color: color || 'var(--ink)' }}>{value}</p>
      {sub && <p className="text-[11px]" style={{ color: subColor || 'var(--faint)' }}>{sub}</p>}
    </div>
  )
}

/** Bloco de cartões de teste de hipótese para uma medida, filtrado por endpoint. */
export function RQTestCards({ measure, cells, tests, endpoints }) {
  const cfg = RQ_CONFIG[measure]
  return (
    <div>
      <Card className="mb-4 bg-[var(--paper-2)] px-4 py-3" style={{ borderColor: 'var(--hairline)' }}>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-xs text-[var(--muted)]">
          <span className="font-mono">{cfg.h0}</span>
          <span className="font-mono">{cfg.h1}</span>
          <span className="text-[var(--faint)]">Mann-Whitney U unilateral · α = {ALPHA}</span>
        </div>
      </Card>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {endpoints.map((ep) => (
          <TestCard key={ep.key} endpoint={ep} measure={measure} cells={cells} test={tests[ep.key][measure]} />
        ))}
      </div>
    </div>
  )
}
