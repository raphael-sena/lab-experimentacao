"""
generate_report.py
Lê os CSVs gerados por analise_dados.py e escreve relatorio.tex em ../docs/
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
import shutil

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
HERE      = Path(__file__).resolve().parent
FIGS_DIR  = HERE / "output" / "figs"
MEDIANS_CSV   = FIGS_DIR / "medians.csv"
RQ_A_CSV      = FIGS_DIR / "rq_a_status_comparisons.csv"
RQ_B_CSV      = FIGS_DIR / "rq_b_correlations_with_reviews.csv"
DOCS_DIR  = HERE.parent / "docs"
DOCS_FIGS = DOCS_DIR / "figs"
TEX_PATH  = DOCS_DIR / "relatorio.tex"
DOCS_FIGS.mkdir(parents=True, exist_ok=True)

# Copy figures to docs/figs so LaTeX can find them
for png in FIGS_DIR.glob("*.png"):
    shutil.copy2(png, DOCS_FIGS / png.name)

# ──────────────────────────────────────────────────────────────────────────────
# Load CSVs
# ──────────────────────────────────────────────────────────────────────────────
def read_csv(path: Path) -> dict[str, dict]:
    result = {}
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row[reader.fieldnames[0]]
            result[key] = row
    return result

medians = read_csv(MEDIANS_CSV)
rq_a    = read_csv(RQ_A_CSV)
rq_b    = read_csv(RQ_B_CSV)

METRICS = [
    'changed_files', 'additions', 'deletions',
    'review_time_hours', 'description_char_count',
    'participants_count', 'comments_count',
]

# Short labels used inside tables (fit within one column)
METRIC_LABELS = {
    'changed_files':          'Arquivos alterados',
    'additions':              'Adições (linhas)',
    'deletions':              'Deleções (linhas)',
    'review_time_hours':      'Tempo de revisão (h)',
    'description_char_count': 'Tamanho da descrição',
    'participants_count':     'Participantes',
    'comments_count':         'Comentários',
}

# Figure file stems
BOX_FIGS = {
    'changed_files':          'box_changed_files',
    'additions':              'box_additions',
    'deletions':              'box_deletions',
    'review_time_hours':      'box_review_time_hours',
    'description_char_count': 'box_description_char_count',
    'participants_count':     'box_participants_count',
    'comments_count':         'box_comments_count',
}

SCATTER_FIGS = {
    'changed_files':          'scatter_reviews_changed_files',
    'additions':              'scatter_reviews_additions',
    'deletions':              'scatter_reviews_deletions',
    'review_time_hours':      'scatter_reviews_review_time_hours',
    'description_char_count': 'scatter_reviews_description_char_count',
    'participants_count':     'scatter_reviews_participants_count',
    'comments_count':         'scatter_reviews_comments_count',
}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _f(v, decimals=2):
    try:
        val = float(v)
        if math.isnan(val):
            return "n/a"
        return f"{val:.{decimals}f}".replace(".", ",")
    except (ValueError, TypeError):
        return "n/a"

def _sci(v):
    try:
        val = float(v)
        if math.isnan(val):
            return "n/a"
        if val == 0.0 or val < 0.001:
            return "$<$0,001"
        return _f(val, 4)
    except (ValueError, TypeError):
        return "n/a"

def sig(pval_str):
    try:
        p = float(pval_str)
        if p < 0.001:  return "***"
        if p < 0.01:   return "**"
        if p < 0.05:   return "*"
        return "ns"
    except (ValueError, TypeError):
        return "n/a"

def direction_rqa(metric):
    """MERGED tendência: U > expected  →  MERGED tem valores maiores."""
    n_merged = int(float(rq_a[metric]['n_merged']))
    n_closed = int(float(rq_a[metric]['n_closed']))
    u = float(rq_a[metric]['stat'])
    return r"M $>$ C" if u > n_merged * n_closed / 2 else r"M $<$ C"

def direction_rqb(metric):
    rho = float(rq_b[metric]['rho'])
    return "positiva" if rho > 0 else "negativa"

# Computed counts
n_prs    = int(float(rq_a['changed_files']['n_merged'])) + int(float(rq_a['changed_files']['n_closed']))
n_merged = int(float(rq_a['changed_files']['n_merged']))
n_closed = int(float(rq_a['changed_files']['n_closed']))
n_repos  = 200

def fmt_n(n): return f"{n:,}".replace(",", ".")

# ──────────────────────────────────────────────────────────────────────────────
# Table rows
# ──────────────────────────────────────────────────────────────────────────────
medians_table = ""
for m in METRICS:
    med = _f(medians[m]['median'])
    medians_table += f"    {METRIC_LABELS[m]} & {med} \\\\\n"

# RQ_A table: 3 cols only (Métrica | Sig. | Tendência)
# p-value is always *** so we skip the raw value to save column width.
rq_a_table = ""
for m in METRICS:
    s = sig(rq_a[m]['pvalue'])
    d = direction_rqa(m)
    rq_a_table += f"    {METRIC_LABELS[m]} & {s} & {d} \\\\\n"

# RQ_B table: 3 cols (Métrica | ρ | Sig.)
# All directions are "positiva" so we drop that column too.
rq_b_table = ""
for m in METRICS:
    rho = _f(rq_b[m]['rho'], 3)
    s   = sig(rq_b[m]['pvalue'])
    rq_b_table += f"    {METRIC_LABELS[m]} & {rho} & {s} \\\\\n"

# ──────────────────────────────────────────────────────────────────────────────
# Per-metric discussion bullets
# ──────────────────────────────────────────────────────────────────────────────
def rqa_blurb(m):
    s = sig(rq_a[m]['pvalue'])
    d = direction_rqa(m).replace(r"M $>$ C", "MERGED $>$ CLOSED").replace(r"M $<$ C", "MERGED $<$ CLOSED")
    label = METRIC_LABELS[m]
    if s in ("***", "**", "*"):
        return (
            f"\\textbf{{{label}}} --- diferença significativa ({s}): {d}."
        )
    return f"\\textbf{{{label}}} --- sem diferença significativa entre os grupos."

def rqb_blurb(m):
    rho_val = float(rq_b[m]['rho'])
    s       = sig(rq_b[m]['pvalue'])
    label   = METRIC_LABELS[m]
    strength = "fraca" if abs(rho_val) < 0.2 else ("moderada" if abs(rho_val) < 0.4 else "forte")
    if s in ("***", "**", "*"):
        return (
            f"\\textbf{{{label}}} --- correlação {strength} e positiva "
            f"($\\rho = {_f(rho_val, 3)}$, {s})."
        )
    return f"\\textbf{{{label}}} --- correlação não significativa ($\\rho = {_f(rho_val, 3)}$)."

rqa_bullets = "\n".join(f"  \\item {rqa_blurb(m)}" for m in METRICS)
rqb_bullets = "\n".join(f"  \\item {rqb_blurb(m)}" for m in METRICS)

# ──────────────────────────────────────────────────────────────────────────────
# Figure blocks — each metric gets its own figure[H] (column-width)
# Organised in pairs (two subfigures side-by-side) inside figure[H]
# ──────────────────────────────────────────────────────────────────────────────
def box_caption(m):
    d = direction_rqa(m).replace(r"M $>$ C", "MERGED $>$ CLOSED").replace(r"M $<$ C", "MERGED $<$ CLOSED")
    s = sig(rq_a[m]['pvalue'])
    return f"{METRIC_LABELS[m]} ({s}; {d})"

def scatter_caption(m):
    rho_val = float(rq_b[m]['rho'])
    s = sig(rq_b[m]['pvalue'])
    return f"{METRIC_LABELS[m]} ($\\rho={_f(rho_val, 3)}$, {s})"

def paired_figures(metrics_list, fig_map, caption_fn, label_prefix, global_caption):
    """
    Emit pairs of subfigures inside figure[H] environments.
    metrics_list  – list of metric keys
    fig_map       – dict metric -> filename stem (without .png)
    caption_fn    – callable metric -> subfigure caption string
    label_prefix  – string prefix for the LaTeX label
    global_caption – caption for the whole pair figure
    """
    blocks = []
    pairs = [metrics_list[i:i+2] for i in range(0, len(metrics_list), 2)]
    for idx, pair in enumerate(pairs):
        label = f"{label_prefix}{idx+1}"
        lines = [
            r"\begin{figure}[H]",
            r"  \centering",
        ]
        width = r"0.48\columnwidth"
        for i, m in enumerate(pair):
            fname = fig_map[m]
            cap   = caption_fn(m)
            lines.append(f"  \\begin{{subfigure}}[b]{{{width}}}")
            lines.append(f"    \\includegraphics[width=\\textwidth]{{figs/{fname}.png}}")
            lines.append(f"    \\caption{{{cap}}}")
            lines.append( "  \\end{subfigure}")
            if i == 0 and len(pair) > 1:
                lines.append(r"  \hfill")
        lines.append(f"  \\caption{{{global_caption} (cont.)}}" if idx > 0 else f"  \\caption{{{global_caption}}}")
        lines.append(f"  \\label{{{label}}}")
        lines.append(r"\end{figure}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)

box_figures = paired_figures(
    METRICS, BOX_FIGS, box_caption,
    "fig:box",
    r"Distribuição por status (MERGED vs.\ CLOSED). Sig.: *** $p<0{,}001$. "
    r"M\,=\,MERGED, C\,=\,CLOSED"
)

scatter_figures = paired_figures(
    METRICS, SCATTER_FIGS, scatter_caption,
    "fig:scat",
    r"Dispersão entre cada métrica e o número de revisões formais. "
    r"Sig.: *** $p<0{,}001$"
)

# ──────────────────────────────────────────────────────────────────────────────
# Generate LaTeX
# ──────────────────────────────────────────────────────────────────────────────
TEX = r"""\documentclass[10pt,a4paper,twocolumn]{article}

% ── Encoding & Language ──────────────────────────────────────────────────────
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

% ── Layout ───────────────────────────────────────────────────────────────────
\usepackage[top=2.3cm, bottom=2.3cm, left=2.0cm, right=2.0cm]{geometry}
\usepackage{setspace}
\setstretch{1.08}
\usepackage{indentfirst}
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{0pt}
\setlength{\columnsep}{0.7cm}
\setlength{\emergencystretch}{3em}

% ── Fonts & Typography ───────────────────────────────────────────────────────
\usepackage{lmodern}
\usepackage{microtype}

% ── Graphics & Tables ────────────────────────────────────────────────────────
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{float}
\usepackage{array}
\usepackage{xcolor}
\usepackage{tabularx}
\usepackage{dblfloatfix}

% ── Math ─────────────────────────────────────────────────────────────────────
\usepackage{amsmath}

% ── Hyperlinks ───────────────────────────────────────────────────────────────
\usepackage[hidelinks,hypertexnames=false]{hyperref}
\renewcommand{\contentsname}{Sumário}

% ── Headers & Footers ────────────────────────────────────────────────────────
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Laboratório de Experimentação de Software}
\fancyhead[R]{\small PUC Minas -- 2026/1}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{14pt}
\renewcommand{\headrulewidth}{0.4pt}

% ─────────────────────────────────────────────────────────────────────────────
\begin{document}

\onecolumn

% ── Capa ─────────────────────────────────────────────────────────────────────
\begin{titlepage}
  \centering
  \vspace*{2.0cm}

  {\normalsize
    Pontifícia Universidade Católica de Minas Gerais (PUC~Minas)\\
    Laboratório de Experimentação de Software -- 2026/1
  }

  \vspace*{2.8cm}

  {\large
    Raphael Brito\\[0.3em]
    Yan Cota
  }

  \vspace*{4.2cm}

  {\LARGE \textbf{Laboratório 03}\\[0.5em]
  \Large Caracterizando a Atividade de Code Review no GitHub}

  \vfill

  {\normalsize Belo Horizonte\\ 2026}
\end{titlepage}

% ── Sumário ──────────────────────────────────────────────────────────────────
\pagenumbering{roman}
\tableofcontents
\newpage
\pagenumbering{arabic}
\setcounter{page}{1}
\twocolumn

% ─────────────────────────────────────────────────────────────────────────────
\section{Introdução}
% ─────────────────────────────────────────────────────────────────────────────

O processo de \textit{code review} -- revisão formal de código por pares -- é
amplamente reconhecido como uma das práticas mais efetivas para garantir
qualidade e disseminar conhecimento em projetos de software.
Plataformas como o GitHub popularizaram o modelo de \textit{pull requests}
(PRs), em que uma contribuição passa por discussão e aprovação antes de ser
integrada ao código principal.

Neste laboratório analisamos \textbf{""" + fmt_n(n_prs) + r"""\,\textit{pull requests}}
coletados dos \textbf{""" + str(n_repos) + r""" repositórios mais populares} do GitHub (medidos
por número de estrelas), investigando como características dos PRs se
relacionam com seu desfecho final (\textit{merged} ou \textit{closed}) e com
o volume de revisões recebidas.

\section{Questões de Pesquisa e Hipóteses}

Antes de analisar os dados, levantamos as seguintes hipóteses:

\begin{description}
  \item[\textbf{H$_{\text{A}}$ -- Características e status final}]
    Esperamos que PRs \textit{merged} apresentem menor número de arquivos
    alterados, menor tamanho de diff e descrições mais completas, pois
    mudanças bem documentadas e de escopo reduzido tendem a ser aceitas com
    mais facilidade pelos revisores.

  \item[\textbf{H$_{\text{B}}$ -- Características e número de revisões}]
    Esperamos que PRs com mais participantes e comentários também recebam
    mais revisões formais, pois discussões ativas costumam envolver ciclos
    iterativos de revisão.
\end{description}

% ─────────────────────────────────────────────────────────────────────────────
\section{Objetivos}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{Objetivo Geral}

Caracterizar a atividade de \textit{code review} nos repositórios mais
populares do GitHub, identificando fatores associados à aprovação de PRs e
ao volume de revisões recebidas.

\subsection{Objetivos Específicos}

\begin{itemize}
  \item Comparar distribuições de métricas de PRs entre os grupos MERGED e
    CLOSED usando o teste de Mann-Whitney~U.
  \item Correlacionar características dos PRs com o número de revisões
    recebidas via coeficiente de Spearman.
  \item Identificar quais fatores estão mais fortemente associados ao
    desfecho e ao engajamento no processo de revisão.
\end{itemize}

% ─────────────────────────────────────────────────────────────────────────────
\section{Metodologia}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{Coleta de Dados}

A coleta foi realizada em duas etapas:

\begin{enumerate}
  \item \textbf{Seleção de repositórios:} via \textbf{API GraphQL do GitHub},
    coletamos os """ + str(n_repos) + r""" repositórios mais populares (por estrelas),
    filtrando aqueles com no mínimo 100 PRs mergeados ou fechados.

  \item \textbf{Coleta de PRs:} para cada repositório foram coletados os
    últimos PRs com status \textit{MERGED} ou \textit{CLOSED}, registrando:
    número de arquivos alterados, linhas adicionadas e removidas, tempo de
    revisão (horas entre abertura e encerramento), tamanho da descrição
    (em caracteres), número de participantes, de comentários e de revisões
    formais.
\end{enumerate}

O dataset final contém """ + fmt_n(n_prs) + r""" PRs: """ + fmt_n(n_merged) + r""" MERGED e
""" + fmt_n(n_closed) + r""" CLOSED.

\subsection{Análise}

\paragraph{RQ$_A$ -- Status do PR.}
Distribuições de cada métrica nos grupos MERGED e CLOSED foram comparadas
com o \textbf{teste de Mann-Whitney~U} (bicaudal), não-paramétrico e robusto
a outliers. Significância: $p < 0{,}001$ (***), $p < 0{,}01$ (**),
$p < 0{,}05$ (*) e $p \geq 0{,}05$ (ns).

\paragraph{RQ$_B$ -- Número de revisões.}
Para cada métrica calculamos o \textbf{coeficiente de correlação de
Spearman} ($\rho$) em relação ao número de revisões formais do PR.

% ─────────────────────────────────────────────────────────────────────────────
\section{Resultados}
% ─────────────────────────────────────────────────────────────────────────────

A Tabela~\ref{tab:medians} apresenta as medianas globais de cada métrica.

\begin{table}[H]
  \centering
  \caption{Medianas globais das métricas de PRs.}
  \label{tab:medians}
  \begin{tabular}{lr}
    \toprule
    \textbf{Métrica} & \textbf{Mediana} \\
    \midrule
""" + medians_table + r"""    \bottomrule
  \end{tabular}
\end{table}

% ─────────────────────────────────────────────────────────────────────────────
\subsection{RQ$_A$ -- Relação entre características e status final}
% ─────────────────────────────────────────────────────────────────────────────

A Tabela~\ref{tab:rqa} resume os resultados do teste de Mann-Whitney~U.
Todas as métricas apresentaram diferença significativa ($p < 0{,}001$).
A coluna \textbf{Tend.} indica se PRs MERGED (M) têm valores maiores ou
menores que CLOSED (C).

\begin{table}[H]
  \centering
  \caption{Mann-Whitney U: MERGED vs.\ CLOSED. Todas as diferenças com $p<0{,}001$ (***).}
  \label{tab:rqa}
  \small
  \begin{tabular}{lll}
    \toprule
    \textbf{Métrica} & \textbf{Sig.} & \textbf{Tend.} \\
    \midrule
""" + rq_a_table + r"""    \bottomrule
  \end{tabular}
\end{table}

Os boxplots a seguir comparam as distribuições de cada métrica entre os
dois grupos. Cada par de figuras é identificado com a significância e a
direção da diferença:

""" + box_figures + r"""

\begin{itemize}
""" + rqa_bullets + r"""
\end{itemize}

% ─────────────────────────────────────────────────────────────────────────────
\subsection{RQ$_B$ -- Relação entre características e número de revisões}
% ─────────────────────────────────────────────────────────────────────────────

A Tabela~\ref{tab:rqb} apresenta as correlações de Spearman com o número
de revisões. Todas as correlações são positivas e estatisticamente
significativas.

\begin{table}[H]
  \centering
  \caption{Correlações de Spearman com o número de revisões (todas positivas).}
  \label{tab:rqb}
  \small
  \begin{tabular}{lrl}
    \toprule
    \textbf{Métrica} & $\boldsymbol{\rho}$ & \textbf{Sig.} \\
    \midrule
""" + rq_b_table + r"""    \bottomrule
  \end{tabular}
\end{table}

Os gráficos de dispersão abaixo mostram a relação de cada métrica com o
número de revisões. O valor de $\rho$ de Spearman e a significância
estão indicados em cada legenda:

""" + scatter_figures + r"""

\begin{itemize}
""" + rqb_bullets + r"""
\end{itemize}

% ─────────────────────────────────────────────────────────────────────────────
\section{Discussão dos Resultados}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{Insights Principais}

\begin{itemize}
  \item \textbf{Diff menor favorece aprovação:} PRs MERGED apresentam, em
    mediana, menos arquivos alterados, adições e deleções. Mudanças de
    escopo reduzido são mais fáceis de revisar e têm maior taxa de
    aceitação.

  \item \textbf{PRs rejeitados ficam abertos por mais tempo:} o tempo de
    revisão é significativamente maior em PRs CLOSED, sugerindo que PRs
    problemáticos ficam estagnados ou que a demora desencoraja o autor.

  \item \textbf{Descrição importa:} PRs MERGED possuem descrições mais
    extensas, indicando que documentar adequadamente a mudança facilita
    a aprovação.

  \item \textbf{Engajamento impulsiona revisões:} participantes e
    comentários têm as maiores correlações com o número de revisões
    ($\rho \approx 0{,}33$ e $0{,}31$). Discussões mais ativas geram mais
    ciclos formais de revisão.

  \item \textbf{Tamanho do diff tem efeito moderado:} adições e tamanho
    da descrição correlacionam moderadamente ($\rho \approx 0{,}21$ e
    $0{,}20$); deleções e tempo de revisão têm efeito menor
    ($\rho \approx 0{,}11$).
\end{itemize}

\subsection{Implicações para Equipes de Desenvolvimento}

Os resultados sugerem práticas concretas: (i)~manter PRs pequenos e
focados aumenta a chance de aprovação; (ii)~descrições detalhadas
facilitam o processo de revisão; (iii)~engajar colaboradores nos
comentários aprofunda o ciclo formal de revisão.

% ─────────────────────────────────────────────────────────────────────────────
% Conclusão — mantida em duas colunas para fluxo contínuo com o restante.
% ─────────────────────────────────────────────────────────────────────────────
\section{Conclusão e Resposta às Hipóteses}
% ─────────────────────────────────────────────────────────────────────────────

A análise de """ + fmt_n(n_prs) + r""" PRs dos repositórios mais populares do GitHub revelou que:

\begin{itemize}
  \item \textbf{Status final (RQ$_A$):} todas as métricas avaliadas
    apresentaram diferença estatisticamente significativa entre PRs MERGED
    e CLOSED. PRs aprovados tendem a ter diffs menores, descrições mais
    completas e menor tempo até o encerramento.
    A hipótese H$_A$ é \textbf{confirmada}.

  \item \textbf{Número de revisões (RQ$_B$):} as correlações mais fortes
    com o número de revisões são participantes e comentários, seguidos pelo
    tamanho do diff e da descrição. A hipótese H$_B$ é
    \textbf{confirmada}, especialmente quanto ao papel do engajamento.
\end{itemize}

\subsection{Tomadas de Decisão}

Com base nas evidências, recomendamos: (i)~limitar o escopo dos PRs para
facilitar revisão e aprovação; (ii)~investir em descrições que
contextualizem a mudança; (iii)~encorajar a participação de múltiplos
revisores desde o início; e (iv)~monitorar PRs com tempo de revisão
elevado como indicador de problemas de processo.

\subsection{Respondendo às Hipóteses}

A Tabela~\ref{tab:hipoteses} sintetiza o resultado de cada hipótese.

\begin{table}[H]
  \centering
  \caption{Síntese de confirmação das hipóteses.}
  \label{tab:hipoteses}
  \small
  \begin{tabularx}{\columnwidth}{lXl}
    \toprule
    Hip. & Descrição resumida & Status \\
    \midrule
    H$_A$ & PRs MERGED têm diffs menores e descrições mais completas. & Confirmada \\
    H$_B$ & Mais participantes e comentários $\Rightarrow$ mais revisões. & Confirmada \\
    \bottomrule
  \end{tabularx}
\end{table}

\end{document}
"""

TEX_PATH.write_text(TEX, encoding="utf-8")
print(f"LaTeX report written to: {TEX_PATH}")
print("Done!")
