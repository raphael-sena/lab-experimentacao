import { Badge } from './ui/primitives'

export function Header({ status, onPrint }) {
  return (
    <header className="border-b border-slate-200/70 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/70 print:static print:bg-white print:backdrop-blur-none">
      <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8 print:max-w-none print:px-0 print:py-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-teal-500 text-lg font-bold text-white shadow-sm">
              04
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
                Caracterização do Dataset &amp; Questões de Pesquisa
              </h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                PRs de agentes de IA vs. confirmados por humanos · Lab04 — Dashboard final
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="no-print flex items-center gap-2">
              {status === 'ready' && <Badge color="green">● dados reais (CSV)</Badge>}
              {status === 'mock' && <Badge color="amber">● dados mockados (fallback)</Badge>}
              {status === 'loading' && <Badge color="slate">● carregando…</Badge>}
            </div>
            <button
              type="button"
              onClick={onPrint}
              className="no-print inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="6 9 6 2 18 2 18 9" />
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
                <rect x="6" y="14" width="12" height="8" />
              </svg>
              Salvar em PDF
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
