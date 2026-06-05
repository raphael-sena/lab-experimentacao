import { CENTRAL_TENDENCY_KEYS, NUMERIC_METRICS } from '../lib/constants'
import { Card } from './ui/primitives'
import { formatMetric } from '../lib/format'

const META = Object.fromEntries(NUMERIC_METRICS.map((m) => [m.key, m]))

export function CentralTendency({ overall }) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {CENTRAL_TENDENCY_KEYS.map((key) => {
        const s = overall.metrics[key] || {}
        const meta = META[key]
        return (
          <Card key={key} className="p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{meta.label}</p>
            <div className="mt-1.5 flex items-baseline gap-2">
              <span className="text-2xl font-bold tabular-nums text-slate-900">
                {formatMetric(key, s.median)}
              </span>
              <span className="text-xs text-slate-400">mediana</span>
            </div>
            <dl className="mt-3 grid grid-cols-3 gap-1.5 text-center text-xs">
              <div className="rounded bg-slate-50 py-1.5">
                <dt className="text-slate-400">média</dt>
                <dd className="font-semibold tabular-nums text-slate-700">
                  {formatMetric(key, s.mean)}
                </dd>
              </div>
              <div className="rounded bg-slate-50 py-1.5">
                <dt className="text-slate-400">P25</dt>
                <dd className="font-semibold tabular-nums text-slate-700">
                  {formatMetric(key, s.p25)}
                </dd>
              </div>
              <div className="rounded bg-slate-50 py-1.5">
                <dt className="text-slate-400">P75</dt>
                <dd className="font-semibold tabular-nums text-slate-700">
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
