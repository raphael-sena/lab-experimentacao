import { Badge } from './ui/primitives'

export function Header({ status }) {
  return (
    <header className="border-b border-slate-200/70 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/70">
      <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-teal-500 text-lg font-bold text-white shadow-sm">
              04
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
                Caracterização do Dataset
              </h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                PRs de agentes de IA vs. confirmados por humanos · Lab04S01
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {status === 'ready' && <Badge color="green">● dados reais (CSV)</Badge>}
            {status === 'mock' && <Badge color="amber">● dados mockados (fallback)</Badge>}
            {status === 'loading' && <Badge color="slate">● carregando…</Badge>}
          </div>
        </div>
      </div>
    </header>
  )
}
