import { API_COLORS, API_TYPES, ENDPOINTS } from '../lib/constants'
import { Chip } from './ui/primitives'

/**
 * Barra de filtro global: foco por endpoint (multi-seleção) e visibilidade das
 * séries REST/GraphQL. Controla TODOS os gráficos, tabelas e cartões de RQ.
 */
export function Filters({ focus, onToggleEndpoint, onClearFocus, apiVisible, onToggleApi }) {
  const focused = focus.size > 0
  return (
    <div className="no-print flex flex-wrap items-center gap-x-5 gap-y-2">
      <div className="flex items-center gap-1.5">
        <span className="mr-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--faint)]">
          Endpoints
        </span>
        <Chip active={!focused} onClick={onClearFocus}>Todos</Chip>
        {ENDPOINTS.map((ep) => (
          <Chip
            key={ep.key}
            color={ep.color}
            active={focus.has(ep.key)}
            dimmed={focused && !focus.has(ep.key)}
            onClick={() => onToggleEndpoint(ep.key)}
          >
            {ep.short}
          </Chip>
        ))}
      </div>

      <span className="hidden h-4 w-px bg-[var(--hairline)] sm:block" />

      <div className="flex items-center gap-1.5">
        <span className="mr-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--faint)]">
          Séries
        </span>
        {API_TYPES.map((api) => {
          const on = apiVisible[api]
          return (
            <button
              key={api}
              type="button"
              onClick={() => onToggleApi(api)}
              className={
                'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition ' +
                (on ? 'border-[var(--hairline)] bg-white text-[var(--ink)]' : 'border-[var(--hairline)] bg-white text-[var(--faint)] line-through')
              }
              style={on ? { borderColor: API_COLORS[api] } : undefined}
            >
              <span className="h-2.5 w-2.5 rounded-sm" style={{ background: API_COLORS[api], opacity: on ? 1 : 0.35 }} />
              {api}
            </button>
          )
        })}
      </div>
    </div>
  )
}
