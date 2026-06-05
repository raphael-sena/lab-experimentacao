// Componentes de UI reutilizáveis estilizados com Tailwind CSS v4.

export function Card({ className = '', children, allowBreak = false }) {
  const breakCls = allowBreak ? '' : 'print:break-inside-avoid '
  return (
    <div
      className={
        'rounded border border-slate-200 bg-white ' +
        breakCls +
        'print:border-slate-300 ' +
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
      <div className="mb-3 flex flex-wrap items-end justify-between gap-2 print:break-after-avoid">
        <div>
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          {subtitle && (
            <p className="mt-0.5 max-w-2xl text-xs text-slate-500">{subtitle}</p>
          )}
        </div>
        {action}
      </div>
      {children}
    </section>
  )
}

export function KpiCard({ label, value, sublabel, accent = 'slate' }) {
  const accentColors = {
    indigo: '#1d4ed8',
    teal: '#0d9488',
    amber: '#b45309',
    rose: '#be123c',
    sky: '#0284c7',
    violet: '#6d28d9',
  }
  const borderColor = accentColors[accent] || '#64748b'
  return (
    <div
      className="rounded border border-slate-200 bg-white overflow-hidden print:border-slate-300"
      style={{ borderLeftColor: borderColor, borderLeftWidth: '3px' }}
    >
      <div className="p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {label}
        </p>
        <p className="mt-1.5 text-2xl font-bold tabular-nums text-slate-900">
          {value}
        </p>
        {sublabel && (
          <p className="mt-0.5 text-xs text-slate-400">{sublabel}</p>
        )}
      </div>
    </div>
  )
}

export function Badge({ children, color = 'slate' }) {
  const colors = {
    slate: 'bg-slate-100 text-slate-600',
    green: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    amber: 'bg-amber-50 text-amber-700 border border-amber-200',
    indigo: 'bg-blue-50 text-blue-700 border border-blue-200',
  }
  return (
    <span className={'inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ' + colors[color]}>
      {children}
    </span>
  )
}

export function ChartFrame({ title, hint, children, height = 300 }) {
  return (
    <Card className="p-4 print:break-inside-avoid">
      <div className="mb-1">
        <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      </div>
      {hint && <p className="mb-3 text-xs text-slate-400">{hint}</p>}
      <div style={{ width: '100%', height }}>{children}</div>
    </Card>
  )
}

export function Loader({ processed }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-700" />
      <div>
        <p className="font-medium text-slate-700">
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
