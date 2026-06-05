import { GROUPS } from '../../lib/constants'
import { formatDecimal, formatInt } from '../../lib/format'

export function GroupMedianCards({ g1, g2, unit }) {
  const items = [
    { meta: GROUPS.IA_autonomo, ...g1 },
    { meta: GROUPS.humano_confirmado, ...g2 },
  ]
  return (
    <div className="grid grid-cols-2 gap-3">
      {items.map(({ meta, median, n }) => (
        <div
          key={meta.key}
          className="rounded border border-slate-200 bg-white p-4"
          style={{ borderLeftColor: meta.color, borderLeftWidth: '3px' }}
        >
          <span className="text-xs font-medium text-slate-600">{meta.label}</span>
          <p className="mt-1.5 flex items-baseline gap-2">
            <span className="text-2xl font-bold tabular-nums text-slate-900">
              {formatDecimal(median)}
            </span>
            {unit && <span className="text-xs text-slate-400">{unit} (mediana)</span>}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">n = {formatInt(n)} PRs</p>
        </div>
      ))}
    </div>
  )
}
