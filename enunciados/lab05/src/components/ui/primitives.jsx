// Componentes de UI editoriais (Tailwind CSS v4 + tokens em index.css).
import { useCountUp } from '../../hooks/useCountUp'

export function Card({ className = '', children, allowBreak = false, hover = false }) {
  const breakCls = allowBreak ? '' : 'print:break-inside-avoid '
  const hoverCls = hover ? 'transition-shadow hover:shadow-[0_1px_18px_rgba(28,25,23,0.06)] ' : ''
  return (
    <div
      className={
        'rounded-lg border bg-[var(--paper)] ' +
        breakCls +
        hoverCls +
        className
      }
      style={{ borderColor: 'var(--hairline)' }}
    >
      {children}
    </div>
  )
}

/** Cabeçalho de seção com numeração de revista e régua. */
export function Section({ id, n, title, subtitle, children, action }) {
  return (
    <section id={id} className="scroll-mt-24">
      <div className="mb-4 print:break-after-avoid">
        <div className="mb-3 flex items-center gap-2">
          <span className="checker-ribbon h-2.5 w-16 shrink-0 rounded-[1px]" aria-hidden />
          <span className="h-px flex-1" style={{ background: 'var(--hairline)' }} />
        </div>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div className="flex items-baseline gap-3">
            {n && (
              <span className="display text-sm font-semibold tabular-nums text-[var(--accent)]">
                {n}
              </span>
            )}
            <div>
              <h2 className="display text-xl text-[var(--ink)] sm:text-2xl">{title}</h2>
              {subtitle && (
                <p className="mt-1 max-w-3xl text-sm leading-relaxed text-[var(--muted)]">{subtitle}</p>
              )}
            </div>
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      </div>
      {children}
    </section>
  )
}

/** KPI editorial: número grande serifado com count-up animado. */
export function KpiCard({ label, value, target, sublabel, format = (v) => v, accent }) {
  const [ref, animated] = useCountUp(Number.isFinite(target) ? target : 0)
  const display = Number.isFinite(target) ? format(animated) : value
  return (
    <div ref={ref} className="fade-up py-1">
      <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">{label}</p>
      <p
        className="display mt-1 text-4xl leading-none tabular-nums sm:text-5xl"
        style={{ color: accent || 'var(--ink)' }}
      >
        {display}
      </p>
      {sublabel && <p className="mt-2 text-xs leading-snug text-[var(--faint)]">{sublabel}</p>}
    </div>
  )
}

export function Badge({ children, color = 'slate' }) {
  const map = {
    slate: 'bg-stone-100 text-stone-600',
    green: 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200',
    amber: 'bg-amber-50 text-amber-800 ring-1 ring-amber-200',
    red: 'bg-red-50 text-red-800 ring-1 ring-red-200',
    ink: 'bg-stone-900 text-white',
  }
  return (
    <span className={'inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ' + map[color]}>
      {children}
    </span>
  )
}

export function ChartFrame({ title, hint, children, height = 300, action }) {
  return (
    <Card className="p-5 print:break-inside-avoid" hover>
      <div className="mb-1 flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-[var(--ink)]">{title}</h3>
        {action}
      </div>
      {hint && <p className="mb-4 text-xs leading-snug text-[var(--faint)]">{hint}</p>}
      <div style={{ width: '100%', height }}>{children}</div>
    </Card>
  )
}

export function Loader({ error }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      {error ? (
        <>
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-red-700">!</div>
          <div>
            <p className="font-medium text-[var(--ink)]">Não foi possível ler o conjunto de dados</p>
            <p className="mt-1 max-w-md text-sm text-[var(--muted)]">{error}</p>
          </div>
        </>
      ) : (
        <>
          <div className="h-9 w-9 animate-spin rounded-full border-2 border-stone-200 border-t-stone-800" />
          <p className="font-medium text-[var(--ink)]">Lendo e analisando as medições…</p>
        </>
      )}
    </div>
  )
}

/** Segmented control minimalista. */
export function Toggle({ options, value, onChange, label }) {
  return (
    <div className="no-print inline-flex items-center gap-2">
      {label && <span className="text-[11px] uppercase tracking-wide text-[var(--faint)]">{label}</span>}
      <div className="inline-flex rounded-md border p-0.5" style={{ borderColor: 'var(--hairline)' }}>
        {options.map((o) => (
          <button
            key={o.value}
            type="button"
            onClick={() => onChange(o.value)}
            className={
              'rounded px-2.5 py-1 text-xs font-medium transition ' +
              (value === o.value
                ? 'bg-stone-900 text-white'
                : 'text-[var(--muted)] hover:text-[var(--ink)]')
            }
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}

/** Chip de filtro com ponto de cor — usado no filtro de endpoints. */
export function Chip({ active, color, onClick, children, dimmed }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        'no-print inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition ' +
        (active
          ? 'border-stone-900 bg-stone-900 text-white'
          : dimmed
            ? 'border-[var(--hairline)] bg-white text-[var(--faint)] hover:text-[var(--ink)]'
            : 'border-[var(--hairline)] bg-white text-[var(--body)] hover:border-stone-400')
      }
    >
      {color && (
        <span
          className="h-2 w-2 rounded-full"
          style={{ background: active ? '#fff' : color, opacity: dimmed ? 0.4 : 1 }}
        />
      )}
      {children}
    </button>
  )
}
