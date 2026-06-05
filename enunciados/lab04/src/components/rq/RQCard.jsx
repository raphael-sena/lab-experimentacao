import { Badge, Card } from '../ui/primitives'
import { formatDecimal2 } from '../../lib/format'

const effectColor = (label) =>
  ({ negligible: 'slate', small: 'slate', medium: 'amber', large: 'indigo' }[label] || 'slate')

function MetaItem({ label, children }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt>
      <dd className="mt-0.5 text-sm font-semibold text-slate-700 dark:text-slate-200">{children}</dd>
    </div>
  )
}

/**
 * Layout auto-explicativo de uma Questão de Pesquisa: o texto EXATO da
 * pergunta em destaque e, abaixo, a(s) visualização(ões) e o veredito do teste.
 */
export function RQCard({ code, dimension, question, metric, centralTendency, test, stat, children, interpretation }) {
  return (
    <Card className="overflow-hidden">
      {/* Cabeçalho com a pergunta em destaque */}
      <div className="border-b border-slate-100 bg-gradient-to-br from-indigo-50/80 to-transparent p-6 dark:border-slate-800 dark:from-indigo-950/30">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <span className="rounded-lg bg-indigo-600 px-2.5 py-1 text-xs font-bold tracking-wide text-white">
            {code}
          </span>
          <Badge color="indigo">{dimension}</Badge>
        </div>
        <h3 className="text-lg font-semibold leading-snug text-slate-900 dark:text-slate-50 sm:text-xl">
          {question}
        </h3>
        <dl className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <MetaItem label="Métrica">{metric}</MetaItem>
          <MetaItem label="Tendência central">{centralTendency}</MetaItem>
          <MetaItem label="Teste estatístico">{test}</MetaItem>
          <MetaItem label="Decisão (α = 0,05)">
            <Badge color="slate">H0 não rejeitada</Badge>
          </MetaItem>
        </dl>
      </div>

      {/* Visualização */}
      <div className="p-6">{children}</div>

      {/* Veredito + interpretação */}
      <div className="border-t border-slate-100 bg-slate-50/60 px-6 py-4 dark:border-slate-800 dark:bg-slate-800/30">
        {stat && (
          <div className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
            <span className="text-slate-600 dark:text-slate-300">
              <strong>p-valor</strong> = {formatDecimal2(stat.p_value)}
            </span>
            {stat.effect_label && (
              <span className="text-slate-600 dark:text-slate-300">
                <strong>Cliff's δ</strong> = {formatDecimal2(stat.effect_size)}{' '}
                <Badge color={effectColor(stat.effect_label)}>{stat.effect_label}</Badge>
              </span>
            )}
            <Badge color={stat.significant === 'yes' ? 'amber' : 'slate'}>
              {stat.significant === 'yes' ? 'p bruto < 0,05' : 'não significativo'}
            </Badge>
          </div>
        )}
        <p className="text-sm leading-relaxed text-slate-500 dark:text-slate-400">{interpretation}</p>
      </div>
    </Card>
  )
}
