import { useEffect, useRef, useState } from 'react'

/**
 * Anima um número de 0 até `target` com easing, ao entrar na viewport.
 * Respeita `prefers-reduced-motion`. Retorna [ref, valorAnimado].
 */
export function useCountUp(target, duration = 1100) {
  const [value, setValue] = useState(0)
  const ref = useRef(null)
  const started = useRef(false)

  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (!Number.isFinite(target)) return
    if (reduce) {
      setValue(target)
      return
    }
    const el = ref.current
    if (!el) {
      setValue(target)
      return
    }
    const run = () => {
      if (started.current) return
      started.current = true
      const t0 = performance.now()
      const tick = (now) => {
        const p = Math.min((now - t0) / duration, 1)
        const eased = 1 - Math.pow(1 - p, 3) // easeOutCubic
        setValue(target * eased)
        if (p < 1) requestAnimationFrame(tick)
      }
      requestAnimationFrame(tick)
    }
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && run()),
      { threshold: 0.4 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [target, duration])

  return [ref, value]
}
