// Utilitários estatísticos compartilhados (tendência central e dispersão).

const num = (v) => {
  if (v == null || v === '') return NaN
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : NaN
}

/** Converte um array bruto em números válidos (descarta vazios/NaN). */
export const toNumbers = (arr) => arr.map(num).filter((v) => !Number.isNaN(v))

/**
 * Resumo de cinco números + média a partir de um array numérico.
 * Usa interpolação linear entre posições (mesmo método do worker).
 */
export function quantiles(rawValues) {
  const values = [...rawValues].sort((a, b) => a - b)
  const n = values.length
  if (n === 0) {
    return { n: 0, min: NaN, q1: NaN, median: NaN, q3: NaN, max: NaN, mean: NaN }
  }
  const at = (q) => {
    const idx = (n - 1) * q
    const lo = Math.floor(idx)
    const hi = Math.ceil(idx)
    return lo === hi ? values[lo] : values[lo] + (values[hi] - values[lo]) * (idx - lo)
  }
  const mean = values.reduce((s, v) => s + v, 0) / n
  return { n, min: values[0], q1: at(0.25), median: at(0.5), q3: at(0.75), max: values[n - 1], mean }
}
