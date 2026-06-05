import { useRqData } from '../../hooks/useRqData'
import { Card, Section } from '../ui/primitives'
import { RQ1Complexity } from './RQ1Complexity'
import { RQ2Smells } from './RQ2Smells'

/**
 * Seção da Sprint 2: Visualizações para as RQ1 e RQ2 (dimensão Q1 —
 * Manutenibilidade Estrutural), extraídas do artigo do estudo.
 *
 * @param {Array} stats  linhas de resultados_estatisticos.csv (estrato "all")
 */
export function ResearchQuestions({ stats }) {
  const rq = useRqData()
  const find = (metric) => stats?.find((r) => r.metric === metric)

  return (
    <Section
      id="rqs"
      title="Questões de Pesquisa — RQ1 e RQ2"
      subtitle="Dimensão Q1 (Manutenibilidade Estrutural). Cada pergunta exibe sua medida de tendência central e a comparação entre contribuições de IA autônoma (G1) e humanas (G2)."
    >
      {!rq ? (
        <Card className="p-6 text-sm text-slate-500">Carregando métricas das RQs…</Card>
      ) : (
        <div className="space-y-6">
          <RQ1Complexity data={rq.ccm} stat={find('ccm_mean')} />
          <RQ2Smells data={rq.smell} stat={find('design_smell_density')} />
        </div>
      )}
    </Section>
  )
}
