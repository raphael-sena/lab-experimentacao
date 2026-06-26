import { API_COLORS, API_TYPES } from '../lib/constants'
import { formatBytes, formatInt, formatMs } from '../lib/format'
import { Card } from './ui/primitives'

/** Tabela de estatísticas descritivas por endpoint × API, para a medida ativa. */
export function EndpointTable({ cells, measure, endpoints }) {
  const isSize = measure === 'size_bytes'
  const fmt = isSize ? formatBytes : formatMs
  const cols = [
    ['N', (s) => formatInt(s.n)],
    ['Média', (s) => fmt(s.mean)],
    ['Mediana', (s) => fmt(s.median)],
    ['Desv. padrão', (s) => fmt(s.std)],
    ['Mín', (s) => fmt(s.min)],
    ['Máx', (s) => fmt(s.max)],
    ...(isSize ? [['Total', (s) => formatBytes(s.total)]] : []),
  ]
  return (
    <Card className="overflow-x-auto p-0">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-[11px] uppercase tracking-[0.1em] text-[var(--faint)]" style={{ borderColor: 'var(--hairline)' }}>
            <th className="px-5 py-3 font-semibold">Endpoint</th>
            <th className="px-5 py-3 font-semibold">API</th>
            {cols.map(([h]) => (
              <th key={h} className="px-5 py-3 text-right font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {endpoints.map((ep) =>
            API_TYPES.map((api, ai) => {
              const s = cells[ep.key][api][measure]
              const lastOfGroup = ai === API_TYPES.length - 1
              return (
                <tr
                  key={ep.key + api}
                  className="transition-colors hover:bg-[var(--paper-2)]"
                  style={lastOfGroup ? { borderBottom: '1px solid var(--hairline)' } : undefined}
                >
                  {ai === 0 && (
                    <td rowSpan={API_TYPES.length} className="px-5 py-3 align-middle font-medium text-[var(--ink)]">
                      <span className="inline-flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full" style={{ background: ep.color }} />
                        {ep.label}
                      </span>
                    </td>
                  )}
                  <td className="px-5 py-3">
                    <span className="inline-flex items-center gap-1.5 font-medium" style={{ color: API_COLORS[api] }}>
                      <span className="h-2 w-2 rounded-full" style={{ background: API_COLORS[api] }} />
                      {api}
                    </span>
                  </td>
                  {cols.map(([h, get]) => (
                    <td key={h} className="px-5 py-3 text-right tabular-nums text-[var(--body)]">{get(s)}</td>
                  ))}
                </tr>
              )
            }),
          )}
        </tbody>
      </table>
    </Card>
  )
}
