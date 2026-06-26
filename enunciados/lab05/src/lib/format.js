// Helpers de formatação (pt-BR) reutilizados em cards, eixos e tooltips.

const nf0 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 })
const nf1 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })
const nf2 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 })

/** Inteiro com separador de milhar: 124304 -> "124.304". */
export const formatInt = (v) => (v == null || Number.isNaN(v) ? '—' : nf0.format(v))

/** Número com 1 casa decimal. */
export const formatDecimal = (v) =>
  v == null || Number.isNaN(v) ? '—' : nf1.format(v)

/** Número com 2 casas decimais. */
export const formatDecimal2 = (v) =>
  v == null || Number.isNaN(v) ? '—' : nf2.format(v)

/** Formatação compacta para eixos: 124304 -> "124,3 mil". */
export function formatCompact(v) {
  if (v == null || Number.isNaN(v)) return '—'
  if (Math.abs(v) >= 1000) return nf1.format(v / 1000) + ' mil'
  return nf1.format(v)
}

/** Bytes legíveis: 124304 -> "121,4 KB". */
export function formatBytes(v) {
  if (v == null || Number.isNaN(v)) return '—'
  if (Math.abs(v) >= 1024 * 1024) return nf1.format(v / (1024 * 1024)) + ' MB'
  if (Math.abs(v) >= 1024) return nf1.format(v / 1024) + ' KB'
  return nf0.format(v) + ' B'
}

/** Tempo legível: 170 -> "170 ms". */
export const formatMs = (v) =>
  v == null || Number.isNaN(v) ? '—' : nf1.format(v) + ' ms'

/** Percentual a partir de uma razão 0..1: 0.844 -> "84,4%". */
export const formatPercent = (ratio) =>
  ratio == null || Number.isNaN(ratio) ? '—' : nf1.format(ratio * 100) + '%'

/** p-valor com notação científica quando muito pequeno. */
export function formatPValue(p) {
  if (p == null || Number.isNaN(p)) return '—'
  if (p < 0.0001) return p.toExponential(2)
  return nf2.format(p) === '0,00' ? p.toFixed(4) : nf2.format(p)
}

/** Escolhe o formatador de acordo com a medida (latência ou tamanho). */
export function formatMeasure(measureKey, value) {
  if (value == null || Number.isNaN(value)) return '—'
  return measureKey === 'size_bytes' ? formatBytes(value) : formatMs(value)
}
