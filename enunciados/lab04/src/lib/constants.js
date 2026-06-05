// Configuração central do dataset (Lab04 - Caracterização do dataset).
//
// Estudo: Pull Requests gerados/assistidos por agentes de IA vs. PRs
// confirmados por humanos. Cada métrica abaixo descreve exatamente a coluna
// correspondente no arquivo `dataset_final.csv`.

/** Caminho do CSV servido estaticamente pelo Vite (pasta `public/`). */
export const DATASET_URL = '/docs/data/dataset_final.csv'

/** Caminho do CSV com os resultados dos testes estatísticos. */
export const STATS_URL = '/docs/data/resultados_estatisticos.csv'

/** Os dois grupos (subpopulações) comparados no estudo. */
export const GROUPS = {
  IA_autonomo: {
    key: 'IA_autonomo',
    label: 'IA Autônoma',
    description: 'PRs abertos de forma autônoma por agentes de IA',
    color: '#6366f1', // indigo-500
  },
  humano_confirmado: {
    key: 'humano_confirmado',
    label: 'Humano Confirmado',
    description: 'PRs assistidos por IA e confirmados por um humano',
    color: '#14b8a6', // teal-500
  },
}

/** Linguagens de programação presentes no dataset. */
export const LANGUAGE_COLORS = {
  TypeScript: '#3178c6',
  Python: '#f7c948',
  JavaScript: '#f59e0b',
  Outras: '#94a3b8',
}

/** Cores para os agentes de IA identificados (fingerprint). */
export const AGENT_COLORS = {
  devin: '#a855f7',
  claude_code: '#f97316',
  cursor: '#06b6d4',
  openai_codex: '#10b981',
  desconhecido: '#94a3b8',
}

/**
 * Métricas numéricas usadas para a caracterização (tendência central,
 * histogramas e comparação de subgrupos). A `key` precisa bater exatamente
 * com o cabeçalho do CSV.
 */
export const NUMERIC_METRICS = [
  { key: 'diff_lines', label: 'Linhas alteradas (diff)', unit: 'linhas', short: 'Diff' },
  { key: 'changed_files', label: 'Arquivos alterados', unit: 'arquivos', short: 'Arquivos' },
  { key: 'days_to_merge', label: 'Tempo até o merge', unit: 'dias', short: 'Dias p/ merge' },
  { key: 'commit_count', label: 'Commits por PR', unit: 'commits', short: 'Commits' },
  { key: 'review_count', label: 'Revisões por PR', unit: 'revisões', short: 'Revisões' },
  { key: 'test_file_ratio', label: 'Proporção de arquivos de teste', unit: 'razão', short: 'Testes' },
  { key: 'additions', label: 'Linhas adicionadas', unit: 'linhas', short: 'Adições' },
  { key: 'deletions', label: 'Linhas removidas', unit: 'linhas', short: 'Remoções' },
]

/** Subconjunto de métricas exibidas como cards de tendência central. */
export const CENTRAL_TENDENCY_KEYS = [
  'diff_lines',
  'changed_files',
  'days_to_merge',
  'commit_count',
  'review_count',
  'test_file_ratio',
]

/** Métricas comparadas lado a lado entre linguagens / grupos. */
export const COMPARISON_KEYS = ['diff_lines', 'changed_files', 'days_to_merge', 'commit_count']

/** Colunas exibidas na tabela de amostra dos dados brutos. */
export const SAMPLE_COLUMNS = [
  { key: 'repository', label: 'Repositório' },
  { key: 'pr_number', label: 'PR' },
  { key: 'group_label', label: 'Grupo' },
  { key: 'language', label: 'Linguagem' },
  { key: 'fingerprint_agent', label: 'Agente' },
  { key: 'diff_lines', label: 'Diff' },
  { key: 'changed_files', label: 'Arquivos' },
  { key: 'days_to_merge', label: 'Dias p/ merge' },
]
