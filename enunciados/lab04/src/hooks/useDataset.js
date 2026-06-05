import { useEffect, useRef, useState } from 'react'
import { DATASET_URL } from '../lib/constants'
import { MOCK_SUMMARY } from '../lib/mockSummary'

/**
 * Orquestra a leitura do CSV real em um Web Worker (com streaming/agregação)
 * e expõe estado de carregamento, progresso e o resumo final.
 *
 * Se o worker falhar ou o arquivo não existir, cai para o resumo MOCK,
 * garantindo que o dashboard sempre renderize.
 */
export function useDataset() {
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'mock'
  const [processed, setProcessed] = useState(0)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)
  const workerRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    let worker

    const fallback = (reason) => {
      if (cancelled) return
      setError(reason)
      setSummary(MOCK_SUMMARY)
      setStatus('mock')
    }

    try {
      worker = new Worker(new URL('../workers/csvWorker.js', import.meta.url), {
        type: 'module',
      })
      workerRef.current = worker

      worker.onmessage = (e) => {
        if (cancelled) return
        const msg = e.data
        if (msg.type === 'progress') {
          setProcessed(msg.processed)
        } else if (msg.type === 'done') {
          setSummary(msg)
          setStatus('ready')
          worker.terminate()
        } else if (msg.type === 'error') {
          fallback(msg.message)
          worker.terminate()
        }
      }
      worker.onerror = (e) => fallback(e.message || 'Falha no worker de leitura do CSV')

      worker.postMessage({ type: 'parse', url: DATASET_URL })
    } catch (err) {
      fallback(String(err))
    }

    return () => {
      cancelled = true
      if (worker) worker.terminate()
    }
  }, [])

  return { status, processed, summary, error }
}
