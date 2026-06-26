import { useMemo, useState } from 'react'
import { useExperiment } from './hooks/useExperiment'
import { useScrollSpy } from './hooks/useScrollSpy'
import { ENDPOINTS, MEASURES, SECTIONS } from './lib/constants'
import { formatBytes, formatInt, formatMs, formatPercent } from './lib/format'
import { Header } from './components/Header'
import { Nav } from './components/Nav'
import { Filters } from './components/Filters'
import { RQTestCards } from './components/ResearchQuestions'
import { EndpointTable } from './components/EndpointTable'
import { BoxPlot } from './components/BoxPlot'
import { Card, ChartFrame, KpiCard, Loader, Section, Toggle } from './components/ui/primitives'
import {
  ApiComparisonBars,
  LatencyDistribution,
  LatencySizeScatter,
  TotalTrafficBars,
} from './components/charts'

const STAT_OPTIONS = [
  { value: 'median', label: 'Mediana' },
  { value: 'mean', label: 'Média' },
]
const SCALE_OPTIONS = [
  { value: 'linear', label: 'Linear' },
  { value: 'log', label: 'Log' },
]
const MEASURE_OPTIONS = [
  { value: 'latency_ms', label: 'Latência' },
  { value: 'size_bytes', label: 'Tamanho' },
]

const SECTION_IDS = SECTIONS.map((s) => s.id)
const pctSigned = (v) => (v >= 0 ? '−' : '+') + formatPercent(Math.abs(v))

export default function App() {
  const { status, error, rows, analysis } = useExperiment()
  const active = useScrollSpy(SECTION_IDS)

  // ── Estado global de filtro ──────────────────────────────────────────────
  const [focus, setFocus] = useState(() => new Set())
  const [apiVisible, setApiVisible] = useState({ REST: true, GraphQL: true })
  const [latStat, setLatStat] = useState('median')
  const [sizeScale, setSizeScale] = useState('log')
  const [boxMeasure, setBoxMeasure] = useState('latency_ms')
  const [boxScale, setBoxScale] = useState('linear')
  const [tableMeasure, setTableMeasure] = useState('latency_ms')

  const toggleEndpoint = (key) =>
    setFocus((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  const clearFocus = () => setFocus(new Set())
  const toggleApi = (api) =>
    setApiVisible((prev) => {
      const next = { ...prev, [api]: !prev[api] }
      if (!next.REST && !next.GraphQL) return prev // mantém ao menos uma série
      return next
    })

  const activeEndpoints = useMemo(
    () => (focus.size ? ENDPOINTS.filter((e) => focus.has(e.key)) : ENDPOINTS),
    [focus],
  )
  const filteredRows = useMemo(() => {
    const keys = new Set(activeEndpoints.map((e) => e.key))
    return rows.filter((r) => keys.has(r.endpoint) && apiVisible[r.api_type])
  }, [rows, activeEndpoints, apiVisible])

  if (!analysis) {
    return (
      <div className="min-h-screen">
        <Header />
        <Loader error={status === 'error' ? error : null} />
      </div>
    )
  }

  const { overall, totals, cells, tests } = analysis
  const sigCount = (m) => ENDPOINTS.filter((ep) => tests[ep.key][m].significant).length

  return (
    <div id="top" className="min-h-screen text-[var(--ink)]">
      <Header />

      {/* Barra sticky: navegação (scrollspy) + filtros globais */}
      <div
        className="no-print sticky top-0 z-40 border-b bg-[rgba(250,249,247,0.85)] backdrop-blur-md"
        style={{ borderColor: 'var(--hairline)' }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="py-2.5">
            <Nav active={active} onPrint={() => window.print()} />
          </div>
          <div className="border-t py-2.5" style={{ borderColor: 'var(--hairline)' }}>
            <Filters
              focus={focus}
              onToggleEndpoint={toggleEndpoint}
              onClearFocus={clearFocus}
              apiVisible={apiVisible}
              onToggleApi={toggleApi}
            />
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-7xl space-y-14 px-4 py-10 sm:px-6 lg:px-8 print:max-w-none print:space-y-6 print:px-0 print:py-2">
        {/* ───────────── 01 · VISÃO GERAL ───────────── */}
        <Section
          id="overview"
          n="01"
          title="Visão geral"
          subtitle="A síntese do experimento em quatro números. GraphQL devolve só os campos solicitados; REST entrega recursos completos."
        >
          <div className="grid grid-cols-2 gap-x-8 gap-y-8 border-y py-7 lg:grid-cols-4" style={{ borderColor: 'var(--hairline)' }}>
            <KpiCard
              label="Economia de banda"
              target={totals.bandwidthSaved}
              format={formatPercent}
              accent="#0F766E"
              sublabel={`${formatBytes(totals.totalBytes.GraphQL)} vs ${formatBytes(totals.totalBytes.REST)} trafegados`}
            />
            <KpiCard
              label="Latência mediana"
              target={totals.latencySaved}
              format={pctSigned}
              sublabel={`GraphQL ${formatMs(overall.GraphQL.latency_ms.median)} · REST ${formatMs(overall.REST.latency_ms.median)}`}
            />
            <KpiCard
              label="Medições válidas"
              target={totals.trials}
              format={formatInt}
              sublabel="requisições com status 200"
            />
            <KpiCard label="Desenho" value="4 × 2" sublabel="endpoints × paradigmas de API" />
          </div>

          <div className="mt-7 grid grid-cols-1 gap-5 lg:grid-cols-5">
            <div className="lg:col-span-3">
              <ChartFrame title="Tráfego total transferido" hint="Soma de todos os bytes recebidos no experimento, por paradigma de API" height={150}>
                <TotalTrafficBars totalBytes={totals.totalBytes} apiVisible={apiVisible} />
              </ChartFrame>
            </div>
            <Card className="p-5 lg:col-span-2" hover>
              <h3 className="text-sm font-semibold text-[var(--ink)]">Leitura dos resultados</h3>
              <div className="mt-3 space-y-3 text-sm leading-relaxed text-[var(--body)]">
                <p>
                  <strong className="text-[var(--ink)]">Tamanho (RQ2):</strong> ganho expressivo e unânime — GraphQL
                  reduz o payload em todos os <strong>{sigCount('size_bytes')}/4</strong> endpoints
                  (Cliff's δ máximo).
                </p>
                <p>
                  <strong className="text-[var(--ink)]">Latência (RQ1):</strong> vantagem real, porém parcial —
                  significativa em <strong>{sigCount('latency_ms')}/4</strong> endpoints. Onde o payload REST é
                  enorme, o tempo também cai.
                </p>
                <p className="border-t pt-3 text-xs text-[var(--faint)]" style={{ borderColor: 'var(--hairline)' }}>
                  Use os filtros acima para isolar um endpoint ou uma série — todos os gráficos respondem.
                </p>
              </div>
            </Card>
          </div>
        </Section>

        {/* ───────────── 02 · RQ1 LATÊNCIA ───────────── */}
        <Section
          id="rq1"
          n="02"
          title="RQ1 — Tempo de resposta"
          subtitle="As respostas via GraphQL são mais rápidas (menor latência) do que via REST?"
        >
          <RQTestCards measure="latency_ms" cells={cells} tests={tests} endpoints={activeEndpoints} />
          <div className="mt-5">
            <ChartFrame
              title={`${latStat === 'median' ? 'Mediana' : 'Média'} de latência por endpoint`}
              hint="Barras agrupadas em milissegundos — menor é melhor. Passe o mouse para destacar."
              height={320}
              action={<Toggle options={STAT_OPTIONS} value={latStat} onChange={setLatStat} />}
            >
              <ApiComparisonBars cells={cells} measure="latency_ms" stat={latStat} endpoints={activeEndpoints} apiVisible={apiVisible} />
            </ChartFrame>
          </div>
        </Section>

        {/* ───────────── 03 · RQ2 TAMANHO ───────────── */}
        <Section
          id="rq2"
          n="03"
          title="RQ2 — Tamanho do payload"
          subtitle="As respostas via GraphQL têm payload menor (em bytes) do que via REST?"
        >
          <RQTestCards measure="size_bytes" cells={cells} tests={tests} endpoints={activeEndpoints} />
          <div className="mt-5">
            <ChartFrame
              title="Mediana do tamanho do payload por endpoint"
              hint="Bytes por resposta — menor é melhor. A escala log evidencia a diferença de ordem de grandeza."
              height={320}
              action={<Toggle options={SCALE_OPTIONS} value={sizeScale} onChange={setSizeScale} />}
            >
              <ApiComparisonBars cells={cells} measure="size_bytes" stat="median" scale={sizeScale} endpoints={activeEndpoints} apiVisible={apiVisible} />
            </ChartFrame>
          </div>
        </Section>

        {/* ───────────── 04 · DISTRIBUIÇÕES ───────────── */}
        <Section
          id="distributions"
          n="04"
          title="Forma das distribuições"
          subtitle="Dispersão e variabilidade das medições — a base que justifica o uso de testes não-paramétricos."
        >
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            <ChartFrame title="Distribuição da latência" hint="Frequência de medições por faixa de tempo de resposta, por API">
              <LatencyDistribution rows={filteredRows} apiVisible={apiVisible} />
            </ChartFrame>
            <ChartFrame title="Latência × tamanho do payload" hint="Cada ponto é uma requisição · eixo X em escala log">
              <LatencySizeScatter rows={filteredRows} apiVisible={apiVisible} />
            </ChartFrame>
          </div>
        </Section>

        {/* ───────────── 05 · BOXPLOTS ───────────── */}
        <Section
          id="boxplots"
          n="05"
          title="Boxplots comparativos"
          subtitle="Resumo de cinco números (mín · P25 · mediana · P75 · máx) por endpoint, revelando assimetria e outliers."
        >
          <ChartFrame
            title={`Boxplot — ${MEASURES[boxMeasure].label.toLowerCase()} (${MEASURES[boxMeasure].unit})`}
            hint="Caixa = intervalo interquartil (P25–P75) · linha central = mediana · hastes = mín/máx"
            height={360}
            action={
              <div className="flex items-center gap-2">
                <Toggle options={MEASURE_OPTIONS} value={boxMeasure} onChange={setBoxMeasure} />
                <Toggle options={SCALE_OPTIONS} value={boxScale} onChange={setBoxScale} />
              </div>
            }
          >
            <BoxPlot cells={cells} measure={boxMeasure} scale={boxScale} endpoints={activeEndpoints} apiVisible={apiVisible} />
          </ChartFrame>
        </Section>

        {/* ───────────── 06 · DADOS ───────────── */}
        <Section
          id="data"
          n="06"
          title="Estatísticas descritivas"
          subtitle="Todos os valores agregados por endpoint e paradigma de API."
          action={<Toggle options={MEASURE_OPTIONS} value={tableMeasure} onChange={setTableMeasure} />}
        >
          <EndpointTable cells={cells} measure={tableMeasure} endpoints={activeEndpoints} />
        </Section>
      </main>

      <footer className="border-t py-8 text-center" style={{ borderColor: 'var(--hairline)' }}>
        <p className="chess-glyphs mb-3 text-lg tracking-[0.35em] text-[var(--faint)]" aria-hidden>
          ♜♞♝♛♚♝♞♜
        </p>
        <p className="display text-sm text-[var(--ink)]">GraphQL vs. REST</p>
        <p className="mt-1 text-xs text-[var(--faint)]">
          Laboratório de Experimentação de Software · Lab 05 · Stockfish · React · Tailwind CSS · Recharts
        </p>
      </footer>
    </div>
  )
}
