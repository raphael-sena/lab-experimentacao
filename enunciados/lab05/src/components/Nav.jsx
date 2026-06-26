import { SECTIONS } from '../lib/constants'

export function Nav({ active, onPrint }) {
  return (
    <nav className="flex items-center justify-between gap-4">
      <div className="no-scrollbar flex items-center gap-1 overflow-x-auto overflow-y-hidden">
        <a
          href="#top"
          title="Lab 05 · Stockfish"
          className="chess-glyphs mr-2 flex h-7 w-7 shrink-0 items-center justify-center rounded bg-stone-900 text-base leading-none text-white"
        >
          ♞
        </a>
        {SECTIONS.map((s) => {
          const isActive = active === s.id
          return (
            <a
              key={s.id}
              href={`#${s.id}`}
              className={
                'relative shrink-0 whitespace-nowrap rounded px-2.5 py-1.5 text-xs font-medium transition ' +
                (isActive ? 'text-[var(--ink)]' : 'text-[var(--muted)] hover:text-[var(--ink)]')
              }
            >
              <span className="mr-1 tabular-nums text-[var(--faint)]">{s.n}</span>
              {s.label}
              {isActive && (
                <span className="absolute inset-x-2 bottom-0 h-[2px] rounded-full bg-[var(--accent)]" />
              )}
            </a>
          )
        })}
      </div>
      <button
        type="button"
        onClick={onPrint}
        className="no-print inline-flex shrink-0 items-center gap-1.5 rounded-md bg-stone-900 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-stone-700"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <polyline points="6 9 6 2 18 2 18 9" />
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
          <rect x="6" y="14" width="12" height="8" />
        </svg>
        PDF
      </button>
    </nav>
  )
}
