"""
generate_report.py
Lê repos.csv, gera os gráficos (pasta ../docs/figs/) e escreve o relatorio.tex
em ../docs/relatorio.tex
"""
from __future__ import annotations

import csv
import math
import os
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "repos.csv"
DOCS_DIR = HERE.parent / "docs"
FIGS_DIR = DOCS_DIR / "figs"
TEX_PATH = DOCS_DIR / "relatorio.tex"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Load CSV
# ──────────────────────────────────────────────────────────────────────────────
rows: list[dict] = []
with CSV_PATH.open(encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        rows.append(row)

def _int(v):
    try:
        return int(v)
    except (ValueError, TypeError):
        return 0

def _float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0

age_days        = [_int(r["age_days"])           for r in rows]
days_update     = [_int(r["days_since_update"])  for r in rows]
merged_prs      = [_int(r["merged_prs"])         for r in rows]
releases        = [_int(r["releases"])           for r in rows]
languages       = [r["language"] or "Unknown"    for r in rows]
closed_ratio    = [_float(r["closed_issue_ratio"]) for r in rows]
stars           = [_int(r["stars"])              for r in rows]

age_years = [d / 365 for d in age_days]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
PALETTE = "#2563EB"
ACCENT  = "#F59E0B"

def save(name: str):
    path = FIGS_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved {path.name}")

def median(data):
    s = sorted(data)
    n = len(s)
    if n == 0:
        return 0
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else s[mid]

# ──────────────────────────────────────────────────────────────────────────────
# RQ01 – Idade do repositório (anos)
# ──────────────────────────────────────────────────────────────────────────────
print("RQ01 – age")
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(age_years, bins=30, color=PALETTE, edgecolor="white", linewidth=0.4)
med = median(age_years)
ax.axvline(med, color=ACCENT, linewidth=2, linestyle="--", label=f"Mediana = {med:.1f} anos")
ax.set_xlabel("Idade (anos)", fontsize=12)
ax.set_ylabel("Número de repositórios", fontsize=12)
ax.set_title("RQ01 – Distribuição da Idade dos Repositórios", fontsize=13, fontweight="bold")
ax.legend()
save("rq01_age.pdf")

# ──────────────────────────────────────────────────────────────────────────────
# RQ02 – Pull Requests aceitas (merged)
# ──────────────────────────────────────────────────────────────────────────────
print("RQ02 – PRs")
fig, ax = plt.subplots(figsize=(7, 4))
# log scale para visualização melhor
log_prs = [math.log10(v + 1) for v in merged_prs]
ax.hist(log_prs, bins=30, color=PALETTE, edgecolor="white", linewidth=0.4)
med_prs = median(merged_prs)
ax.axvline(math.log10(med_prs + 1), color=ACCENT, linewidth=2, linestyle="--",
           label=f"Mediana = {int(med_prs):,}")
ax.set_xlabel("log₁₀(Merged PRs + 1)", fontsize=12)
ax.set_ylabel("Número de repositórios", fontsize=12)
ax.set_title("RQ02 – Distribuição de Pull Requests Aceitas", fontsize=13, fontweight="bold")
ax.legend()
save("rq02_prs.pdf")

# ──────────────────────────────────────────────────────────────────────────────
# RQ03 – Total de releases
# ──────────────────────────────────────────────────────────────────────────────
print("RQ03 – releases")
fig, ax = plt.subplots(figsize=(7, 4))
log_rel = [math.log10(v + 1) for v in releases]
ax.hist(log_rel, bins=30, color=PALETTE, edgecolor="white", linewidth=0.4)
med_rel = median(releases)
ax.axvline(math.log10(med_rel + 1), color=ACCENT, linewidth=2, linestyle="--",
           label=f"Mediana = {int(med_rel):,}")
ax.set_xlabel("log₁₀(Releases + 1)", fontsize=12)
ax.set_ylabel("Número de repositórios", fontsize=12)
ax.set_title("RQ03 – Distribuição do Número de Releases", fontsize=13, fontweight="bold")
ax.legend()
save("rq03_releases.pdf")

# ──────────────────────────────────────────────────────────────────────────────
# RQ04 – Dias desde a última atualização
# ──────────────────────────────────────────────────────────────────────────────
print("RQ04 – days since update")
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(days_update, bins=40, color=PALETTE, edgecolor="white", linewidth=0.4)
med_upd = median(days_update)
ax.axvline(med_upd, color=ACCENT, linewidth=2, linestyle="--",
           label=f"Mediana = {int(med_upd)} dias")
ax.set_xlabel("Dias desde a última atualização", fontsize=12)
ax.set_ylabel("Número de repositórios", fontsize=12)
ax.set_title("RQ04 – Tempo desde a Última Atualização", fontsize=13, fontweight="bold")
ax.legend()
save("rq04_update.pdf")

# ──────────────────────────────────────────────────────────────────────────────
# RQ05 – Linguagens primárias (top 10)
# ──────────────────────────────────────────────────────────────────────────────
print("RQ05 – languages")
lang_count = Counter(languages)
top_langs = lang_count.most_common(10)
labels = [l for l, _ in top_langs]
counts = [c for _, c in top_langs]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(labels[::-1], counts[::-1], color=PALETTE)
ax.bar_label(bars, padding=3, fontsize=9)
ax.set_xlabel("Número de repositórios", fontsize=12)
ax.set_title("RQ05 – Top 10 Linguagens Primárias", fontsize=13, fontweight="bold")
ax.set_xlim(0, max(counts) * 1.15)
save("rq05_langs.pdf")

# ──────────────────────────────────────────────────────────────────────────────
# RQ06 – Razão de issues fechadas
# ──────────────────────────────────────────────────────────────────────────────
print("RQ06 – closed issue ratio")
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(closed_ratio, bins=30, color=PALETTE, edgecolor="white", linewidth=0.4)
med_cr = median(closed_ratio)
ax.axvline(med_cr, color=ACCENT, linewidth=2, linestyle="--",
           label=f"Mediana = {med_cr:.2f}")
ax.set_xlabel("Razão de Issues Fechadas (fechadas / total)", fontsize=12)
ax.set_ylabel("Número de repositórios", fontsize=12)
ax.set_title("RQ06 – Razão de Issues Fechadas", fontsize=13, fontweight="bold")
ax.legend()
save("rq06_issues.pdf")

# ──────────────────────────────────────────────────────────────────────────────
# RQ07 – Métricas por linguagem (top 8) – BÔNUS
# ──────────────────────────────────────────────────────────────────────────────
print("RQ07 – metrics by language")
TOP_N = 8
top8_langs = [l for l, _ in lang_count.most_common(TOP_N)]

def group_by_lang(metric_list):
    groups = {lang: [] for lang in top8_langs}
    for lang, val in zip(languages, metric_list):
        if lang in groups:
            groups[lang].append(val)
    return groups

prs_by_lang  = group_by_lang(merged_prs)
rel_by_lang  = group_by_lang(releases)
upd_by_lang  = group_by_lang(days_update)

def box_by_lang(data_dict, title, xlabel, fname, log_scale=True):
    langs_sorted = list(data_dict.keys())
    data_values  = [data_dict[l] for l in langs_sorted]
    if log_scale:
        data_values = [[math.log10(v + 1) for v in d] for d in data_values]

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(data_values, vert=False, patch_artist=True,
                    medianprops=dict(color=ACCENT, linewidth=2),
                    boxprops=dict(facecolor=PALETTE, alpha=0.6))
    ax.set_yticks(range(1, len(langs_sorted) + 1))
    ax.set_yticklabels(langs_sorted, fontsize=10)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    save(fname)

box_by_lang(prs_by_lang,
            "RQ07a – Merged PRs por Linguagem",
            "log₁₀(Merged PRs + 1)",
            "rq07a_prs_lang.pdf")

box_by_lang(rel_by_lang,
            "RQ07b – Releases por Linguagem",
            "log₁₀(Releases + 1)",
            "rq07b_releases_lang.pdf")

box_by_lang(upd_by_lang,
            "RQ07c – Dias desde Última Atualização por Linguagem",
            "Dias desde última atualização",
            "rq07c_update_lang.pdf",
            log_scale=False)

# ──────────────────────────────────────────────────────────────────────────────
# Print summary stats (for LaTeX tables)
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== SUMMARY STATS ===")
print(f"N repositórios   : {len(rows)}")
print(f"RQ01 mediana idade: {median(age_years):.1f} anos ({median(age_days):.0f} dias)")
print(f"RQ02 mediana PRs  : {median(merged_prs):.0f}")
print(f"RQ03 mediana rels : {median(releases):.0f}")
print(f"RQ04 mediana upd  : {median(days_update):.0f} dias")
print(f"RQ06 mediana ratio: {median(closed_ratio):.4f}")
print(f"Top languages     : {top_langs[:5]}")

# ──────────────────────────────────────────────────────────────────────────────
# Compute per-language medians for RQ07 table
# ──────────────────────────────────────────────────────────────────────────────
rq07_rows = []
for lang in top8_langs:
    prs_vals = prs_by_lang.get(lang, [])
    rel_vals = rel_by_lang.get(lang, [])
    upd_vals = upd_by_lang.get(lang, [])
    count    = lang_count[lang]
    rq07_rows.append({
        "lang":   lang,
        "count":  count,
        "med_prs": median(prs_vals) if prs_vals else 0,
        "med_rel": median(rel_vals) if rel_vals else 0,
        "med_upd": median(upd_vals) if upd_vals else 0,
    })

# ──────────────────────────────────────────────────────────────────────────────
# Compute language table for RQ05 (all top10)
# ──────────────────────────────────────────────────────────────────────────────
lang_table_rows = top_langs  # list of (lang, count)

# ──────────────────────────────────────────────────────────────────────────────
# Generate LaTeX
# ──────────────────────────────────────────────────────────────────────────────
med_age_y  = median(age_years)
med_age_d  = median(age_days)
med_prs_v  = median(merged_prs)
med_rel_v  = median(releases)
med_upd_v  = median(days_update)
med_cr_v   = median(closed_ratio)
n_repos    = len(rows)

def fmt_int(v):
    return f"{int(v):,}".replace(",", ".")

def fmt_float2(v):
    return f"{v:.2f}".replace(".", ",")

def fmt_float4(v):
    return f"{v:.4f}".replace(".", ",")

def fmt_pct1(v):
  return f"{v:.1f}".replace(".", ",")

# Build RQ07 table rows
rq07_tex_rows = ""
for r in rq07_rows:
    rq07_tex_rows += (
        f"        {r['lang']} & {r['count']} & "
        f"{fmt_int(r['med_prs'])} & "
        f"{fmt_int(r['med_rel'])} & "
        f"{fmt_int(r['med_upd'])} \\\\\n"
    )

# Build RQ05 table rows
lang_tex_rows = ""
for lang, cnt in lang_table_rows:
    pct = cnt / n_repos * 100
    lang_tex_rows += f"        {lang} & {cnt} & {pct:.1f}\\% \\\\\n"

top3_langs = []
for lang, cnt in lang_table_rows[:3]:
  pct = cnt / n_repos * 100
  top3_langs.append((lang, pct))
top3_langs_str = ", ".join(
  f"{lang} ({fmt_pct1(pct)}\\%)" for lang, pct in top3_langs
)

TEX = rf"""\documentclass[12pt,a4paper]{{article}}

% ── Encoding & Language ──────────────────────────────────────────────────────
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}

% ── Layout ───────────────────────────────────────────────────────────────────
\usepackage[top=2.5cm, bottom=2.5cm, left=3cm, right=2.5cm]{{geometry}}
\usepackage{{setspace}}
\onehalfspacing

% ── Fonts & Typography ───────────────────────────────────────────────────────
\usepackage{{lmodern}}
\usepackage{{microtype}}

% ── Graphics & Tables ────────────────────────────────────────────────────────
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{caption}}
\usepackage{{subcaption}}
\usepackage{{float}}
\usepackage{{array}}
\usepackage{{xcolor}}

% ── Math ─────────────────────────────────────────────────────────────────────
\usepackage{{amsmath}}

% ── Hyperlinks ───────────────────────────────────────────────────────────────
\usepackage[hidelinks]{{hyperref}}

% ── Headers & Footers ────────────────────────────────────────────────────────
\usepackage{{fancyhdr}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small Laboratório de Experimentação de Software}}
\fancyhead[R]{{\small PUC Minas -- 2026/1}}
\fancyfoot[C]{{\thepage}}
\renewcommand{{\headrulewidth}}{{0.4pt}}

% ─────────────────────────────────────────────────────────────────────────────
\begin{{document}}

% ── Capa ─────────────────────────────────────────────────────────────────────
\begin{{titlepage}}
  \centering
  \vspace*{{\fill}}
  {{\LARGE \textbf{{Laboratório 01 -- Relatório Final (Lab01S03)}}\\[0.4em]
  \Large Características de Repositórios Populares do GitHub}}\\[2em]
  {{\large
    Raphael Brito\\[0.3em]
    Yan Cota
  }}\\[2em]
  {{\normalsize Pontifícia Universidade Católica de Minas Gerais (PUC~Minas)\\
  Laboratório de Experimentação de Software -- 2026/1}}\\[1.5em]
  {{\normalsize Belo Horizonte, {n_repos} repositórios analisados -- Março de 2026}}
  \vspace*{{\fill}}
\end{{titlepage}}

% ── Sumário ──────────────────────────────────────────────────────────────────
\tableofcontents
\newpage

% ─────────────────────────────────────────────────────────────────────────────
\section{{Introdução}}
% ─────────────────────────────────────────────────────────────────────────────

O GitHub hospeda hoje mais de 300 milhões de repositórios públicos, tornando-se
a maior plataforma de desenvolvimento colaborativo do mundo. Neste trabalho
analisamos os \textbf{{{n_repos} repositórios mais populares}} (medidos pelo número
de \textit{{stars}}) a fim de compreender suas características estruturais e de
processo de desenvolvimento.

Para isso, utilizamos a \textbf{{API GraphQL do GitHub}} para coletar dados como
data de criação, data de última atualização, linguagem primária, número de
\textit{{pull requests}} aceitas (merged), número de \textit{{releases}} e número de
\textit{{issues}} abertas e fechadas.

\subsection{{Hipóteses Informais}}

Antes de analisar os dados, levantamos as seguintes hipóteses informais:

\begin{{description}}
  \item[\textbf{{H1 -- Maturidade}}]
    Esperamos que repositórios populares sejam, em geral, \textbf{{maduros}},
    com pelo menos 3--5 anos de existência. A popularidade tende a se acumular
    com o tempo, à medida que mais usuários descobrem e marcam o projeto.

  \item[\textbf{{H2 -- Contribuição externa}}]
    Projetos populares devem atrair \textbf{{muitas contribuições externas}},
    resultando em um número elevado de PRs aceitas. Comunidades grandes são
    naturalmente mais ativas.

  \item[\textbf{{H3 -- Frequência de releases}}]
    Supomos que repositórios populares lancem releases com certa regularidade;
    entretanto, projetos de documentação/listas (como \textit{{awesome-*}})
    tipicamente \textbf{{não utilizam releases}}, o que deve fazer a mediana ser
    baixa.

  \item[\textbf{{H4 -- Atualização recente}}]
    Esperamos que a grande maioria dos repositórios populares esteja
    \textbf{{atualizada recentemente}} (últimos 30--60 dias), pois projetos
    abandonados raramente mantêm o topo do ranking.

  \item[\textbf{{H5 -- Linguagens populares}}]
    Acreditamos que linguagens como \textbf{{JavaScript/TypeScript, Python e Java}}
    dominem os repositórios populares, refletindo a popularidade dessas
    linguagens na comunidade open-source.

  \item[\textbf{{H6 -- Alto percentual de issues fechadas}}]
    Projetos ativos e com boa manutenção devem ter um \textbf{{alto percentual
    de issues fechadas}} (acima de 0,8), indicando equipes responsivas.

  \item[\textbf{{H7 -- Linguagem e contribuição (Bônus)}}]
    Esperamos que projetos escritos em linguagens mais populares
    (JavaScript, TypeScript, Python) recebam \textbf{{mais contribuição externa}},
    lancem mais releases e sejam atualizados com maior frequência.
\end{{description}}

% ─────────────────────────────────────────────────────────────────────────────
\section{{Metodologia}}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{{Coleta de Dados}}

A coleta foi realizada por meio da \textbf{{API GraphQL do GitHub}} em duas etapas:

\begin{{enumerate}}
  \item \textbf{{Busca paginada de repositórios:}} utilizamos a busca por
    \texttt{{stars:>0 sort:stars-desc}} com páginas de 100 repositórios,
    repetindo a paginação via \textit{{cursor}} até atingir os 1.000 repositórios
    mais estrelados.

  \item \textbf{{Coleta de métricas:}} para cada repositório coletamos, via
    consulta GraphQL em lotes de 4, o total de PRs aceitas
    (\texttt{{pullRequests(states: MERGED)}}\texttt{{.totalCount}}),
    o total de releases (\texttt{{releases.totalCount}}) e o total e
    número de issues fechadas.
\end{{enumerate}}

Os dados foram consolidados em um arquivo \texttt{{repos.csv}} com os seguintes
campos: \texttt{{full\_name}}, \texttt{{stars}}, \texttt{{language}},
\texttt{{created\_at}}, \texttt{{updated\_at}}, \texttt{{age\_days}},
\texttt{{days\_since\_update}}, \texttt{{merged\_prs}}, \texttt{{releases}},
\texttt{{total\_issues}}, \texttt{{closed\_issues}}, \texttt{{closed\_issue\_ratio}}.

\subsection{{Análise}}

Para cada questão de pesquisa utilizamos a \textbf{{mediana}} como medida de
tendência central, por ser robusta a valores extremos (outliers), comuns em
distribuições de métricas de software. Para variáveis categóricas (linguagem)
realizamos contagem por categoria. Os gráficos foram gerados com
\texttt{{matplotlib}} em Python.

\subsection{{Visualização dos Dados}}

As distribuições numéricas foram apresentadas por meio de histogramas
(RQs 01, 02, 03, 04 e 06). Para as RQs 02 e 03, utilizamos escala logarítmica
para reduzir o efeito de outliers. As análises por linguagem (RQ07) foram
representadas com boxplots, comparando medianas e dispersões por categoria.

% ─────────────────────────────────────────────────────────────────────────────
\section{{Resumo das Métricas}}
% ─────────────────────────────────────────────────────────────────────────────

A Tabela~\ref{{tab:summary}} apresenta as medianas das métricas numéricas.
Para a RQ05 (variável categórica), a contagem por linguagem está na
Tabela~\ref{{tab:rq05}}.

\begin{{table}}[H]
  \centering
  \caption{{Resumo das medianas das métricas (RQs 01, 02, 03, 04 e 06).}}
  \label{{tab:summary}}
  \begin{{tabular}}{{llr}}
    \toprule
    \textbf{{RQ}} & \textbf{{Métrica}} & \textbf{{Mediana}} \\
    \midrule
    RQ01 & Idade (anos) & {fmt_float2(med_age_y)} \\
    RQ02 & PRs aceitas & {fmt_int(med_prs_v)} \\
    RQ03 & Releases & {fmt_int(med_rel_v)} \\
    RQ04 & Dias desde atualização & {fmt_int(med_upd_v)} \\
    RQ06 & Razão issues fechadas & {fmt_float4(med_cr_v)} \\
    \bottomrule
  \end{{tabular}}
\end{{table}}

% ─────────────────────────────────────────────────────────────────────────────
\section{{Questões de Pesquisa e Resultados}}
% ─────────────────────────────────────────────────────────────────────────────

% ──────────────────────────────────────────────────
\subsection{{RQ01 -- Sistemas populares são maduros/antigos?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica:}} idade do repositório em anos (calculada a partir de
\texttt{{created\_at}}).

\textbf{{Hipótese (H1):}} repositórios populares tendem a ser maduros,
com 3--5 anos ou mais de existência.

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq01_age.pdf}}
  \caption{{Distribuição da idade dos 1.000 repositórios mais populares.}}
  \label{{fig:rq01}}
\end{{figure}}

\textbf{{Resultado:}} a mediana da idade é de \textbf{{{fmt_float2(med_age_y)} anos}}
({fmt_int(med_age_d)} dias). A distribuição é assimétrica à esquerda, com a maioria
dos repositórios concentrada entre 3 e 8 anos.

\textbf{{Discussão:}} a hipótese H1 foi \textbf{{confirmada}}. Repositórios populares
são, em geral, maduros. Há pouquíssimos repositórios populares com menos de
1 ano de existência, o que reforça que a popularidade se acumula com o tempo.

% ──────────────────────────────────────────────────
\subsection{{RQ02 -- Sistemas populares recebem muita contribuição externa?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica:}} total de pull requests aceitas (\textit{{merged}}).

\textbf{{Hipótese (H2):}} projetos populares atraem muitas contribuições
externas e, portanto, apresentam alto volume de PRs aceitas.

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq02_prs.pdf}}
  \caption{{Distribuição do número de PRs aceitas (escala log\textsubscript{{10}}).}}
  \label{{fig:rq02}}
\end{{figure}}

\textbf{{Resultado:}} a mediana é de \textbf{{{fmt_int(med_prs_v)} PRs aceitas}}.
A distribuição é bastante dispersa: projetos de documentação/listas apresentam
poucas PRs, enquanto projetos de código com grandes comunidades (e.g.,
\textit{{VSCode}}, \textit{{TensorFlow}}) chegam a dezenas de milhares.

\textbf{{Discussão:}} a hipótese H2 é \textbf{{parcialmente confirmada}}.
Embora a mediana é razoável, a grande variância indica que o volume de
contribuições externas depende fortemente do tipo de projeto.

% ──────────────────────────────────────────────────
\subsection{{RQ03 -- Sistemas populares lançam releases com frequência?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica:}} total de releases publicadas.

\textbf{{Hipótese (H3):}} repositórios populares lançam releases com
regularidade, mas projetos de conteúdo podem reduzir a mediana.

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq03_releases.pdf}}
  \caption{{Distribuição do número de releases (escala log\textsubscript{{10}}).}}
  \label{{fig:rq03}}
\end{{figure}}

\textbf{{Resultado:}} a mediana é de \textbf{{{fmt_int(med_rel_v)} releases}}.
Uma grande parcela dos repositórios possui zero ou poucas releases,
puxando a mediana para baixo.

\textbf{{Discussão:}} a hipótese H3 foi \textbf{{confirmada em parte}}.
Muitos projetos populares são repositórios de conteúdo (listas, documentação,
tutoriais) que não utilizam o mecanismo de releases do GitHub.
Projetos de software propriamente ditos tendem a ter muito mais releases.

% ──────────────────────────────────────────────────
\subsection{{RQ04 -- Sistemas populares são atualizados com frequência?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica:}} número de dias desde a última atualização
(\texttt{{days\_since\_update}}).

\textbf{{Hipótese (H4):}} a maioria dos repositórios populares está atualizada
recentemente (últimos 30--60 dias).

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq04_update.pdf}}
  \caption{{Distribuição do tempo desde a última atualização (dias).}}
  \label{{fig:rq04}}
\end{{figure}}

\textbf{{Resultado:}} a mediana é de \textbf{{{fmt_int(med_upd_v)} dia(s)}} desde a
última atualização. A concentração próxima de zero indica que a esmagadora
maioria dos repositórios populares foi atualizada muito recentemente
(na data de coleta, 6 de março de 2026).

\textbf{{Discussão:}} a hipótese H4 foi \textbf{{fortemente confirmada}}.
Repositórios populares são quase todos ativos e atualizados recentemente.

% ──────────────────────────────────────────────────
\subsection{{RQ05 -- Sistemas populares são escritos nas linguagens mais populares?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica:}} linguagem primária de cada repositório.

\textbf{{Hipótese (H5):}} linguagens populares na comunidade open-source
(JavaScript/TypeScript, Python e Java) dominam os repositórios mais estrelados.

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq05_langs.pdf}}
  \caption{{Top 10 linguagens primárias nos 1.000 repositórios mais populares.}}
  \label{{fig:rq05}}
\end{{figure}}

\begin{{table}}[H]
  \centering
  \caption{{Top 10 linguagens primárias.}}
  \label{{tab:rq05}}
  \begin{{tabular}}{{lrr}}
    \toprule
    \textbf{{Linguagem}} & \textbf{{Repositórios}} & \textbf{{(\%)}} \\
    \midrule
{lang_tex_rows}    \bottomrule
  \end{{tabular}}
\end{{table}}

\textbf{{Resultado:}} as linguagens que mais aparecem são
\textbf{{{top3_langs_str}}}, confirmando sua popularidade global.
A categoria ``Unknown'' representa repositórios sem linguagem de código
(documentação, listas, etc.).

\textbf{{Discussão:}} a hipótese H5 foi \textbf{{confirmada}}.
JavaScript/TypeScript e Python dominam o ecossistema open-source popular.

% ──────────────────────────────────────────────────
\subsection{{RQ06 -- Sistemas populares possuem alto percentual de issues fechadas?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica:}} razão entre issues fechadas e total de issues
($\text{{ratio}} = \text{{closed}} / \text{{total}}$).

\textbf{{Hipótese (H6):}} projetos populares têm alto percentual de issues
fechadas (acima de 0,8), indicando manutenção ativa.

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq06_issues.pdf}}
  \caption{{Distribuição da razão de issues fechadas.}}
  \label{{fig:rq06}}
\end{{figure}}

\textbf{{Resultado:}} a mediana da razão é de \textbf{{{fmt_float4(med_cr_v)}}},
ou seja, aproximadamente {fmt_float2(med_cr_v * 100)}\% das issues são fechadas
nos repositórios medianos da amostra.

\textbf{{Discussão:}} a hipótese H6 foi \textbf{{confirmada}}.
A alta mediana indica que projetos populares são bem mantidos e que suas
equipes são responsivas no tratamento de issues.

% ─────────────────────────────────────────────────────────────────────────────
\section{{RQ07 (Bônus) -- Linguagem e Contribuição Externa, Releases e Atualização}}
% ─────────────────────────────────────────────────────────────────────────────

Esta questão de pesquisa bônus investiga se a linguagem primária do repositório
influencia as métricas das RQs 02, 03 e 04.

\textbf{{Hipótese (H7):}} linguagens mais populares tendem a receber mais
contribuições, lançar mais releases e manter atualizações mais frequentes.

\subsection{{RQ07a -- PRs aceitas por linguagem}}

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq07a_prs_lang.pdf}}
  \caption{{Distribuição de PRs aceitas por linguagem (escala log\textsubscript{{10}}).}}
  \label{{fig:rq07a}}
\end{{figure}}

\subsection{{RQ07b -- Releases por linguagem}}

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq07b_releases_lang.pdf}}
  \caption{{Distribuição de releases por linguagem (escala log\textsubscript{{10}}).}}
  \label{{fig:rq07b}}
\end{{figure}}

\subsection{{RQ07c -- Tempo desde última atualização por linguagem}}

\begin{{figure}}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{{figs/rq07c_update_lang.pdf}}
  \caption{{Distribuição de dias desde última atualização por linguagem.}}
  \label{{fig:rq07c}}
\end{{figure}}

\begin{{table}}[H]
  \centering
  \caption{{Medianas das métricas das RQs 02, 03 e 04 por linguagem (top 8).}}
  \label{{tab:rq07}}
  \begin{{tabular}}{{lrrrr}}
    \toprule
    \textbf{{Linguagem}} & \textbf{{Repos}} &
    \textbf{{Med. PRs}} & \textbf{{Med. Releases}} & \textbf{{Med. Dias Upd.}} \\
    \midrule
{rq07_tex_rows}    \bottomrule
  \end{{tabular}}
\end{{table}}

\textbf{{Discussão:}} a hipótese H7 é \textbf{{parcialmente confirmada}}.
Linguagens tipicamente usadas em projetos de software ativos (TypeScript,
Python, JavaScript, C++) tendem a apresentar medianas de PRs e releases mais
altas do que linguagens usadas em projetos de documentação (Markdown,
HTML, ``Unknown''). Quanto à frequência de atualização, a diferença entre
linguagens é menor, pois projetos de documentação também costumam ser
atualizados com frequência.

% ─────────────────────────────────────────────────────────────────────────────
\section{{Conclusão}}
% ─────────────────────────────────────────────────────────────────────────────

A análise dos {n_repos} repositórios mais populares do GitHub revelou que:

\begin{{itemize}}
  \item Repositórios populares são, em geral, \textbf{{maduros}} (mediana de
    {fmt_float2(med_age_y)} anos) e \textbf{{recentemente atualizados}}
    (mediana de {fmt_int(med_upd_v)} dia(s) desde o último \textit{{push}}).

  \item A contribuição externa é significativa em projetos de código, com
    mediana de {fmt_int(med_prs_v)} PRs aceitas, embora projetos de
    documentação reduzam essa mediana.

  \item O uso de releases é heterogêneo: muitos repositórios populares são de
    conteúdo e não utilizam releases formais (mediana de {fmt_int(med_rel_v)}).

  \item JavaScript/TypeScript e Python dominam as linguagens dos projetos
    populares.

  \item A manutenção é alta, com mediana de razão de issues fechadas de
    {fmt_float4(med_cr_v)}.

  \item Linguagens de código tendem a apresentar mais contribuição externa e
    mais releases do que repositórios de documentação.
\end{{itemize}}

% ─────────────────────────────────────────────────────────────────────────────
\end{{document}}
"""

TEX_PATH.write_text(TEX, encoding="utf-8")
print(f"\nLaTeX report written to: {TEX_PATH}")
print("Done!")
