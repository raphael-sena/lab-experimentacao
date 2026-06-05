import { GROUPS } from '../../lib/constants'
import { formatDecimal } from '../../lib/format'
import { quantiles } from '../../lib/stats'
import { RQCard } from './RQCard'
import { BoxPlot } from './BoxPlot'
import { GroupMedianCards } from './GroupMedianCards'

/**
 * RQ01 — Manutenibilidade Estrutural: Complexidade Ciclomática (CCM).
 * Compara a CCM média por PR entre contribuições de IA (G1) e humanas (G2).
 */
export function RQ1Complexity({ data, stat }) {
  const g1 = quantiles(data?.G1 || [])
  const g2 = quantiles(data?.G2 || [])

  const groups = [
    { label: GROUPS.IA_autonomo.label, color: GROUPS.IA_autonomo.color, values: data?.G1 || [] },
    { label: GROUPS.humano_confirmado.label, color: GROUPS.humano_confirmado.color, values: data?.G2 || [] },
  ]

  return (
    <RQCard
      code="RQ01"
      dimension="Q1 · Manutenibilidade Estrutural"
      question="As contribuições geradas por agentes autônomos de IA apresentam complexidade ciclomática (CCM) diferente das contribuições humanas?"
      metric="ccm_mean (CCM média por PR)"
      centralTendency="Mediana"
      test="Mann-Whitney U"
      stat={stat}
      interpretation={`A mediana da CCM no grupo de IA (≈ ${formatDecimal(g1.median)}) é mais alta que a do grupo humano (≈ ${formatDecimal(
        g2.median,
      )}), com tamanho de efeito grande (Cliff's δ ≈ 0,71). Porém, com apenas n = ${g1.n} PRs analisáveis em G1, a diferença não sobrevive à correção para múltiplos testes — é um indício exploratório, não evidência robusta.`}
    >
      <GroupMedianCards
        g1={{ median: g1.median, n: g1.n }}
        g2={{ median: g2.median, n: g2.n }}
        unit="CCM"
      />
      <div className="mt-5">
        <BoxPlot
          groups={groups}
          yLabel="Complexidade ciclomática média (CCM) por PR"
          formatY={(v) => formatDecimal(v)}
        />
      </div>
    </RQCard>
  )
}
