import { Badge, Card } from '../ui/primitives'
import { formatDecimal2 } from '../../lib/format'

const effectColor = (label) =>
  ({ negligible: 'slate', small: 'slate', medium: 'amber', large: 'indigo' }[label] || 'slate')

function MetaItem({ label, children }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt>
      <dd className="mt-0.5 text-sm font-semibold text-slate-700">{children}</dd>
    </div>
  )
}

export function RQCard({ code, dimension, question, metric, centralTendency, test, stat, children, interpretation }) {
  return (
    <Card className="overflow-hidden">
      {/* Cabeçalho com a pergunta em destaque */}
      <div className="border-b border-slate-100 bg-slate-50 p-5">
        <div className="mb-2.5 flex flex-wrap items-center gap-2">
          <span className="rounded bg-slate-900 px-2 py-0.5 text-xs font-bold tracking-wide text-white">
            {code}
          </span>
          <Badge color="slate">{dimension}</Badge>
        </div>
        <h3 className="text-base font-semibold leading-snug text-slate-900">
          {question}
        </h3>
        <dl className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <MetaItem label="Métrica">{metric}</MetaItem>
          <MetaItem label="Tendência central">{centralTendency}</MetaItem>
          <MetaItem label="Teste estatístico">{test}</MetaItem>
          <MetaItem label="Decisão (α = 0,05)">
            <Badge color="slate">H0 não rejeitada</Badge>
          </MetaItem>
        </dl>
      </div>

      {/* Visualização */}
      <div className="p-5">{children}</div>

      {/* Veredito + interpretação */}
      <div className="border-t border-slate-100 bg-slate-50 px-5 py-4">
        {stat && (
          <div className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
            <span className="text-slate-600">
              <strong>p-valor</strong> = {formatDecimal2(stat.p_value)}
            </span>
            {stat.effect_label && (
              <span className="text-slate-600">
                <strong>Cliff's δ</strong> = {formatDecimal2(stat.effect_size)}{' '}
                <Badge color={effectColor(stat.effect_label)}>{stat.effect_label}</Badge>
              </span>
            )}
            <Badge color={stat.significant === 'yes' ? 'amber' : 'slate'}>
              {stat.significant === 'yes' ? 'p bruto < 0,05' : 'não significativo'}
            </Badge>
          </div>
        )}
        <p className="text-xs leading-relaxed text-slate-500">{interpretation}</p>
      </div>
    </Card>
  )
}
