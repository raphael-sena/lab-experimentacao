import { SAMPLE_COLUMNS, GROUPS } from '../lib/constants'
import { Badge, Card } from './ui/primitives'

/** Amostra dos dados brutos do CSV (primeiras linhas), para inspeção. */
export function SampleTable({ rows }) {
  if (!rows?.length) return null
  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/80 dark:border-slate-800 dark:bg-slate-800/50">
              {SAMPLE_COLUMNS.map((c) => (
                <th
                  key={c.key}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
              >
                {SAMPLE_COLUMNS.map((c) => (
                  <td key={c.key} className="whitespace-nowrap px-4 py-2.5 text-slate-700 dark:text-slate-300">
                    {c.key === 'group_label' ? (
                      <Badge color={row[c.key] === 'IA_autonomo' ? 'indigo' : 'green'}>
                        {GROUPS[row[c.key]]?.label || row[c.key]}
                      </Badge>
                    ) : c.key === 'repository' ? (
                      <span className="font-mono text-xs">{row[c.key]}</span>
                    ) : (
                      row[c.key] ?? '—'
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
