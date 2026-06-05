// Componentes de UI reutilizáveis estilizados com Tailwind CSS v4.

export function Card({ className = '', children }) {
  return (
    <div
      className={
        'rounded-2xl border border-slate-200/70 bg-white shadow-sm ' +
        'dark:border-slate-800 dark:bg-slate-900 ' +
        className
      }
    >
      {children}
    </div>
  )
}

export function Section({ id, title, subtitle, children, action }) {
  return (
    <section id={id} className="scroll-mt-20">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
          {subtitle && (
            <p className="mt-0.5 max-w-2xl text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
          )}
        </div>
        {action}
      </div>
      {children}
    </section>
  )
}

export function KpiCard({ label, value, sublabel, accent = 'indigo', icon }) {
  const accents = {
    indigo: 'from-indigo-500/10 text-indigo-600 dark:text-indigo-400',
    teal: 'from-teal-500/10 text-teal-600 dark:text-teal-400',
    amber: 'from-amber-500/10 text-amber-600 dark:text-amber-400',
    rose: 'from-rose-500/10 text-rose-600 dark:text-rose-400',
    sky: 'from-sky-500/10 text-sky-600 dark:text-sky-400',
    violet: 'from-violet-500/10 text-violet-600 dark:text-violet-400',
  }
  return (
    <Card className="overflow-hidden">
      <div className={'bg-gradient-to-br to-transparent p-5 ' + accents[accent]}>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            {label}
          </p>
          {icon && <span className="text-base opacity-80">{icon}</span>}
        </div>
        <p className="mt-2 text-3xl font-bold tabular-nums text-slate-900 dark:text-slate-50">
          {value}
        </p>
        {sublabel && (
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{sublabel}</p>
        )}
      </div>
    </Card>
  )
}

export function Badge({ children, color = 'slate' }) {
  const colors = {
    slate: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
    green: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
    amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
    indigo: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
  }
  return (
    <span className={'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ' + colors[color]}>
      {children}
    </span>
  )
}

export function ChartFrame({ title, hint, children, height = 300 }) {
  return (
    <Card className="p-5">
      <div className="mb-1 flex items-baseline justify-between gap-2">
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">{title}</h3>
      </div>
      {hint && <p className="mb-3 text-xs text-slate-400">{hint}</p>}
      <div style={{ width: '100%', height }}>{children}</div>
    </Card>
  )
}

export function Loader({ processed }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-500" />
      <div>
        <p className="font-medium text-slate-700 dark:text-slate-200">
          Lendo e agregando o dataset…
        </p>
        <p className="mt-1 text-sm tabular-nums text-slate-500">
          {processed > 0
            ? `${processed.toLocaleString('pt-BR')} registros processados`
            : 'Iniciando o leitor de CSV (Web Worker)…'}
        </p>
      </div>
    </div>
  )
}
