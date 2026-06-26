// Estatística descritiva e testes de hipótese calculados no cliente, a partir
// dos dados brutos (raw_data.csv). Mantém o dashboard 100% consistente: todos
// os números exibidos derivam da MESMA amostra carregada no navegador.

/** Estatísticas descritivas (com quantis interpolados) de um vetor numérico. */
export function describe(input) {
  const values = input.filter((v) => Number.isFinite(v)).slice().sort((a, b) => a - b)
  const n = values.length
  if (n === 0) {
    return { n: 0, mean: NaN, median: NaN, std: NaN, p25: NaN, p75: NaN, min: NaN, max: NaN, total: 0 }
  }
  let sum = 0
  for (const v of values) sum += v
  const mean = sum / n
  let sq = 0
  for (const v of values) sq += (v - mean) ** 2
  const std = n > 1 ? Math.sqrt(sq / (n - 1)) : 0
  const at = (q) => {
    const idx = (n - 1) * q
    const lo = Math.floor(idx)
    const hi = Math.ceil(idx)
    if (lo === hi) return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (idx - lo)
  }
  return {
    n,
    mean,
    median: at(0.5),
    std,
    p25: at(0.25),
    p75: at(0.75),
    min: values[0],
    max: values[n - 1],
    total: sum,
  }
}

/** Função de distribuição acumulada da normal padrão (aprox. de Abramowitz–Stegun). */
function normalCdf(z) {
  const t = 1 / (1 + 0.2316419 * Math.abs(z))
  const d = 0.3989423 * Math.exp((-z * z) / 2)
  let p =
    d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
  if (z > 0) p = 1 - p
  return p
}

/**
 * Cliff's Delta — tamanho de efeito não-paramétrico em [-1, 1].
 * delta < 0  ⇒  o grupo `a` tende a ter valores MENORES que `b`.
 */
export function cliffsDelta(a, b) {
  let gt = 0
  let lt = 0
  for (const x of a) {
    for (const y of b) {
      if (x > y) gt += 1
      else if (x < y) lt += 1
    }
  }
  const delta = (gt - lt) / (a.length * b.length)
  const mag = Math.abs(delta)
  let label
  if (mag < 0.147) label = 'Desprezível'
  else if (mag < 0.33) label = 'Pequeno'
  else if (mag < 0.474) label = 'Médio'
  else label = 'Grande'
  return { delta, magnitude: label }
}

/**
 * Teste U de Mann-Whitney unilateral para H1: `a` < `b` (com correção de
 * empates e continuidade). Retorna a estatística U do grupo `a` e o p-valor.
 */
export function mannWhitneyU(a, b) {
  const na = a.length
  const nb = b.length
  if (na === 0 || nb === 0) return { U: NaN, p: NaN, z: NaN }

  // Ranqueamento conjunto com correção de empates (ranks médios).
  const combined = [
    ...a.map((v) => ({ v, g: 0 })),
    ...b.map((v) => ({ v, g: 1 })),
  ].sort((x, y) => x.v - y.v)

  const N = combined.length
  let i = 0
  let tieSum = 0 // Σ (t³ − t) para a correção de variância
  let rankSumA = 0
  while (i < N) {
    let j = i
    while (j < N && combined[j].v === combined[i].v) j += 1
    const t = j - i
    const avgRank = (i + 1 + j) / 2 // ranks de 1..N → média do bloco de empate
    for (let k = i; k < j; k++) {
      if (combined[k].g === 0) rankSumA += avgRank
    }
    tieSum += t ** 3 - t
    i = j
  }

  const Ua = rankSumA - (na * (na + 1)) / 2
  const mu = (na * nb) / 2
  const sigma = Math.sqrt(
    (na * nb / (N * (N - 1))) * ((N ** 3 - N) / 12 - tieSum / 12),
  )
  // H1: a < b  ⇒  esperamos Ua pequeno. p = P(U ≤ Ua) com correção de continuidade.
  const z = sigma > 0 ? (Ua - mu + 0.5) / sigma : 0
  const p = normalCdf(z)
  return { U: Ua, p, z }
}

/** Razão de redução de `b` para `a`: (b − a) / b, em [0,1] quando a < b. */
export function reduction(a, b) {
  if (!Number.isFinite(a) || !Number.isFinite(b) || b === 0) return NaN
  return (b - a) / b
}
