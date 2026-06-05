import { Badge, Card } from './ui/primitives'
import { formatDecimal2 } from '../lib/format'
import { NUMERIC_METRICS } from '../lib/constants'

const METRIC_PT = Object.fromEntries(NUMERIC_METRICS.map((m) => [m.key, m.label]))
const prettyMetric = (k) =>
  METRIC_PT[k] ||
  ({
    has_review: 'Possui revisão',
    is_revert: 'É revert',
    language: 'Linguagem',
    ccm_mean: 'Complexidade ciclomática (média)',
    ccm_max: 'Complexidade ciclomática (máx.)',
    avg_func_length: 'Tamanho médio de função',
    long_line_ratio: 'Proporção de linhas longas',
    design_smell_density: 'Densidade de design smells',
    maintainability_index: 'Índice de manutenibilidade',
    smell_type: 'Tipo de smell',
  }[k] || k)

const effectColor = (label) =>
  ({ negligible: 'slate', small: 'slate', medium: 'amber', large: 'indigo' }[label] || 'slate')

/**
 * Tabela bônus: resultados dos testes (IA_autonomo vs. humano_confirmado)
 * no dataset completo. Caracteriza onde os subgrupos diferem.
 */
export function StatsTable({ rows }) {
  if (!rows) {
    return <Card className="p-5 text-sm text-slate-500">Carregando resultados estatísticos…</Card>
  }
  if (!rows.length) {
    return <Card className="p-5 text-sm text-slate-500">Resultados estatísticos indisponíveis.</Card>
  }
  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/80 dark:border-slate-800 dark:bg-slate-800/50">
              {['Métrica', 'Teste', 'Mediana IA', 'Mediana Humano', 'p-valor', 'Tam. efeito', 'Significância'].map(
                (h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                  >
                    {h}
                  </th>
                ),
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr
                key={i}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
              >
                <td className="px-4 py-2.5 font-medium text-slate-700 dark:text-slate-200">
                  {prettyMetric(r.metric)}
                </td>
                <td className="px-4 py-2.5 text-slate-500">{r.test}</td>
                <td className="px-4 py-2.5 tabular-nums text-slate-600 dark:text-slate-300">
                  {r.median_g1 == null ? '—' : formatDecimal2(r.median_g1)}
                </td>
                <td className="px-4 py-2.5 tabular-nums text-slate-600 dark:text-slate-300">
                  {r.median_g2 == null ? '—' : formatDecimal2(r.median_g2)}
                </td>
                <td className="px-4 py-2.5 tabular-nums text-slate-600 dark:text-slate-300">
                  {r.p_value == null ? '—' : formatDecimal2(r.p_value)}
                </td>
                <td className="px-4 py-2.5">
                  {r.effect_label ? <Badge color={effectColor(r.effect_label)}>{r.effect_label}</Badge> : '—'}
                </td>
                <td className="px-4 py-2.5">
                  <Badge color={r.significant === 'yes' ? 'amber' : 'slate'}>
                    {r.significant === 'yes' ? 'significativo' : 'n.s.'}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400 dark:border-slate-800">
        Testes não-paramétricos (Mann-Whitney U / Fisher / Qui-quadrado) no estrato completo.
        Atenção à forte assimetria amostral (n=9 vs. n≈202 mil): diferenças devem ser lidas com cautela.
      </p>
    </Card>
  )
}
