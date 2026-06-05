import { useEffect, useState } from 'react'
import Papa from 'papaparse'
import { toNumbers } from '../lib/stats'

// CSVs dedicados (pequenos) com as métricas estáticas das RQs 1 e 2.
const CCM_URL = '/docs/data/metricas_b2.csv' // RQ01 — ccm_mean por PR
const SMELL_URL = '/docs/data/metricas_q3.csv' // RQ02 — design_smell_density por PR

const loadCsv = (url) =>
  new Promise((resolve) => {
    Papa.parse(url, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (res) => resolve(res.data),
      error: () => resolve([]),
    })
  })

/** Separa os valores de uma coluna entre os grupos do estudo (G1=IA, G2=Humano). */
function splitByGroup(rows, column) {
  const g1 = []
  const g2 = []
  for (const r of rows) {
    const g = String(r.group)
    if (r[column] === '' || r[column] == null) continue
    if (g === '1') g1.push(r[column])
    else if (g === '2') g2.push(r[column])
  }
  return { G1: toNumbers(g1), G2: toNumbers(g2) }
}

/**
 * Carrega e estrutura os dados das RQ1 (complexidade ciclomática) e
 * RQ2 (densidade de code smells), agrupados por IA (G1) vs. Humano (G2).
 */
export function useRqData() {
  const [data, setData] = useState(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([loadCsv(CCM_URL), loadCsv(SMELL_URL)]).then(([ccmRows, smellRows]) => {
      if (cancelled) return
      setData({
        ccm: splitByGroup(ccmRows, 'ccm_mean'),
        smell: splitByGroup(smellRows, 'design_smell_density'),
      })
    })
    return () => {
      cancelled = true
    }
  }, [])

  return data
}
