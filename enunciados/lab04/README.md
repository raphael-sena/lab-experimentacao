# Lab04 — Dashboard de Caracterização do Dataset (Lab04S01)

Dashboard de **visualização de dados** construído com **React + Tailwind CSS v4 + Recharts**,
para a disciplina de Laboratório de Experimentação de Software.

O estudo compara **Pull Requests gerados por agentes de IA autônomos** (`IA_autonomo`)
com **PRs assistidos por IA e confirmados por humanos** (`humano_confirmado`), em ~202 mil
PRs de ~1.290 repositórios, particionados por **linguagem** e **agente de IA**.

## Como rodar

```bash
npm install
npm run dev      # ambiente de desenvolvimento (http://localhost:5173)
npm run build    # build de produção
npm run preview  # serve o build
```

> A aplicação roda imediatamente: se o CSV real não puder ser lido, um conjunto de
> **dados mockados** (mesma estrutura) é exibido automaticamente.

## Arquitetura

```
public/docs/data/        CSVs do estudo (servidos estaticamente)
  dataset_final.csv      ~29 MB · 202k linhas · dataset principal
  resultados_estatisticos.csv  testes IA vs. humano

src/
  workers/csvWorker.js   Lê e AGREGA o CSV em um Web Worker (streaming via PapaParse),
                         sem travar a UI. Retorna apenas um resumo compacto.
  hooks/useDataset.js    Orquestra o worker (progresso + fallback para mock)
  hooks/useStats.js      Lê o CSV de resultados estatísticos (pequeno)
  lib/                   constants (config do dataset), format (pt-BR), mockSummary
  components/            Header, KPIs, CentralTendency, charts (Recharts), tabelas
  App.jsx                Composição das seções do dashboard
```

### Por que um Web Worker?

O `dataset_final.csv` tem ~29 MB / 202 mil linhas. Carregá-lo na thread principal
travaria a interface. O worker faz **streaming linha a linha** (callback `step` do
PapaParse), acumula contagens/medianas/histogramas e devolve só o resultado agregado.

### Seções do dashboard

1. **Visão geral** — KPIs (total de PRs, repositórios, linguagens, agentes, taxas de revisão/revert).
2. **Tendência central** — mediana, média e P25–P75 das principais métricas.
3. **Composição por subgrupos** — distribuição por linguagem (donut) e por agente (barras).
4. **Forma das distribuições** — histogramas de diff e tempo até o merge.
5. **Comparação entre linguagens** — mediana/média por métrica selecionável.
6. **Comparação entre grupos** — IA autônoma vs. humano (com aviso de assimetria amostral).
7. **Testes estatísticos (bônus)** — tabela de significância.
8. **Amostra dos dados brutos** — primeiras linhas do CSV.

## Stack

- **React 19** + **Vite**
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **Recharts** — gráficos responsivos
- **PapaParse** — leitura/streaming de CSV
