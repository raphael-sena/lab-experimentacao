import { useEffect, useState } from 'react'

/**
 * Observa as seções por id e retorna o id da seção atualmente mais visível —
 * usado para destacar o item ativo na navegação sticky.
 */
export function useScrollSpy(ids, offset = 96) {
  const [active, setActive] = useState(ids[0])

  useEffect(() => {
    const handler = () => {
      const y = window.scrollY + offset + 1
      let current = ids[0]
      for (const id of ids) {
        const el = document.getElementById(id)
        if (el && el.offsetTop <= y) current = id
      }
      // Garante o último item ao chegar ao fim da página.
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 4) {
        current = ids[ids.length - 1]
      }
      setActive(current)
    }
    handler()
    window.addEventListener('scroll', handler, { passive: true })
    window.addEventListener('resize', handler)
    return () => {
      window.removeEventListener('scroll', handler)
      window.removeEventListener('resize', handler)
    }
  }, [ids, offset])

  return active
}
