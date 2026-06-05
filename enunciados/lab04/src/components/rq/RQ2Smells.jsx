import { GROUPS } from '../../lib/constants'
import { formatDecimal2, formatInt } from '../../lib/format'
import { quantiles } from '../../lib/stats'
import { RQCard } from './RQCard'
import { BoxPlot } from './BoxPlot'
import { GroupMedianCards } from './GroupMedianCards'

/**
 * RQ02 — Manutenibilidade Estrutural: Densidade de Code Smells / KLoC.
 * Compara a densidade de smells de design (proxy via Lizard) entre IA e humanos.
 */
export function RQ2Smells({ data, stat }) {
  const g1 = quantiles(data?.G1 || [])
  const g2 = quantiles(data?.G2 || [])

  const groups = [
    { label: GROUPS.IA_autonomo.label, color: GROUPS.IA_autonomo.color, values: data?.G1 || [] },
    { label: GROUPS.humano_confirmado.label, color: GROUPS.humano_confirmado.color, values: data?.G2 || [] },
  ]

  const g1Outliers = (data?.G1 || []).filter((v) => v > 0).length
  const g2Outliers = (data?.G2 || []).filter((v) => v > 0).length

  return (
    <RQCard
      code="RQ02"
      dimension="Q1 · Manutenibilidade Estrutural"
      question="As contribuições geradas por agentes autônomos de IA apresentam densidade de code smells (por KLoC) diferente das contribuições humanas?"
      metric="design_smell_density (smells de design / KLoC)"
      centralTendency="Mediana"
      test="Mann-Whitney U"
      stat={stat}
      interpretation={`A mediana da densidade de smells é zero nos dois grupos: a maioria dos PRs não apresenta smells de design. As poucas observações positivas (${g1Outliers} em IA, ${g2Outliers} em Humano) são outliers que não alteram a tendência central. O teste não indica diferença significativa (δ negligível). Observação metodológica: ESLint/Pylint não foram executados; a densidade é uma proxy do Lizard (funções longas, NLOC > 50, por KLoC).`}
    >
      <GroupMedianCards
        g1={{ median: g1.median, n: g1.n }}
        g2={{ median: g2.median, n: g2.n }}
        unit="smells/KLoC"
      />
      <div className="mt-5">
        <BoxPlot
          groups={groups}
          yLabel="Densidade de smells de design (por KLoC) por PR"
          formatY={(v) => formatDecimal2(v)}
        />
      </div>
      <p className="mt-3 text-xs text-slate-400">
        Mediana = 0 em ambos os grupos · {formatInt(g1Outliers + g2Outliers)} PRs com densidade &gt; 0 (outliers).
      </p>
    </RQCard>
  )
}
