// Resumo MOCK no mesmo formato emitido pelo csvWorker.
//
// Usado apenas como fallback de layout caso o CSV real não possa ser lido
// (ex.: arquivo ausente). Os valores são aproximações realistas derivadas do
// próprio dataset, para que o dashboard rode imediatamente.

const q = (n, mean, median, p25, p75, min, max) => ({ n, mean, median, p25, p75, min, max })

const overallMetrics = {
  diff_lines: q(201800, 118.99, 71, 24, 160, 0, 98000),
  changed_files: q(201800, 6.32, 4, 2, 7, 1, 1200),
  days_to_merge: q(200500, 4.34, 0.62, 0.05, 3.1, 0, 600),
  commit_count: q(201900, 3.7, 3, 1, 4, 1, 480),
  review_count: q(201900, 2.32, 1, 0, 3, 0, 90),
  test_file_ratio: q(201800, 0.1824, 0, 0, 0.33, 0, 1),
  additions: q(201800, 88.4, 48, 14, 110, 0, 90000),
  deletions: q(201800, 30.6, 14, 4, 42, 0, 40000),
}

const scaleMetrics = (factors) => {
  const out = {}
  for (const [k, base] of Object.entries(overallMetrics)) {
    const f = factors[k] ?? 1
    out[k] = q(
      Math.round(base.n * (factors._n ?? 0.3)),
      base.mean * f,
      base.median * f,
      base.p25 * f,
      base.p75 * f,
      base.min,
      base.max,
    )
  }
  return out
}

export const MOCK_SUMMARY = {
  type: 'done',
  source: 'mock',
  totalPRs: 202014,
  totalRepositories: 1290,
  reviewRate: 0.7354,
  revertRate: 0.0337,
  languages: [
    { name: 'TypeScript', count: 98520 },
    { name: 'Python', count: 65868 },
    { name: 'JavaScript', count: 37626 },
  ],
  agents: [
    { name: 'devin', count: 134718, diffMedian: 64 },
    { name: 'desconhecido', count: 38824, diffMedian: 82 },
    { name: 'claude_code', count: 24769, diffMedian: 90 },
    { name: 'cursor', count: 3696, diffMedian: 58 },
    { name: 'openai_codex', count: 7, diffMedian: 120 },
  ],
  groups: [
    { name: 'humano_confirmado', count: 202005 },
    { name: 'IA_autonomo', count: 9 },
  ],
  overall: { count: 202014, metrics: overallMetrics },
  byLanguage: {
    TypeScript: { count: 98520, metrics: scaleMetrics({ _n: 0.49, diff_lines: 1.05, days_to_merge: 0.9 }) },
    Python: { count: 65868, metrics: scaleMetrics({ _n: 0.33, diff_lines: 1.0, days_to_merge: 1.2 }) },
    JavaScript: { count: 37626, metrics: scaleMetrics({ _n: 0.18, diff_lines: 0.92, days_to_merge: 0.8 }) },
  },
  byGroup: {
    humano_confirmado: { count: 202005, metrics: scaleMetrics({ _n: 0.999 }) },
    IA_autonomo: {
      count: 9,
      metrics: {
        diff_lines: q(9, 121, 35, 18, 140, 5, 480),
        changed_files: q(9, 2.67, 2, 1, 3, 1, 8),
        days_to_merge: q(9, 7.47, 0.04, 0.01, 8, 0, 38),
        commit_count: q(9, 3.11, 2, 1, 4, 1, 9),
        review_count: q(9, 1.22, 1, 0, 2, 0, 4),
        test_file_ratio: q(9, 0, 0, 0, 0, 0, 0),
        additions: q(9, 95, 28, 12, 110, 4, 400),
        deletions: q(9, 26, 7, 2, 30, 0, 80),
      },
    },
  },
  histograms: {
    diff_lines: [
      { label: '0–25', lo: 0, hi: 25, count: 52000 },
      { label: '25–50', lo: 25, hi: 50, count: 38000 },
      { label: '50–100', lo: 50, hi: 100, count: 44000 },
      { label: '100–250', lo: 100, hi: 250, count: 40000 },
      { label: '250–500', lo: 250, hi: 500, count: 16000 },
      { label: '500–1000', lo: 500, hi: 1000, count: 7000 },
      { label: '> 1000', lo: 1000, hi: Infinity, count: 5014 },
    ],
    days_to_merge: [
      { label: '0–1', lo: 0, hi: 1, count: 96000 },
      { label: '1–3', lo: 1, hi: 3, count: 34000 },
      { label: '3–7', lo: 3, hi: 7, count: 28000 },
      { label: '7–14', lo: 7, hi: 14, count: 18000 },
      { label: '14–30', lo: 14, hi: 30, count: 13000 },
      { label: '30–90', lo: 30, hi: 90, count: 9000 },
      { label: '> 90', lo: 90, hi: Infinity, count: 4014 },
    ],
  },
  sample: [
    { repository: '0dotxyz/marginfi-v2', pr_number: '350', group_label: 'humano_confirmado', language: 'TypeScript', fingerprint_agent: 'claude_code', diff_lines: '242', changed_files: '8', days_to_merge: '4.26' },
    { repository: '0dotxyz/marginfi-v2', pr_number: '351', group_label: 'humano_confirmado', language: 'TypeScript', fingerprint_agent: 'claude_code', diff_lines: '332', changed_files: '10', days_to_merge: '2.23' },
    { repository: 'Significant-Gravitas/AutoGPT', pr_number: '9965', group_label: 'IA_autonomo', language: 'Python', fingerprint_agent: 'devin', diff_lines: '362', changed_files: '8', days_to_merge: '0.04' },
    { repository: 'Significant-Gravitas/AutoGPT', pr_number: '9968', group_label: 'IA_autonomo', language: 'Python', fingerprint_agent: 'devin', diff_lines: '61', changed_files: '1', days_to_merge: '0.62' },
    { repository: '0dotxyz/marginfi-v2', pr_number: '507', group_label: 'humano_confirmado', language: 'TypeScript', fingerprint_agent: 'claude_code', diff_lines: '154', changed_files: '6', days_to_merge: '4.68' },
  ],
}
