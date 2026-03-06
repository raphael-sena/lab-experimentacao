# Lab 01 – Características de Repositórios Populares do GitHub

> **Disciplina:** Laboratório de Experimentação de Software  
> **Autores:** Raphael Brito e Yan Cota  
> **PUC Minas – 2026/1**

---

## Sumário

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Token do GitHub](#token-do-github)
- [Execução](#execução)
  - [1. Coleta de dados (Sprint 1 – até 100 repositórios)](#1-coleta-de-dados-sprint-1--até-100-repositórios)
  - [2. Coleta de dados (Sprint 2 – 1000 repositórios com paginação)](#2-coleta-de-dados-sprint-2--1000-repositórios-com-paginação)
  - [3. Geração do relatório (gráficos + LaTeX)](#3-geração-do-relatório-gráficos--latex)
- [Compilação do Relatório LaTeX](#compilação-do-relatório-latex)
- [Questões de Pesquisa](#questões-de-pesquisa)
- [Saídas Geradas](#saídas-geradas)

---

## Visão Geral

Este projeto minera dados da **API GraphQL do GitHub** para analisar características dos 1 000 repositórios mais estrelados da plataforma, respondendo às seguintes questões de pesquisa (RQs):

| # | Questão | Métrica |
|---|---------|---------|
| RQ 01 | Sistemas populares são maduros/antigos? | Idade do repositório (dias desde a criação) |
| RQ 02 | Sistemas populares recebem muita contribuição externa? | Total de Pull Requests aceitas (merged) |
| RQ 03 | Sistemas populares lançam releases com frequência? | Total de releases |
| RQ 04 | Sistemas populares são atualizados com frequência? | Dias desde a última atualização |
| RQ 05 | Sistemas populares são escritos nas linguagens mais populares? | Linguagem primária do repositório |
| RQ 06 | Sistemas populares possuem alto percentual de issues fechadas? | Razão issues fechadas / total de issues |
| RQ 07 *(bônus)* | Linguagens influenciam contribuição, releases e frequência de atualização? | RQs 02, 03 e 04 segmentadas por linguagem |

---

## Estrutura do Projeto

```
enunciado_um/
├── code/
│   ├── .env                  # ← você cria este arquivo (veja abaixo)
│   ├── github_gql.py         # cliente GraphQL com retry/backoff
│   ├── main.py               # coleta Sprint 1 (até 100 repos, sem paginação)
│   ├── main_sprint2.py       # coleta Sprint 2 (até 1000 repos, com paginação)
│   ├── generate_report.py    # gera gráficos e escreve relatorio.tex
│   └── repos.csv             # CSV gerado após a coleta
└── docs/
    ├── relatorio.tex         # gerado por generate_report.py
    ├── relatorio.pdf         # compilado a partir do .tex
    └── figs/                 # gráficos .pdf gerados automaticamente
```

---

## Pré-requisitos

| Ferramenta | Versão mínima | Observação |
|---|---|---|
| Python | 3.11+ | Testado com 3.13 |
| pip | qualquer | incluso no Python |
| TeX Live / MiKTeX | qualquer recente | para compilar o `.tex` em PDF |

### Instalação do LaTeX no Windows

Baixe e instale o **MiKTeX** (recomendado para Windows):  
<https://miktex.org/download>

Após a instalação, o comando `pdflatex` estará disponível em um novo terminal.  
O MiKTeX instala pacotes ausentes automaticamente na primeira compilação.

---

## Configuração do Ambiente

```powershell
# 1. Entre na pasta do código
cd enunciado_um\code

# 2. Crie e ative um ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install requests python-dotenv matplotlib numpy
```

---

## Token do GitHub

A API GraphQL do GitHub exige autenticação. Crie um **Personal Access Token (classic)** em:  
<https://github.com/settings/tokens>

Permissões necessárias: `public_repo` (ou apenas leitura pública).

Depois, crie o arquivo `code/.env` com o seguinte conteúdo:

```dotenv
GITHUB_TOKEN=ghp_SEU_TOKEN_AQUI
```

> **Atenção:** nunca faça commit deste arquivo. Ele já deve estar no `.gitignore`.

---

## Execução

### 1. Coleta de dados (Sprint 1 – até 100 repositórios)

```powershell
# dentro de code/ com o .venv ativado
python main.py
```

O script pergunta quantos repositórios buscar (padrão: 100, máximo: 1000).  
Ao final, exibe um relatório resumido no terminal.

---

### 2. Coleta de dados (Sprint 2 – 1000 repositórios com paginação)

```powershell
python main_sprint2.py
```

- Utiliza paginação cursor-based para superar o limite de 100 itens por requisição.  
- Coleta métricas detalhadas (PRs, releases, issues) em lotes de 4 repositórios.  
- Ao final, exporta todos os dados para `code/repos.csv`.

> A coleta completa de 1 000 repositórios pode levar **entre 15 e 30 minutos** dependendo do rate limit da API.

---

### 3. Geração do relatório (gráficos + LaTeX)

```powershell
python generate_report.py
```

O script:
1. Lê `code/repos.csv`.
2. Gera os gráficos em `docs/figs/` (formato PDF, prontos para inclusão no LaTeX).
3. Escreve/sobrescreve `docs/relatorio.tex` com o relatório completo.

---

## Compilação do Relatório LaTeX

Com o MiKTeX instalado e `pdflatex` disponível no PATH, execute a partir da pasta `docs/`:

```powershell
cd ..\docs

# Compile duas vezes para gerar índices e referências corretamente
pdflatex relatorio.tex
pdflatex relatorio.tex
```

O arquivo `relatorio.pdf` será gerado na mesma pasta.

> **Dica:** se algum pacote LaTeX não estiver instalado, o MiKTeX solicitará instalação automática durante a primeira compilação. Aceite as instalações.

---

## Questões de Pesquisa

Veja a seção [Visão Geral](#visão-geral) para o mapeamento completo de RQs e métricas.

O relatório gerado apresenta, para cada RQ:
- **Hipótese informal** elaborada antes da análise.
- **Metodologia** de coleta e cálculo.
- **Resultados** com valores medianos e gráficos.
- **Discussão** comparando hipóteses com os dados obtidos.

---

## Saídas Geradas

| Arquivo | Descrição |
|---|---|
| `code/repos.csv` | Dataset bruto com todos os repositórios coletados |
| `docs/figs/rq01_age.pdf` | Distribuição de idades dos repositórios |
| `docs/figs/rq02_prs.pdf` | Distribuição de PRs merged |
| `docs/figs/rq03_releases.pdf` | Distribuição de releases |
| `docs/figs/rq04_update.pdf` | Distribuição de dias desde a última atualização |
| `docs/figs/rq05_langs.pdf` | Contagem por linguagem primária |
| `docs/figs/rq06_issues.pdf` | Distribuição da razão de issues fechadas |
| `docs/figs/rq07a_prs_lang.pdf` | PRs por linguagem (bônus) |
| `docs/figs/rq07b_releases_lang.pdf` | Releases por linguagem (bônus) |
| `docs/figs/rq07c_update_lang.pdf` | Atualização por linguagem (bônus) |
| `docs/relatorio.tex` | Relatório em LaTeX |
| `docs/relatorio.pdf` | Relatório compilado em PDF |

