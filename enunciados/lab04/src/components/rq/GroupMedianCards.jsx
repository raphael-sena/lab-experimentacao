import { GROUPS } from '../../lib/constants'
import { formatDecimal, formatInt } from '../../lib/format'

/** Dois cards lado a lado com a mediana (tendência central) de cada grupo. */
export function GroupMedianCards({ g1, g2, unit }) {
  const items = [
    { meta: GROUPS.IA_autonomo, ...g1 },
    { meta: GROUPS.humano_confirmado, ...g2 },
  ]
  return (
    <div className="grid grid-cols-2 gap-4">
      {items.map(({ meta, median, n }) => (
        <div
          key={meta.key}
          className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
        >
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: meta.color }} />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{meta.label}</span>
          </div>
          <p className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold tabular-nums text-slate-900 dark:text-slate-50">
              {formatDecimal(median)}
            </span>
            {unit && <span className="text-xs text-slate-400">{unit} (mediana)</span>}
          </p>
          <p className="mt-1 text-xs text-slate-400">n = {formatInt(n)} PRs</p>
        </div>
      ))}
    </div>
  )
}
