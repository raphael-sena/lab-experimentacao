import { useEffect, useMemo, useState } from 'react'
import Papa from 'papaparse'
import { ALPHA, API_TYPES, DATASET_URL, ENDPOINTS, MEASURES } from '../lib/constants'
import { cliffsDelta, describe, mannWhitneyU, reduction } from '../lib/stats'

const num = (v) => {
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : NaN
}

/**
 * Carrega raw_data.csv e deriva TODA a análise no cliente: estatísticas
 * descritivas por (endpoint × API × medida) e os testes de hipótese
 * (Mann-Whitney unilateral + Cliff's Delta) por endpoint, para RQ1 e RQ2.
 */
export function useExperiment() {
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    Papa.parse(DATASET_URL, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (res) => {
        if (cancelled) return
        try {
          const clean = res.data
            .filter((r) => r.api_type && r.endpoint)
            .map((r) => ({
              timestamp: r.timestamp,
              trial: num(r.trial),
              api_type: r.api_type.trim(),
              endpoint: r.endpoint.trim(),
              latency_ms: num(r.latency_ms),
              size_bytes: num(r.size_bytes),
              status_code: num(r.status_code),
            }))
            .filter((r) => Number.isFinite(r.latency_ms) && Number.isFinite(r.size_bytes))
          setRows(clean)
          setStatus('ready')
        } catch (err) {
          setError(String(err))
          setStatus('error')
        }
      },
      error: (err) => {
        if (cancelled) return
        setError(String(err?.message || err))
        setStatus('error')
      },
    })
    return () => {
      cancelled = true
    }
  }, [])

  const analysis = useMemo(() => {
    if (rows.length === 0) return null

    const pick = (filter, key) => rows.filter(filter).map((r) => r[key])

    // cells[endpoint][api][measure] = describe(...)
    const cells = {}
    for (const ep of ENDPOINTS) {
      cells[ep.key] = {}
      for (const api of API_TYPES) {
        cells[ep.key][api] = {}
        for (const m of Object.keys(MEASURES)) {
          cells[ep.key][api][m] = describe(
            pick((r) => r.endpoint === ep.key && r.api_type === api, m),
          )
        }
      }
    }

    // Visão geral por API (todos os endpoints juntos).
    const overall = {}
    for (const api of API_TYPES) {
      overall[api] = {}
      for (const m of Object.keys(MEASURES)) {
        overall[api][m] = describe(pick((r) => r.api_type === api, m))
      }
    }

    // Testes de hipótese por endpoint, para cada medida (H1: GraphQL < REST).
    const tests = {}
    for (const ep of ENDPOINTS) {
      tests[ep.key] = {}
      for (const m of Object.keys(MEASURES)) {
        const g = pick((r) => r.endpoint === ep.key && r.api_type === 'GraphQL', m)
        const rst = pick((r) => r.endpoint === ep.key && r.api_type === 'REST', m)
        const mw = mannWhitneyU(g, rst)
        const cd = cliffsDelta(g, rst)
        tests[ep.key][m] = {
          ...mw,
          ...cd,
          reduction: reduction(describe(g).median, describe(rst).median),
          significant: mw.p < ALPHA,
        }
      }
    }

    const totalBytes = {}
    const totalTrials = {}
    for (const api of API_TYPES) {
      totalBytes[api] = overall[api].size_bytes.total
      totalTrials[api] = overall[api].size_bytes.n
    }
    const bandwidthSaved = reduction(totalBytes.GraphQL, totalBytes.REST)
    const latencySaved = reduction(overall.GraphQL.latency_ms.median, overall.REST.latency_ms.median)

    return {
      cells,
      overall,
      tests,
      totals: {
        trials: rows.length,
        totalBytes,
        totalTrials,
        bandwidthSaved,
        latencySaved,
      },
    }
  }, [rows])

  return { status, error, rows, analysis }
}
