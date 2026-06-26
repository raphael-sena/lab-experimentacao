import { useLayoutEffect, useRef, useState } from 'react'

/**
 * Mede a largura de um elemento via ResizeObserver e a retorna.
 *
 * Usado para dimensionar os gráficos com largura/altura EXPLÍCITAS (em px),
 * em vez do ResponsiveContainer do Recharts. Isso é essencial para a
 * exportação em PDF: o ResponsiveContainer re-mede de forma assíncrona e
 * "colapsa" (renderiza vazio) no instante da impressão; dimensões fixas
 * gravadas no SVG são preservadas no papel.
 */
export function useElementWidth(initial = 640) {
  const ref = useRef(null)
  const [width, setWidth] = useState(initial)
  useLayoutEffect(() => {
    if (!ref.current) return
    const el = ref.current
    const update = () => setWidth(el.clientWidth || initial)
    update()
    const ro = new ResizeObserver(update)
    ro.observe(el)
    return () => ro.disconnect()
  }, [initial])
  return [ref, width]
}
