// Web Worker: lê e agrega o dataset_final.csv (~29 MB, ~202k linhas) fora da
// thread principal usando streaming do PapaParse (callback `step`), de modo que
// a UI nunca trave. Apenas um objeto-resumo compacto é enviado de volta.

import Papa from 'papaparse'

const KNOWN_LANGS = new Set(['TypeScript', 'Python', 'JavaScript'])

// Métricas numéricas para as quais calculamos tendência central por escopo.
const MEDIAN_METRICS = [
  'diff_lines',
  'changed_files',
  'days_to_merge',
  'commit_count',
  'review_count',
  'test_file_ratio',
  'additions',
  'deletions',
]

const num = (v) => {
  if (v == null) return NaN
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : NaN
}

// --------- acumuladores ---------
const repos = new Set()
const langCounts = new Map()
const agentCounts = new Map()
const groupCounts = new Map()
let total = 0
let reviewTotal = 0
let revertTotal = 0

// scope -> { count, metrics: { metricKey: number[] } }
const scopes = new Map()
const ensureScope = (key) => {
  let s = scopes.get(key)
  if (!s) {
    s = { count: 0, metrics: {} }
    scopes.set(key, s)
  }
  return s
}
const pushMetric = (scope, key, val) => {
  ;(scope.metrics[key] || (scope.metrics[key] = [])).push(val)
}

// diff_lines por agente (para enriquecer o gráfico de agentes)
const agentDiff = new Map()

const sample = []
const inc = (map, key) => map.set(key, (map.get(key) || 0) + 1)

function handleRow(row) {
  total += 1

  const lang = KNOWN_LANGS.has(row.language) ? row.language : 'Outras'
  const groupLabel = row.group_label || 'desconhecido'
  const agent = row.fingerprint_agent ? row.fingerprint_agent : 'desconhecido'

  if (row.repository) repos.add(row.repository)
  inc(langCounts, lang)
  inc(agentCounts, agent)
  inc(groupCounts, groupLabel)
  if (num(row.has_review) === 1) reviewTotal += 1
  if (num(row.is_revert) === 1) revertTotal += 1

  const all = ensureScope('all')
  const langScope = ensureScope('lang:' + lang)
  const groupScope = ensureScope('group:' + groupLabel)
  all.count += 1
  langScope.count += 1
  groupScope.count += 1

  for (const m of MEDIAN_METRICS) {
    const v = num(row[m])
    if (!Number.isNaN(v)) {
      pushMetric(all, m, v)
      pushMetric(langScope, m, v)
      pushMetric(groupScope, m, v)
    }
  }

  const dl = num(row.diff_lines)
  if (!Number.isNaN(dl)) {
    let arr = agentDiff.get(agent)
    if (!arr) agentDiff.set(agent, (arr = []))
    arr.push(dl)
  }

  if (sample.length < 25) {
    sample.push({
      repository: row.repository,
      pr_number: row.pr_number,
      group_label: groupLabel,
      language: row.language || '—',
      fingerprint_agent: agent,
      diff_lines: row.diff_lines,
      changed_files: row.changed_files,
      days_to_merge: row.days_to_merge,
    })
  }

  if (total % 10000 === 0) {
    self.postMessage({ type: 'progress', processed: total })
  }
}

// --------- estatísticas ---------
function quantiles(values) {
  const n = values.length
  if (n === 0) return { n: 0, mean: NaN, median: NaN, p25: NaN, p75: NaN, min: NaN, max: NaN }
  values.sort((a, b) => a - b)
  let sum = 0
  for (let i = 0; i < n; i++) sum += values[i]
  const at = (q) => {
    const idx = (n - 1) * q
    const lo = Math.floor(idx)
    const hi = Math.ceil(idx)
    if (lo === hi) return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (idx - lo)
  }
  return {
    n,
    mean: sum / n,
    median: at(0.5),
    p25: at(0.25),
    p75: at(0.75),
    min: values[0],
    max: values[n - 1],
  }
}

function statsForScope(scopeKey) {
  const s = scopes.get(scopeKey)
  if (!s) return { count: 0, metrics: {} }
  const metrics = {}
  for (const m of MEDIAN_METRICS) {
    metrics[m] = quantiles(s.metrics[m] || [])
  }
  return { count: s.count, metrics }
}

function histogram(values, edges) {
  const bins = edges.slice(0, -1).map((lo, i) => ({
    label: `${lo}–${edges[i + 1]}`,
    lo,
    hi: edges[i + 1],
    count: 0,
  }))
  // bin extra para valores acima do último limite
  const last = edges[edges.length - 1]
  bins.push({ label: `> ${last}`, lo: last, hi: Infinity, count: 0 })
  for (const v of values) {
    let placed = false
    for (let i = 0; i < bins.length - 1; i++) {
      if (v >= bins[i].lo && v < bins[i].hi) {
        bins[i].count += 1
        placed = true
        break
      }
    }
    if (!placed) bins[bins.length - 1].count += 1
  }
  return bins
}

function buildSummary() {
  const mapToSorted = (map) =>
    [...map.entries()].map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count)

  // histogramas a partir das séries já coletadas no escopo "all"
  const allScope = scopes.get('all')
  const diffValues = (allScope?.metrics.diff_lines || []).slice()
  const daysValues = (allScope?.metrics.days_to_merge || []).slice()

  const byLanguage = {}
  for (const { name } of mapToSorted(langCounts)) {
    byLanguage[name] = statsForScope('lang:' + name)
  }
  const byGroup = {}
  for (const { name } of mapToSorted(groupCounts)) {
    byGroup[name] = statsForScope('group:' + name)
  }

  const agents = mapToSorted(agentCounts).map((a) => {
    const arr = (agentDiff.get(a.name) || []).slice()
    return { ...a, diffMedian: quantiles(arr).median }
  })

  return {
    type: 'done',
    source: 'csv',
    totalPRs: total,
    totalRepositories: repos.size,
    reviewRate: total ? reviewTotal / total : 0,
    revertRate: total ? revertTotal / total : 0,
    languages: mapToSorted(langCounts),
    agents,
    groups: mapToSorted(groupCounts),
    overall: statsForScope('all'),
    byLanguage,
    byGroup,
    histograms: {
      diff_lines: histogram(diffValues, [0, 25, 50, 100, 250, 500, 1000]),
      days_to_merge: histogram(daysValues, [0, 1, 3, 7, 14, 30, 90]),
    },
    sample,
  }
}

self.onmessage = (e) => {
  if (e.data?.type !== 'parse') return
  const url = e.data.url

  Papa.parse(url, {
    download: true,
    header: true,
    skipEmptyLines: true,
    step: (results) => handleRow(results.data),
    complete: () => {
      try {
        self.postMessage(buildSummary())
      } catch (err) {
        self.postMessage({ type: 'error', message: String(err) })
      }
    },
    error: (err) => self.postMessage({ type: 'error', message: String(err?.message || err) }),
  })
}
