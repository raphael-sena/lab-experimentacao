import { CENTRAL_TENDENCY_KEYS, NUMERIC_METRICS } from '../lib/constants'
import { Card } from './ui/primitives'
import { formatMetric } from '../lib/format'

const META = Object.fromEntries(NUMERIC_METRICS.map((m) => [m.key, m]))

/**
 * Grade de cards de tendência central (mediana destacada + média e IQR)
 * para as principais métricas do dataset completo.
 */
export function CentralTendency({ overall }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {CENTRAL_TENDENCY_KEYS.map((key) => {
        const s = overall.metrics[key] || {}
        const meta = META[key]
        return (
          <Card key={key} className="p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{meta.label}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-bold tabular-nums text-slate-900 dark:text-slate-50">
                {formatMetric(key, s.median)}
              </span>
              <span className="text-xs text-slate-400">mediana</span>
            </div>
            <dl className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
              <div className="rounded-lg bg-slate-50 py-1.5 dark:bg-slate-800/60">
                <dt className="text-slate-400">média</dt>
                <dd className="font-semibold tabular-nums text-slate-700 dark:text-slate-200">
                  {formatMetric(key, s.mean)}
                </dd>
              </div>
              <div className="rounded-lg bg-slate-50 py-1.5 dark:bg-slate-800/60">
                <dt className="text-slate-400">P25</dt>
                <dd className="font-semibold tabular-nums text-slate-700 dark:text-slate-200">
                  {formatMetric(key, s.p25)}
                </dd>
              </div>
              <div className="rounded-lg bg-slate-50 py-1.5 dark:bg-slate-800/60">
                <dt className="text-slate-400">P75</dt>
                <dd className="font-semibold tabular-nums text-slate-700 dark:text-slate-200">
                  {formatMetric(key, s.p75)}
                </dd>
              </div>
            </dl>
          </Card>
        )
      })}
    </div>
  )
}
