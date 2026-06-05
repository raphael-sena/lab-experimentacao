import { useEffect, useState } from 'react'
import Papa from 'papaparse'
import { STATS_URL } from '../lib/constants'

/**
 * Carrega o CSV (pequeno) com os resultados dos testes estatísticos
 * IA_autonomo vs. humano_confirmado. Usado na seção bônus de comparação.
 */
export function useStats() {
  const [rows, setRows] = useState(null)

  useEffect(() => {
    let cancelled = false
    Papa.parse(STATS_URL, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (res) => {
        if (cancelled) return
        // Apenas o estrato "all" (dataset completo) para a caracterização.
        setRows(res.data.filter((r) => r.stratum === 'all' && r.metric))
      },
      error: () => !cancelled && setRows([]),
    })
    return () => {
      cancelled = true
    }
  }, [])

  return rows
}
