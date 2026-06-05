import { useState } from 'react'
import { useDataset } from './hooks/useDataset'
import { useStats } from './hooks/useStats'
import { GROUPS, NUMERIC_METRICS } from './lib/constants'
import { formatInt, formatPercent, formatDecimal } from './lib/format'
import { Header } from './components/Header'
import { ResearchQuestions } from './components/rq/ResearchQuestions'
import { CentralTendency } from './components/CentralTendency'
import { Card, ChartFrame, KpiCard, Loader, Section } from './components/ui/primitives'
import {
  AgentBar,
  GroupComparison,
  LanguageDonut,
  MedianByLanguage,
  MetricHistogram,
} from './components/charts'

const metricLabel = (k) => NUMERIC_METRICS.find((m) => m.key === k)?.label || k

const COMPARISON_OPTIONS = NUMERIC_METRICS.filter((m) => m.key !== 'test_file_ratio').map((m) => m.key)

function MetricSelect({ value, onChange, options = COMPARISON_OPTIONS }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="no-print rounded border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 outline-none focus:border-slate-500"
    >
      {options.map((k) => (
        <option key={k} value={k}>
          {metricLabel(k)}
        </option>
      ))}
    </select>
  )
}

export default function App() {
  const { status, processed, summary, error } = useDataset()
  const stats = useStats()
  const [langMetric, setLangMetric] = useState('diff_lines')
  const [groupMetric, setGroupMetric] = useState('diff_lines')

  if (!summary) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header status={status} />
        <Loader processed={processed} />
      </div>
    )
  }

  const langCount = summary.languages.length
  const agentCount = summary.agents.filter((a) => a.name !== 'desconhecido').length
  const iaGroup = summary.groups.find((g) => g.name === 'IA_autonomo')?.count ?? 0
  const humanGroup = summary.groups.find((g) => g.name === 'humano_confirmado')?.count ?? 0

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 print:bg-white">
      <Header status={status} onPrint={() => window.print()} />

      <main className="mx-auto max-w-7xl space-y-8 px-4 py-6 sm:px-6 lg:px-8 print:max-w-none print:space-y-5 print:px-0 print:py-2">
        {status === 'mock' && (
          <div className="no-print rounded border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
            Não foi possível ler o CSV real ({error}). Exibindo <strong>dados mockados</strong> com a mesma
            estrutura, apenas para ilustrar o layout.
          </div>
        )}

        {/* ---------- VISÃO GERAL ---------- */}
        <Section
          title="Visão geral"
          subtitle="Totais e composição do dataset completo de pull requests analisados."
        >
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <KpiCard label="Total de PRs" value={formatInt(summary.totalPRs)} accent="indigo" />
            <KpiCard label="Repositórios" value={formatInt(summary.totalRepositories)} accent="teal" />
            <KpiCard label="Linguagens" value={formatInt(langCount)} sublabel={summary.languages.map((l) => l.name).join(' · ')} accent="amber" />
            <KpiCard label="Agentes de IA" value={formatInt(agentCount)} sublabel="identificados por fingerprint" accent="violet" />
            <KpiCard label="PRs com revisão" value={formatPercent(summary.reviewRate)} accent="sky" />
            <KpiCard label="PRs revertidos" value={formatPercent(summary.revertRate)} accent="rose" />
            <KpiCard label="Grupo IA autônoma" value={formatInt(iaGroup)} sublabel="PRs abertos por agentes" accent="indigo" />
            <KpiCard label="Grupo humano" value={formatInt(humanGroup)} sublabel="confirmados por humanos" accent="teal" />
          </div>
        </Section>

        {/* ---------- TENDÊNCIA CENTRAL ---------- */}
        <Section
          title="Tendência central das métricas"
          subtitle="Mediana (destaque), média e intervalo interquartil (P25–P75) no dataset completo. A mediana é a medida-síntese preferida por causa da forte assimetria das distribuições."
        >
          <CentralTendency overall={summary.overall} />
        </Section>

        {/* ---------- QUESTÕES DE PESQUISA ---------- */}
        <ResearchQuestions stats={stats} />

        {/* ---------- DISTRIBUIÇÕES (subgrupos categóricos) ---------- */}
        <Section
          title="Composição por subgrupos"
          subtitle="Particionamento do dataset por linguagem de programação e por agente de IA."
        >
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <ChartFrame title="PRs por linguagem" hint="Distribuição percentual no dataset completo">
              <LanguageDonut data={summary.languages} />
            </ChartFrame>
            <ChartFrame title="PRs por agente de IA" hint="Identificação via fingerprint do PR">
              <AgentBar data={summary.agents} />
            </ChartFrame>
          </div>
        </Section>

        {/* ---------- FORMA DAS DISTRIBUIÇÕES ---------- */}
        <Section
          title="Forma das distribuições"
          subtitle="Histogramas mostram a concentração e a cauda longa das principais métricas contínuas."
        >
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <ChartFrame title="Distribuição de linhas alteradas (diff)" hint="Eixo Y: nº de PRs · Eixo X: faixas de linhas no diff">
              <MetricHistogram bins={summary.histograms.diff_lines} color="#1d4ed8" />
            </ChartFrame>
            <ChartFrame title="Distribuição do tempo até o merge" hint="Eixo Y: nº de PRs · Eixo X: faixas de dias até o merge">
              <MetricHistogram bins={summary.histograms.days_to_merge} color="#374151" />
            </ChartFrame>
          </div>
        </Section>

        {/* ---------- COMPARAÇÃO POR LINGUAGEM ---------- */}
        <Section
          title="Comparação entre linguagens"
          subtitle="Mediana e média de uma métrica selecionada, comparando cada subgrupo de linguagem."
          action={<MetricSelect value={langMetric} onChange={setLangMetric} />}
        >
          <ChartFrame
            title={`Mediana de "${metricLabel(langMetric)}" por linguagem`}
            hint="Barras coloridas: mediana por linguagem · Barra cinza: média"
            height={340}
          >
            <MedianByLanguage byLanguage={summary.byLanguage} metricKey={langMetric} />
          </ChartFrame>
        </Section>

        {/* ---------- COMPARAÇÃO ENTRE GRUPOS ---------- */}
        <Section
          title="Comparação entre grupos do estudo"
          subtitle="IA autônoma vs. humano confirmado. Os tamanhos amostrais são muito distintos — interprete com cautela."
          action={<MetricSelect value={groupMetric} onChange={setGroupMetric} />}
        >
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
            <Card className="p-4 lg:col-span-2">
              <h3 className="mb-2 text-sm font-semibold text-slate-800">
                Mediana de "{metricLabel(groupMetric)}" por grupo
              </h3>
              <div style={{ height: 280 }}>
                <GroupComparison byGroup={summary.byGroup} metricKey={groupMetric} />
              </div>
            </Card>
            <div className="space-y-3">
              {Object.values(GROUPS).map((g) => {
                const scope = summary.byGroup[g.key]
                if (!scope) return null
                return (
                  <Card key={g.key} className="p-4">
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-sm" style={{ background: g.color }} />
                      <h4 className="text-sm font-semibold text-slate-800">{g.label}</h4>
                    </div>
                    <p className="mt-0.5 text-xs text-slate-500">{g.description}</p>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="text-xs text-slate-400">Nº de PRs</p>
                        <p className="font-bold tabular-nums">{formatInt(scope.count)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Mediana</p>
                        <p className="font-bold tabular-nums">
                          {formatDecimal(scope.metrics[groupMetric]?.median)}
                        </p>
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>
          </div>
        </Section>
      </main>

      <footer className="border-t border-slate-200 py-5 text-center text-xs text-slate-400">
        Laboratório de Experimentação de Software · Lab04 — Visualização de dados · React + Tailwind CSS + Recharts
      </footer>
    </div>
  )
}
