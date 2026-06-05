// Helpers de formatação (pt-BR) reutilizados em cards, eixos e tooltips.

const nf0 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 })
const nf1 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })
const nf2 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 })

/** Inteiro com separador de milhar: 202014 -> "202.014". */
export const formatInt = (v) => (v == null || Number.isNaN(v) ? '—' : nf0.format(v))

/** Número com 1 casa decimal. */
export const formatDecimal = (v) =>
  v == null || Number.isNaN(v) ? '—' : nf1.format(v)

/** Número com 2 casas decimais (proporções, p-valores). */
export const formatDecimal2 = (v) =>
  v == null || Number.isNaN(v) ? '—' : nf2.format(v)

/** Formatação compacta para eixos: 202014 -> "202 mil". */
export function formatCompact(v) {
  if (v == null || Number.isNaN(v)) return '—'
  if (Math.abs(v) >= 1000) return nf1.format(v / 1000) + ' mil'
  return nf1.format(v)
}

/** Percentual a partir de uma razão 0..1: 0.735 -> "73,5%". */
export const formatPercent = (ratio) =>
  ratio == null || Number.isNaN(ratio) ? '—' : nf1.format(ratio * 100) + '%'

/** Escolhe o formatador adequado ao tipo da métrica. */
export function formatMetric(key, value) {
  if (value == null || Number.isNaN(value)) return '—'
  if (key === 'test_file_ratio') return formatDecimal2(value)
  if (key === 'days_to_merge') return formatDecimal(value)
  return formatDecimal(value)
}
