import { TARGET_REPO } from '../lib/constants'

export function Header() {
  return (
    <header className="relative overflow-hidden border-b bg-[var(--paper)] print:static" style={{ borderColor: 'var(--hairline)' }}>
      {/* Marca d'água: tabuleiro de xadrez (Stockfish é um motor de xadrez). */}
      <div className="checker-watermark pointer-events-none absolute -right-10 -top-10 h-64 w-80 print:hidden" aria-hidden />

      <div className="relative mx-auto max-w-7xl px-4 pb-8 pt-10 sm:px-6 lg:px-8 print:max-w-none print:px-0 print:py-3">
        <p className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
          <span className="chess-glyphs text-base leading-none">♞</span>
          Laboratório de Experimentação de Software · Lab 05
        </p>
        <h1 className="display mt-3 max-w-4xl text-4xl leading-[1.05] text-[var(--ink)] sm:text-5xl lg:text-6xl">
          GraphQL <span className="text-[var(--muted)]">vs.</span> REST
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-[var(--body)]">
          Um experimento controlado pareado medindo <strong className="font-semibold text-[var(--ink)]">tempo de
          resposta</strong> e <strong className="font-semibold text-[var(--ink)]">tamanho do payload</strong> nas
          APIs do GitHub, sobre <span className="font-mono text-sm">{TARGET_REPO}</span> — o motor de xadrez de
          código aberto.
        </p>
        <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-1 text-xs text-[var(--muted)]">
          <span className="dotted pb-0.5">4 endpoints · 2 paradigmas · 487 medições</span>
          <span className="dotted pb-0.5">Testes não-paramétricos (Mann-Whitney U · Cliff's δ)</span>
          <span className="dotted pb-0.5">Análise computada no navegador</span>
        </div>
      </div>
    </header>
  )
}
