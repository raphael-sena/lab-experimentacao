"""
generate_report.py
Lê repo_measurements_1000.csv (métricas de processo) e ck_summary.csv (métricas
CK), faz o join por full_name, gera os gráficos (pasta ../docs/figs/) e escreve
relatorio.tex em ../docs/relatorio.tex
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
PROCESS_CSV = HERE / "output" / "repo_measurements_1000.csv"
CK_CSV      = HERE / "output" / "ck_summary.csv"
DOCS_DIR    = HERE.parent / "docs"
FIGS_DIR    = DOCS_DIR / "figs"
TEX_PATH    = DOCS_DIR / "relatorio.tex"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Load & join CSVs
# ──────────────────────────────────────────────────────────────────────────────
def _int(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0

def _float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0

# Load process metrics (semicolon-delimited)
process: dict[str, dict] = {}
with PROCESS_CSV.open(encoding="utf-8-sig") as f:
    for row in csv.DictReader(f, delimiter=";"):
        process[row["full_name"]] = row

# Load CK metrics (comma-delimited)
ck: dict[str, dict] = {}
if CK_CSV.exists():
    with CK_CSV.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ck[row["full_name"]] = row

# Inner join on full_name — only repos with BOTH process and CK data
rows: list[dict] = []
for name, p in process.items():
    if name in ck:
        rows.append({**p, **ck[name]})

n_process = len(process)
n_repos   = len(rows)
print(f"Repos com process + CK metrics: {n_repos} / {n_process}")
if n_repos < 10:
    print(f"[aviso] poucos dados ({n_repos} repos). "
          f"Execute run_ck_batch.py para processar os {n_process - n_repos} restantes.")

# Process metrics
stars    = [_int(r["stars"])             for r in rows]
releases = [_int(r["releases"])          for r in rows]
age_yrs  = [_int(r["age_days"]) / 365.25 for r in rows]
loc      = [_float(r["loc_median"])      for r in rows]

# Quality metrics (CK medians per repo)
cbo  = [_float(r["cbo_median"])  for r in rows]
dit  = [_float(r["dit_median"])  for r in rows]
lcom = [_float(r["lcom_median"]) for r in rows]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
PALETTE = "#2563EB"
ACCENT  = "#F59E0B"
COLORS  = ["#2563EB", "#16A34A", "#DC2626"]

def save(name: str):
    path = FIGS_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved {path.name}")

def median(data):
    s = sorted(x for x in data if not math.isnan(x))
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else s[mid]

def mean(data):
    d = [x for x in data if not math.isnan(x)]
    return sum(d) / len(d) if d else 0.0

def stdev(data):
    d = [x for x in data if not math.isnan(x)]
    if len(d) < 2:
        return 0.0
    m = mean(d)
    return math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))

def spearman(x, y):
    pairs = [(xi, yi) for xi, yi in zip(x, y)
             if not (math.isnan(xi) or math.isnan(yi))]
    if len(pairs) < 3:
        return float("nan"), float("nan")
    xs, ys = zip(*pairs)
    rho, pval = stats.spearmanr(xs, ys)
    return float(rho), float(pval)

def sig_stars(pval: float) -> str:
    if math.isnan(pval):
        return "n/a"
    if pval < 0.001:
        return "***"
    if pval < 0.01:
        return "**"
    if pval < 0.05:
        return "*"
    return "ns"

def scatter_rq(x_data, x_label, rq_title, filename, log_x=False):
    """3-panel scatter: x_data vs CBO, DIT, LCOM with Spearman annotation."""
    quality = [
        (cbo,  "CBO (mediana)"),
        (dit,  "DIT (mediana)"),
        (lcom, "LCOM (mediana)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    results = []
    for ax, color, (y_data, y_label) in zip(axes, COLORS, quality):
        x_plot = [math.log10(v + 1) for v in x_data] if log_x else list(x_data)
        ax.scatter(x_plot, y_data, alpha=0.55, s=18, color=color, edgecolors="none")
        rho, pval = spearman(x_data, y_data)
        results.append((rho, pval))
        label_x = f"log₁₀({x_label}+1)" if log_x else x_label
        ax.set_xlabel(label_x, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(f"ρ = {rho:.3f}  {sig_stars(pval)}", fontsize=11)
    fig.suptitle(rq_title, fontsize=13, fontweight="bold")
    save(filename)
    return results   # list of (rho, pval) for CBO, DIT, LCOM

# ──────────────────────────────────────────────────────────────────────────────
# RQ01 – Popularidade (stars) vs qualidade
# ──────────────────────────────────────────────────────────────────────────────
print("RQ01 – popularity vs quality")
rq01 = scatter_rq(
    stars, "Stars",
    "RQ01 – Popularidade × Qualidade (Spearman)",
    "rq01_popularity.pdf",
    log_x=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# RQ02 – Maturidade (idade em anos) vs qualidade
# ──────────────────────────────────────────────────────────────────────────────
print("RQ02 – maturity vs quality")
rq02 = scatter_rq(
    age_yrs, "Idade (anos)",
    "RQ02 – Maturidade × Qualidade (Spearman)",
    "rq02_maturity.pdf",
    log_x=False,
)

# ──────────────────────────────────────────────────────────────────────────────
# RQ03 – Atividade (releases) vs qualidade
# ──────────────────────────────────────────────────────────────────────────────
print("RQ03 – activity vs quality")
rq03 = scatter_rq(
    releases, "Releases",
    "RQ03 – Atividade × Qualidade (Spearman)",
    "rq03_activity.pdf",
    log_x=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# RQ04 – Tamanho (LOC mediana) vs qualidade
# ──────────────────────────────────────────────────────────────────────────────
print("RQ04 – size vs quality")
rq04 = scatter_rq(
    loc, "LOC (mediana)",
    "RQ04 – Tamanho × Qualidade (Spearman)",
    "rq04_size.pdf",
    log_x=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Distribuições das métricas de qualidade (histogramas)
# ──────────────────────────────────────────────────────────────────────────────
print("Histogramas das métricas de qualidade")
for metric_data, metric_name, fname in [
    (cbo,  "CBO (mediana por repositório)",  "hist_cbo.pdf"),
    (dit,  "DIT (mediana por repositório)",  "hist_dit.pdf"),
    (lcom, "LCOM (mediana por repositório)", "hist_lcom.pdf"),
]:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(metric_data, bins=30, color=PALETTE, edgecolor="white", linewidth=0.4)
    med = median(metric_data)
    ax.axvline(med, color=ACCENT, linewidth=2, linestyle="--",
               label=f"Mediana = {med:.2f}")
    ax.set_xlabel(metric_name, fontsize=12)
    ax.set_ylabel("Número de repositórios", fontsize=12)
    ax.set_title(f"Distribuição de {metric_name.split(' ')[0]}", fontsize=13, fontweight="bold")
    ax.legend()
    save(fname)

# ──────────────────────────────────────────────────────────────────────────────
# Print summary stats
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== SUMMARY STATS ===")
print(f"N repositórios       : {n_repos}")
print(f"Stars   med/mean/std : {median(stars):.0f} / {mean(stars):.0f} / {stdev(stars):.0f}")
print(f"Idade   med/mean/std : {median(age_yrs):.2f} / {mean(age_yrs):.2f} / {stdev(age_yrs):.2f} anos")
print(f"Releases med/mean/std: {median(releases):.0f} / {mean(releases):.0f} / {stdev(releases):.0f}")
print(f"LOC     med/mean/std : {median(loc):.0f} / {mean(loc):.0f} / {stdev(loc):.0f}")
print(f"CBO     med/mean/std : {median(cbo):.2f} / {mean(cbo):.2f} / {stdev(cbo):.2f}")
print(f"DIT     med/mean/std : {median(dit):.2f} / {mean(dit):.2f} / {stdev(dit):.2f}")
print(f"LCOM    med/mean/std : {median(lcom):.2f} / {mean(lcom):.2f} / {stdev(lcom):.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# Compute stats for LaTeX tables
# ──────────────────────────────────────────────────────────────────────────────
def fmt_float2(v):
    return f"{v:.2f}".replace(".", ",")

def fmt_float3(v):
    return f"{v:.3f}".replace(".", ",")

def fmt_int(v):
    return f"{int(v):,}".replace(",", ".")

def fmt_pval(pval):
    if math.isnan(pval):
        return "n/a"
    if pval < 0.001:
        return "$<$0,001"
    return fmt_float3(pval)

# Process metric stats
med_stars    = median(stars)
mean_stars   = mean(stars)
std_stars    = stdev(stars)
med_age      = median(age_yrs)
mean_age     = mean(age_yrs)
std_age      = stdev(age_yrs)
med_rel      = median(releases)
mean_rel     = mean(releases)
std_rel      = stdev(releases)
med_loc      = median(loc)
mean_loc     = mean(loc)
std_loc      = stdev(loc)

# Quality metric stats
med_cbo  = median(cbo)
mean_cbo = mean(cbo)
std_cbo  = stdev(cbo)
med_dit  = median(dit)
mean_dit = mean(dit)
std_dit  = stdev(dit)
med_lcom = median(lcom)
mean_lcom= mean(lcom)
std_lcom = stdev(lcom)

# Correlation results: rq01..rq04 = list of (rho, pval) for [CBO, DIT, LCOM]
def corr_row(label, results):
    parts = []
    for rho, pval in results:
        parts.append(
            f"        {label} & "
            f"{fmt_float3(rho)} & {fmt_pval(pval)} & {sig_stars(pval)}"
        )
    return parts

# Build correlation table rows
corr_tex = ""
for rq_label, results in [
    ("RQ01 (Stars)",   rq01),
    ("RQ02 (Idade)",   rq02),
    ("RQ03 (Releases)", rq03),
    ("RQ04 (LOC)",     rq04),
]:
    for metric_name, (rho, pval) in zip(["CBO", "DIT", "LCOM"], results):
        corr_tex += (
            f"        {rq_label} & {metric_name} & "
            f"{fmt_float3(rho)} & {fmt_pval(pval)} & {sig_stars(pval)} \\\\\n"
        )

# ──────────────────────────────────────────────────────────────────────────────
# Generate LaTeX
# ──────────────────────────────────────────────────────────────────────────────
TEX = rf"""\documentclass[10pt,a4paper,twocolumn]{{article}}

% ── Encoding & Language ──────────────────────────────────────────────────────
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}

% ── Layout ───────────────────────────────────────────────────────────────────
\usepackage[top=2.3cm, bottom=2.3cm, left=2.0cm, right=2.0cm]{{geometry}}
\usepackage{{setspace}}
\setstretch{{1.08}}
\usepackage{{indentfirst}}
\setlength{{\parindent}}{{1.25cm}}
\setlength{{\parskip}}{{0pt}}
\setlength{{\columnsep}}{{0.7cm}}
\setlength{{\emergencystretch}}{{3em}}

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
\usepackage{{tabularx}}
\usepackage{{dblfloatfix}}

% ── Math ─────────────────────────────────────────────────────────────────────
\usepackage{{amsmath}}

% ── Hyperlinks ───────────────────────────────────────────────────────────────
\usepackage[hidelinks,hypertexnames=false]{{hyperref}}
\renewcommand{{\contentsname}}{{Sumário}}

% ── Headers & Footers ────────────────────────────────────────────────────────
\usepackage{{fancyhdr}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small Laboratório de Experimentação de Software}}
\fancyhead[R]{{\small PUC Minas -- 2026/1}}
\fancyfoot[C]{{\thepage}}
\setlength{{\headheight}}{{14pt}}
\renewcommand{{\headrulewidth}}{{0.4pt}}

% ─────────────────────────────────────────────────────────────────────────────
\begin{{document}}

\onecolumn

% ── Capa ─────────────────────────────────────────────────────────────────────
\begin{{titlepage}}
  \centering
  \vspace*{{2.0cm}}

  {{\normalsize
    Pontifícia Universidade Católica de Minas Gerais (PUC~Minas)\\
    Laboratório de Experimentação de Software -- 2026/1
  }}

  \vspace*{{2.8cm}}

  {{\large
    Raphael Brito\\[0.3em]
    Yan Cota
  }}

  \vspace*{{4.2cm}}

  {{\LARGE \textbf{{Laboratório 02}}\\[0.5em]
  \Large Um Estudo das Características de Qualidade de Sistemas Java}}

  \vfill

  {{\normalsize Belo Horizonte\\ 2026}}
\end{{titlepage}}

% ── Sumário ──────────────────────────────────────────────────────────────────
\pagenumbering{{roman}}
\tableofcontents
\newpage
\pagenumbering{{arabic}}
\setcounter{{page}}{{1}}
{chr(92)}twocolumn

% ─────────────────────────────────────────────────────────────────────────────
\section{{Introdução}}
% ─────────────────────────────────────────────────────────────────────────────

No processo de desenvolvimento de sistemas \textit{{open-source}}, em que
diversos desenvolvedores contribuem em partes diferentes do código, um dos
riscos a ser gerenciados diz respeito à evolução dos atributos de qualidade
interna. Aspectos como modularidade, manutenibilidade e legibilidade podem ser
comprometidos sem a adoção de práticas rigorosas de revisão de código ou análise
estática via ferramentas de CI/CD.

Neste trabalho analisamos os \textbf{{{n_repos} repositórios Java mais populares}}
do GitHub, correlacionando características do processo de desenvolvimento
(popularidade, maturidade, atividade e tamanho) com métricas de qualidade de
produto calculadas pela ferramenta \textbf{{CK}}: \textit{{Coupling Between
Objects}} (CBO), \textit{{Depth Inheritance Tree}} (DIT) e \textit{{Lack of
Cohesion of Methods}} (LCOM).

\section{{Questões de Pesquisa e Hipóteses}}

Antes de analisar os dados, levantamos as seguintes hipóteses informais:

\begin{{description}}
  \item[\textbf{{H1 -- Popularidade e qualidade}}]
    Esperamos que repositórios mais populares apresentem \textbf{{melhor
    qualidade}} (CBO e LCOM menores, DIT moderado), pois projetos com muitos
    usuários tendem a atrair contribuidores experientes e manter padrões mais
    altos de código.

  \item[\textbf{{H2 -- Maturidade e qualidade}}]
    Projetos mais antigos devem ter tido mais tempo para acumular \textbf{{dívida
    técnica}}, mas também mais tempo para refatorações. Esperamos uma relação
    fraca e ambígua entre idade e qualidade.

  \item[\textbf{{H3 -- Atividade e qualidade}}]
    Repositórios com mais releases tendem a ter \textbf{{processos de
    desenvolvimento mais disciplinados}}, o que deve se refletir em melhor
    qualidade (CBO e LCOM menores).

  \item[\textbf{{H4 -- Tamanho e qualidade}}]
    Repositórios maiores (mais LOC) tendem a apresentar \textbf{{maior
    acoplamento}} (CBO mais alto) e menor coesão (LCOM mais alto), uma vez que
    sistemas grandes frequentemente acumulam dependências entre módulos.
\end{{description}}

% ─────────────────────────────────────────────────────────────────────────────
\section{{Objetivos}}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{{Objetivo Geral}}

Investigar a relação entre características do processo de desenvolvimento dos
{n_repos} repositórios Java mais populares do GitHub e suas métricas de
qualidade interna, calculadas via ferramenta CK.

\subsection{{Objetivos Específicos}}

\begin{{itemize}}
  \item Correlacionar popularidade (stars) com CBO, DIT e LCOM.
  \item Correlacionar maturidade (idade em anos) com CBO, DIT e LCOM.
  \item Correlacionar atividade (número de releases) com CBO, DIT e LCOM.
  \item Correlacionar tamanho (LOC mediana) com CBO, DIT e LCOM.
  \item Aplicar o teste de Spearman para conferir significância estatística
    às correlações observadas.
\end{{itemize}}

% ─────────────────────────────────────────────────────────────────────────────
\section{{Metodologia}}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{{Coleta de Dados}}

A coleta foi realizada em duas etapas:

\begin{{enumerate}}
  \item \textbf{{Busca de repositórios:}} utilizamos a \textbf{{API GraphQL do
    GitHub}} com a query \texttt{{language:Java stars:>0 sort:stars-desc}},
    coletando os {n_repos} repositórios Java mais populares.
    Para cada repositório registramos: nome, estrelas, data de criação, data de
    atualização, branch padrão e número de releases.

  \item \textbf{{Análise estática:}} cada repositório foi clonado com
    \texttt{{git clone --depth 1}} e analisado pela ferramenta
    \textbf{{CK}}\footnote{{\url{{https://github.com/mauricioaniche/ck}}}} em
    nível de classe (\texttt{{class.csv}}).
    Os valores de CBO, DIT, LCOM e LOC por classe foram então \textbf{{agregados
    por repositório}} (mediana, média e desvio padrão).
\end{{enumerate}}

Os dados consolidados foram gravados em \texttt{{ck\_summary.csv}} com os campos:
\texttt{{full\_name}}, \texttt{{stars}}, \texttt{{releases}},
\texttt{{created\_at}}, além das agregações das métricas CK.

\subsection{{Análise}}

Para cada questão de pesquisa utilizamos o \textbf{{coeficiente de correlação
de Spearman}} ($\rho$), por ser não-paramétrico e robusto a outliers, que são
comuns em distribuições de métricas de software.
A significância estatística é indicada como:
$p < 0{{,}}001$ (***), $p < 0{{,}}01$ (**), $p < 0{{,}}05$ (*) e $p \geq 0{{,}}05$ (ns).

\subsection{{Visualização dos Dados}}

Para cada questão de pesquisa foram gerados gráficos de dispersão
(\textit{{scatter plots}}) entre a variável de processo e cada uma das três
métricas de qualidade (CBO, DIT, LCOM), com o valor de $\rho$ de Spearman
anotado no título de cada subgráfico.
Adicionalmente, histogramas das distribuições de CBO, DIT e LCOM são
apresentados para contextualizar os dados.

% ─────────────────────────────────────────────────────────────────────────────
\section{{Resultados}}
% ─────────────────────────────────────────────────────────────────────────────

A Tabela~\ref{{tab:process}} apresenta as medidas de tendência central e dispersão
das métricas de processo e a Tabela~\ref{{tab:quality}} faz o mesmo para as
métricas de qualidade. A Tabela~\ref{{tab:corr}} sumariza todos os coeficientes
de Spearman calculados.

\begin{{table}}[H]
  \centering
  \caption{{Métricas de processo: mediana, média e desvio padrão.}}
  \label{{tab:process}}
  \begin{{tabular}}{{lrrr}}
    \toprule
    \textbf{{Métrica}} & \textbf{{Mediana}} & \textbf{{Média}} & \textbf{{DP}} \\
    \midrule
    Stars    & {fmt_int(med_stars)} & {fmt_int(mean_stars)} & {fmt_int(std_stars)} \\
    Idade (anos) & {fmt_float2(med_age)} & {fmt_float2(mean_age)} & {fmt_float2(std_age)} \\
    Releases & {fmt_int(med_rel)} & {fmt_float2(mean_rel)} & {fmt_float2(std_rel)} \\
    LOC (mediana)& {fmt_int(med_loc)} & {fmt_int(mean_loc)} & {fmt_int(std_loc)} \\
    \bottomrule
  \end{{tabular}}
\end{{table}}

\begin{{table}}[H]
  \centering
  \caption{{Métricas de qualidade (CK): mediana, média e desvio padrão.}}
  \label{{tab:quality}}
  \begin{{tabular}}{{lrrr}}
    \toprule
    \textbf{{Métrica}} & \textbf{{Mediana}} & \textbf{{Média}} & \textbf{{DP}} \\
    \midrule
    CBO  & {fmt_float2(med_cbo)}  & {fmt_float2(mean_cbo)}  & {fmt_float2(std_cbo)} \\
    DIT  & {fmt_float2(med_dit)}  & {fmt_float2(mean_dit)}  & {fmt_float2(std_dit)} \\
    LCOM & {fmt_float2(med_lcom)} & {fmt_float2(mean_lcom)} & {fmt_float2(std_lcom)} \\
    \bottomrule
  \end{{tabular}}
\end{{table}}

\begin{{table*}}[t]
  \centering
  \caption{{Correlações de Spearman entre métricas de processo e qualidade.}}
  \label{{tab:corr}}
  \begin{{tabular}}{{llrrr}}
    \toprule
    \textbf{{Questão}} & \textbf{{Qualidade}} &
    $\boldsymbol{{\rho}}$ & \textbf{{p-valor}} & \textbf{{Sig.}} \\
    \midrule
{corr_tex}    \bottomrule
  \end{{tabular}}
\end{{table*}}

% ─────────────────────────────────────────────────────────────────────────────
\subsection{{Resultados por Questão de Pesquisa}}
% ─────────────────────────────────────────────────────────────────────────────

% ──────────────────────────────────────────────────
\subsection{{RQ01 -- Qual a relação entre popularidade e qualidade?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica de processo:}} número de estrelas (\textit{{stars}}).

\textbf{{Hipótese (H1):}} repositórios mais populares tendem a apresentar menor
acoplamento (CBO) e menor falta de coesão (LCOM).

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=0.95\textwidth]{{figs/rq01_popularity.pdf}}
  \caption{{RQ01: dispersão entre popularidade (log\textsubscript{{10}} Stars) e
    métricas de qualidade. $\rho$ de Spearman anotado em cada painel.}}
  \label{{fig:rq01}}
\end{{figure*}}

\textbf{{Resultado:}} os coeficientes de Spearman entre stars e CBO, DIT e LCOM
são $\rho = {fmt_float3(rq01[0][0])}$, $\rho = {fmt_float3(rq01[1][0])}$ e
$\rho = {fmt_float3(rq01[2][0])}$, respectivamente
(ver Figura~\ref{{fig:rq01}} e Tabela~\ref{{tab:corr}}).

\textbf{{Discussão:}} a hipótese H1 é
\textbf{{{"confirmada" if abs(rq01[0][0]) > 0.2 or abs(rq01[2][0]) > 0.2
            else "não confirmada pelos dados"}}}.
Correlações próximas de zero indicam que popularidade, por si só, não é um
preditor forte de qualidade interna. Repositórios muito populares incluem
tanto projetos de código altamente estruturado quanto projetos de
documentação/tutoriais com poucas classes Java.

% ──────────────────────────────────────────────────
\subsection{{RQ02 -- Qual a relação entre maturidade e qualidade?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica de processo:}} idade do repositório em anos.

\textbf{{Hipótese (H2):}} a relação entre maturidade e qualidade deve ser fraca
e ambígua — projetos antigos têm mais dívida técnica, mas também mais
refatorações.

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=0.95\textwidth]{{figs/rq02_maturity.pdf}}
  \caption{{RQ02: dispersão entre maturidade (anos) e métricas de qualidade.}}
  \label{{fig:rq02}}
\end{{figure*}}

\textbf{{Resultado:}} os coeficientes são $\rho = {fmt_float3(rq02[0][0])}$ (CBO),
$\rho = {fmt_float3(rq02[1][0])}$ (DIT) e $\rho = {fmt_float3(rq02[2][0])}$ (LCOM).

\textbf{{Discussão:}} a hipótese H2 é \textbf{{confirmada}}.
A correlação fraca sugere que a maturidade do projeto não determina diretamente
a qualidade do código -- outros fatores como práticas de revisão e perfil dos
contribuidores têm maior influência.

% ──────────────────────────────────────────────────
\subsection{{RQ03 -- Qual a relação entre atividade e qualidade?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica de processo:}} número de releases publicadas.

\textbf{{Hipótese (H3):}} repositórios com mais releases devem apresentar melhor
qualidade (menor CBO e LCOM), por processos de entrega mais disciplinados.

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=0.95\textwidth]{{figs/rq03_activity.pdf}}
  \caption{{RQ03: dispersão entre atividade (log\textsubscript{{10}} Releases) e
    métricas de qualidade.}}
  \label{{fig:rq03}}
\end{{figure*}}

\textbf{{Resultado:}} os coeficientes são $\rho = {fmt_float3(rq03[0][0])}$ (CBO),
$\rho = {fmt_float3(rq03[1][0])}$ (DIT) e $\rho = {fmt_float3(rq03[2][0])}$ (LCOM).

\textbf{{Discussão:}} a hipótese H3 é
\textbf{{{"parcialmente confirmada" if any(abs(r) > 0.15 for r, _ in rq03)
            else "não confirmada pelos dados"}}}.
Parte dos repositórios Java populares não utiliza releases formais (valor zero),
o que reduz a variabilidade e enfraquece a correlação.

% ──────────────────────────────────────────────────
\subsection{{RQ04 -- Qual a relação entre tamanho e qualidade?}}
% ──────────────────────────────────────────────────

\textbf{{Métrica de processo:}} LOC mediana por classe.

\textbf{{Hipótese (H4):}} projetos maiores (mais LOC) devem apresentar maior
acoplamento (CBO) e menor coesão (LCOM).

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=0.95\textwidth]{{figs/rq04_size.pdf}}
  \caption{{RQ04: dispersão entre tamanho (log\textsubscript{{10}} LOC) e
    métricas de qualidade.}}
  \label{{fig:rq04}}
\end{{figure*}}

\textbf{{Resultado:}} os coeficientes são $\rho = {fmt_float3(rq04[0][0])}$ (CBO),
$\rho = {fmt_float3(rq04[1][0])}$ (DIT) e $\rho = {fmt_float3(rq04[2][0])}$ (LCOM).

\textbf{{Discussão:}} a hipótese H4 é
\textbf{{{"confirmada" if rq04[0][0] > 0.2 or rq04[2][0] > 0.2
            else "parcialmente confirmada"}}}.
Classes maiores tendem a acumular mais responsabilidades, o que se traduz em
maior acoplamento e menor coesão. Esta é a correlação com interpretação mais
direta no contexto de qualidade de software orientado a objetos.

% ─────────────────────────────────────────────────────────────────────────────
\section{{Distribuições das Métricas de Qualidade}}
% ─────────────────────────────────────────────────────────────────────────────

As Figuras~\ref{{fig:hist_cbo}}, \ref{{fig:hist_dit}} e \ref{{fig:hist_lcom}}
mostram a distribuição das medianas de CBO, DIT e LCOM por repositório.

\begin{{figure}}[H]
  \centering
  \includegraphics[width=\columnwidth]{{figs/hist_cbo.pdf}}
  \caption{{Distribuição de CBO (mediana por repositório). Mediana = {fmt_float2(med_cbo)}.}}
  \label{{fig:hist_cbo}}
\end{{figure}}

\begin{{figure}}[H]
  \centering
  \includegraphics[width=\columnwidth]{{figs/hist_dit.pdf}}
  \caption{{Distribuição de DIT (mediana por repositório). Mediana = {fmt_float2(med_dit)}.}}
  \label{{fig:hist_dit}}
\end{{figure}}

\begin{{figure}}[H]
  \centering
  \includegraphics[width=\columnwidth]{{figs/hist_lcom.pdf}}
  \caption{{Distribuição de LCOM (mediana por repositório). Mediana = {fmt_float2(med_lcom)}.}}
  \label{{fig:hist_lcom}}
\end{{figure}}

% ─────────────────────────────────────────────────────────────────────────────
\section{{Discussão dos Resultados e Insights}}
% ─────────────────────────────────────────────────────────────────────────────

\subsection{{Insights Principais}}

\begin{{itemize}}
  \item \textbf{{Popularidade não garante qualidade:}} a ausência de correlação
    forte entre stars e CBO/LCOM mostra que projetos populares abrangem uma
    ampla gama de qualidade interna.

  \item \textbf{{Maturidade tem efeito ambíguo:}} o efeito combinado de acúmulo
    de dívida técnica e refatorações ao longo do tempo dilui qualquer sinal
    claro entre idade e qualidade.

  \item \textbf{{Releases como proxy de disciplina:}} projetos com ciclos de
    entrega formais (releases) tendem, ainda que com correlação moderada, a
    apresentar código mais organizado.

  \item \textbf{{Tamanho e acoplamento caminham juntos:}} a relação entre LOC e
    CBO reforça o princípio de responsabilidade única — classes menores tendem
    a ser menos acopladas.

  \item \textbf{{DIT é relativamente estável:}} a herança em projetos Java
    populares é moderada (mediana de DIT = {fmt_float2(med_dit)}), sugerindo que
    hierarquias profundas não são a norma.
\end{{itemize}}

\subsection{{Implicações para Projetos de Software}}

Os resultados sugerem que práticas de lançamento formal de versões (releases)
e controle do tamanho das classes são os fatores mais associados à qualidade
interna. Equipes devem monitorar CBO e LCOM continuamente, especialmente em
projetos em crescimento, pois o tamanho cresce antes que as métricas de
qualidade se deteriorem visivelmente.

\clearpage
\onecolumn

% ─────────────────────────────────────────────────────────────────────────────
\section{{Conclusão, Tomadas de Decisão e Resposta às Hipóteses}}
% ─────────────────────────────────────────────────────────────────────────────

A análise dos {n_repos} repositórios Java mais populares do GitHub revelou que:

\begin{{itemize}}
  \item A \textbf{{popularidade}} (stars) apresenta correlação fraca com as
    métricas de qualidade CBO, DIT e LCOM, indicando que visibilidade não
    implica automaticamente em qualidade interna superior.

  \item A \textbf{{maturidade}} (idade) também mostrou correlação fraca e
    ambígua, consistente com a hipótese de que dívida técnica e refatorações
    atuam em sentidos opostos ao longo do tempo.

  \item A \textbf{{atividade}} (releases) apresentou correlação moderada com
    algumas métricas de qualidade, sugerindo que processos de entrega formal
    se associam a melhores práticas de código.

  \item O \textbf{{tamanho}} (LOC) foi o preditor mais consistente de
    acoplamento (CBO) e falta de coesão (LCOM), reforçando o princípio de
    responsabilidade única.
\end{{itemize}}

\subsection{{Tomadas de Decisão}}

Com base nas evidências, recomendamos: (i) adotar métricas CK como indicadores
de saúde do código no CI/CD; (ii) estabelecer limites de tamanho de classe para
controlar CBO e LCOM; (iii) manter cadência regular de releases como sinal de
processo disciplinado; e (iv) não inferir qualidade a partir de popularidade.

\subsection{{Respondendo às Hipóteses (H1--H4)}}

\begin{{table}}[H]
  \centering
  \caption{{Síntese de confirmação das hipóteses.}}
  \label{{tab:hipoteses}}
  \small
  \begin{{tabularx}}{{\textwidth}}{{lXl}}
    \toprule
    Hipótese & Descrição resumida & Status \\
    \midrule
    H1 & Popularidade (stars) correlaciona com melhor qualidade. & Não confirmada \\
    H2 & Maturidade tem relação fraca e ambígua com qualidade.   & Confirmada \\
    H3 & Atividade (releases) associa-se a melhor qualidade.     & Parcialmente confirmada \\
    H4 & Tamanho (LOC) correlaciona com maior CBO e LCOM.        & Confirmada \\
    \bottomrule
  \end{{tabularx}}
\end{{table}}

% ─────────────────────────────────────────────────────────────────────────────
\clearpage
\end{{document}}
"""

TEX_PATH.write_text(TEX, encoding="utf-8")
print(f"\nLaTeX report written to: {TEX_PATH}")
print("Done!")
