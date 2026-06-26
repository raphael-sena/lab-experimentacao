// Configuração central do experimento Lab05 — GraphQL vs REST.

export const DATASET_URL = '/data/raw_data.csv'

// Repositório-alvo do experimento controlado.
export const TARGET_REPO = 'official-stockfish/Stockfish'

// Os dois paradigmas comparados. A ordem define a posição nas barras agrupadas.
export const API_TYPES = ['REST', 'GraphQL']

// Paleta editorial sóbria: um vermelho (REST) e um verde-petróleo (GraphQL).
export const API_COLORS = {
  REST: '#C0392B', // vermelho-tijolo
  GraphQL: '#0F766E', // verde-petróleo
}

export const API_FILL = {
  REST: 'rgba(192, 57, 43, 0.10)',
  GraphQL: 'rgba(15, 118, 110, 0.10)',
}

// Endpoints (recursos) avaliados, com rótulos e cor de acento própria (muted).
export const ENDPOINTS = [
  { key: 'repo', label: 'Repositório', short: 'repo', color: '#1E40AF' },
  { key: 'commits', label: 'Commits', short: 'commits', color: '#B45309' },
  { key: 'issues', label: 'Issues', short: 'issues', color: '#0E7490' },
  { key: 'pulls', label: 'Pull Requests', short: 'pulls', color: '#7E22CE' },
]

export const ENDPOINT_LABEL = Object.fromEntries(ENDPOINTS.map((e) => [e.key, e.label]))
export const ENDPOINT_COLOR = Object.fromEntries(ENDPOINTS.map((e) => [e.key, e.color]))

// As duas variáveis de resposta medidas em cada requisição.
export const MEASURES = {
  latency_ms: { key: 'latency_ms', label: 'Tempo de resposta', unit: 'ms', rq: 'RQ1' },
  size_bytes: { key: 'size_bytes', label: 'Tamanho do payload', unit: 'bytes', rq: 'RQ2' },
}

export const ALPHA = 0.05

// Seções para a navegação sticky (scrollspy).
export const SECTIONS = [
  { id: 'overview', n: '01', label: 'Visão geral' },
  { id: 'rq1', n: '02', label: 'RQ1 · Latência' },
  { id: 'rq2', n: '03', label: 'RQ2 · Payload' },
  { id: 'distributions', n: '04', label: 'Distribuições' },
  { id: 'boxplots', n: '05', label: 'Boxplots' },
  { id: 'data', n: '06', label: 'Dados' },
]
