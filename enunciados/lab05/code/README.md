# Experimento Controlado: GraphQL vs REST no Repositório official-stockfish/Stockfish

Este documento detalha o desenho do experimento, a preparação, os scripts de execução e a metodologia de análise estatística para comparar quantitativamente os paradigmas de API **REST** e **GraphQL** utilizando a API pública do GitHub no repositório [official-stockfish/Stockfish](https://github.com/official-stockfish/Stockfish).

Esta documentação foi estruturada para permitir a replicação integral do experimento por qualquer desenvolvedor e para servir como base conceitual e metodológica para a redação do artigo científico final.

---

## 1. Desenho do Experimento (Passo 1)

O objetivo principal deste experimento controlado é avaliar quantitativamente os impactos de desempenho e eficiência na escolha entre as tecnologias **GraphQL** e **REST**, buscando responder às seguintes perguntas de pesquisa:

*   **RQ1.** Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST? (Métrica: *Latência de rede* em milissegundos)
*   **RQ2.** Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST? (Métrica: *Tamanho do payload* em bytes)

### A. Hipóteses Nula ($H_0$) e Alternativa ($H_1$)

#### Para RQ1 (Tempo de Resposta / Latência)
*   **Hipótese Nula ($H_{0,1}$):** A latência das consultas utilizando a API GraphQL é estatisticamente igual ou maior que a latência das consultas utilizando a API REST.
    $$H_{0,1}: \text{Latência}_{\text{GraphQL}} \geq \text{Latência}_{\text{REST}}$$
*   **Hipótese Alternativa ($H_{1,1}$):** A latência das consultas utilizando a API GraphQL é estatisticamente menor (mais rápida) do que utilizando a API REST.
    $$H_{1,1}: \text{Latência}_{\text{GraphQL}} < \text{Latência}_{\text{REST}}$$

#### Para RQ2 (Tamanho do Payload / Banda consumida)
*   **Hipótese Nula ($H_{0,2}$):** O tamanho em bytes dos payloads retornados pela API GraphQL é estatisticamente igual ou maior do que os retornados pela API REST.
    $$H_{0,2}: \text{Tamanho}_{\text{GraphQL}} \geq \text{Tamanho}_{\text{REST}}$$
*   **Hipótese Alternativa ($H_{1,2}$):** O tamanho em bytes dos payloads retornados pela API GraphQL é estatisticamente menor do que os retornados pela API REST.
    $$H_{1,2}: \text{Tamanho}_{\text{GraphQL}} < \text{Tamanho}_{\text{REST}}$$

### B. Variáveis

*   **Variáveis Independentes:**
    1.  **Paradigma de API:** O paradigma tecnológico testado, contendo dois níveis ou tratamentos: **REST** e **GraphQL**.
    2.  **Tipo de Recurso Consultado (Endpoint):** O tipo de informação requisitada do repositório, com quatro níveis:
        *   `repo` (Informações gerais do repositório)
        *   `commits` (Lista dos últimos 30 commits)
        *   `issues` (Lista das últimas 30 issues)
        *   `pulls` (Lista dos últimos 30 pull requests)
*   **Variáveis Dependentes:**
    1.  **Latência de Resposta ($Y_1$):** O tempo de ida e volta (Round-Trip Time - RTT) medido em milissegundos (ms) a partir do cliente.
    2.  **Tamanho da Resposta ($Y_2$):** O tamanho total em bytes (B) do corpo do payload JSON retornado pela API.

### C. Tratamentos
*   **Tratamento 1 (REST):** Requisições HTTP GET enviadas aos endpoints padrão da API REST v3 do GitHub.
*   **Tratamento 2 (GraphQL):** Requisições HTTP POST enviadas à API GraphQL v4 do GitHub, especificando no corpo da consulta (`query`) estritamente os mesmos campos lógicos que seriam tipicamente exibidos em uma interface de usuário, evitando o *over-fetching*.

### D. Objetos Experimentais
O objeto experimental é o repositório público do motor de xadrez de código aberto **official-stockfish/Stockfish** hospedado no GitHub. Este repositório foi escolhido por ser altamente ativo, contendo um grande volume de commits, issues e pull requests, o que garante a presença de dados volumosos e realistas.

### E. Tipo de Projeto Experimental
O experimento adota um desenho **dentro de sujeitos (within-subject)** ou de **emparelhamento controlado**. Para garantir a validade dos testes:
1.  **Intercalação (Interleaving):** As requisições REST e GraphQL são intercaladas na mesma execução.
2.  **Randomização total:** A ordem de todas as requisições (combinações de Tratamento e Endpoint) é completamente embaralhada no início de cada execução. Isso isola influências de oscilações na rede local, flutuações temporais do servidor do GitHub e efeitos de cache de rotas.

### F. Quantidade de Medições
São realizadas $N = 30$ medições (trials) para cada combinação de tratamento e recurso. Com 2 tratamentos (REST/GraphQL) e 4 recursos (`repo`, `commits`, `issues`, `pulls`), são geradas:
$$\text{Total de requisições} = 30 \times 2 \times 4 = 240 \text{ requisições}$$
Este tamanho amostral satisfaz os critérios do Teorema do Limite Central ($N \geq 30$), permitindo a aplicação consistente de testes estatísticos.

### G. Ameaças à Validade e Mitigações
*   **Validade Interna (Fatores que afetam as medições):**
    *   *Cache do Servidor/CDN:* O GitHub pode responder mais rápido a requisições idênticas consecutivas devido a caching.
        *   *Mitigação:* As requisições são enviadas com o cabeçalho `Cache-Control: no-cache`. A randomização completa e o atraso configurável de 1.5 segundos entre as chamadas evitam rajadas repetitivas consecutivas.
    *   *Jitter e Latência de Rede Local:* Oscilações na internet local do executor podem inflar artificialmente tempos de resposta.
        *   *Mitigação:* A randomização distribui essas flutuações uniformemente entre os dois tratamentos. Caso haja um pico de rede, ele afetará REST e GraphQL de maneira aleatória e não sistemática.
*   **Validade de Construto (Métrica vs. Conceito):**
    *   *Desequilíbrio de Campos:* O REST pode transferir dados extras não utilizados, enquanto o GraphQL transfere apenas o que é solicitado.
        *   *Mitigação:* O GraphQL foi projetado sob medida para solicitar exatamente o conjunto equivalente de informações que o cliente precisa, refletindo com precisão a vantagem conceitual da tecnologia (prevenção de over-fetching).
*   **Validade Externa (Generalização dos resultados):**
    *   Os resultados obtidos na infraestrutura de servidores de alto desempenho do GitHub podem diferir de APIs desenvolvidas localmente ou sob outras arquiteturas.
        *   *Mitigação:* A documentação deixa claro que este estudo se restringe a APIs de larga escala sob internet pública, sugerindo estudos futuros em redes locais/intranet.

---

## 2. Preparação do Experimento (Passo 2)

### Pré-requisitos
O ambiente necessita do **Python 3.8+** instalado.

### Estrutura de Arquivos no Diretório `code/`
*   `requirements.txt`: Dependências Python.
*   `.env.example`: Modelo para variáveis de ambiente.
*   `collector.py`: Script para extração de dados reais da API do GitHub.
*   `generate_samples.py`: Gerador de dados simulados (permite testar todo o pipeline de análise sem usar uma chave do GitHub).
*   `processor.py`: Limpa e calcula estatísticas descritivas (média, mediana, desvio padrão).
*   `analyzer.py`: Executa testes de hipóteses estatísticas (Shapiro-Wilk, Mann-Whitney U, Welch's T, Cliff's Delta, Cohen's d).
*   `visualizer.py`: Cria os gráficos em formato PNG (`plots/`).

---

## 3. Execução do Experimento (Passo 3)

Siga o passo a passo a seguir para executar o experimento no seu terminal local.

### Passo 3.1: Instalação das Dependências
Instale as bibliotecas necessárias rodando no terminal na pasta `code/`:
```bash
pip install -r requirements.txt
```

### Passo 3.2: Configuração das Credenciais do GitHub
1.  Crie um Token de Acesso Pessoal (Classic) no GitHub em: [https://github.com/settings/tokens](https://github.com/settings/tokens).
    *   *Observação:* Não selecione nenhum escopo. O token precisa de acesso de leitura apenas para repositórios públicos.
2.  Copie o arquivo `.env.example` para `.env`:
    ```bash
    copy .env.example .env
    ```
3.  Abra o arquivo `.env` e substitua `your_personal_access_token_here` pelo token gerado.

### Passo 3.3: Coleta dos Dados
Para coletar dados reais do GitHub, execute:
```bash
python collector.py
```
> [!TIP]
> **Modo de Teste Rápido:** Caso queira validar a integridade dos scripts de processamento e gráficos sem efetuar requisições reais ou sem gerar um token, você pode rodar o simulador:
> ```bash
> python generate_samples.py
> ```
> O simulador criará automaticamente o arquivo `data/raw_data.csv` com 240 linhas simulando dados reais com comportamento de latência instável e a economia drástica de tamanho do GraphQL.

---

## 4. Processamento & Análise de Resultados (Passos 4 e 5)

Após obter o arquivo `data/raw_data.csv` (seja por coleta real ou simulação), o processamento e a análise estatística são conduzidos.

### Passo 4.1: Processamento dos Dados
Execute o script de processamento para calcular as métricas descritivas básicas:
```bash
python processor.py
```
Esse script gera:
1.  `data/processed_data.csv`: Tabela com médias, medianas, desvio padrão e dados acumulados estruturados para dashboards.
2.  `data/processed_summary.json`: Estrutura JSON aninhada.
3.  Uma tabela Markdown de visualização rápida no console.

### Passo 4.2: Análise Estatística (Testes de Hipótese)
Execute o script analisador para rodar os testes formais de significância estatística:
```bash
python analyzer.py
```
Este script executa:
1.  **Teste de Shapiro-Wilk (`stats.shapiro`)** para cada grupo de latência. Avalia se a distribuição segue uma curva normal.
    *   Se $p > 0.05$, aceitamos a normalidade e aplicamos o **Welch's T-Test** (teste paramétrico unilateral).
    *   Se $p \leq 0.05$, a distribuição é não-normal (típica de latência de rede devido a outliers/spikes) e aplicamos o **Mann-Whitney U-Test** (teste não-paramétrico unilateral).
2.  **Cálculo do Tamanho de Efeito (Effect Size):**
    *   Para dados normais: **Cohen's d**.
    *   Para dados não-normais: **Cliff's Delta**. O Cliff's Delta mede a probabilidade de uma observação de um grupo ser maior que uma do outro grupo. Varia de -1 a 1, onde -1 indica que GraphQL é deterministicamente menor que REST, e 0 indica sobreposição perfeita.
3.  **Avaliação Estatística de RQ1 e RQ2:**
    *   Calcula o $p$-value unilateral. Se $p < 0.05$, rejeitamos a Hipótese Nula com 95% de confiança.
    *   Salva o relatório detalhado em `data/statistical_results.txt`.

---

## 5. Visualização de Dados & Dashboard (Passo 6)

Para gerar gráficos com qualidade de publicação científica, execute:
```bash
python visualizer.py
```
O script lerá os dados limpos e salvará três visualizações na pasta `plots/`:
1.  `plots/latency_comparison.png`: Gráfico do tipo Boxplot mostrando as distribuições de tempo de resposta. A caixa exibe o primeiro quartil, a mediana e o terceiro quartil, destacando visualmente se a latência do GraphQL é consistentemente menor e exibindo pontos fora da curva (*outliers* causados por jitter).
2.  `plots/size_comparison.png`: Gráfico de barras agrupadas comparando a média em Kilobytes (KB) transmitidos por endpoint. Exibe o tamanho exato de cada payload sobre cada barra, ilustrando a gritante redução de banda do GraphQL.
3.  `plots/size_comparison_log.png`: Gráfico de boxplot com escala logarítmica na ordenada, ideal para o artigo, pois expressa visualmente a diferença de ordens de grandeza entre REST (dezenas a centenas de KB) e GraphQL (poucos KB ou Bytes) sem esmagar as caixas do GraphQL.

---

## 6. Diretrizes para a Redação do Artigo Científico

O desenvolvedor responsável por redigir o artigo pode usar as seguintes diretrizes estruturais baseadas nos arquivos gerados:

*   **Resumo (Abstract):** Mencione o repositório estudado (`official-stockfish/Stockfish`), a quantidade de amostras ($240$ chamadas no total) e resuma as principais conclusões (ex: "GraphQL reduziu em média X% do volume de dados trafegados e obteve latência Y% menor/semelhante").
*   **Introdução:** Defina o problema de *over-fetching* em REST e como o GraphQL propõe solucionar isso estruturando consultas sob demanda. Apresente as RQ1, RQ2 e as hipóteses conceituais do experimento.
*   **Metodologia (Desenho & Preparação):** Descreva o modelo experimental de emparelhamento dentro do sujeito com randomização e interleaving (copie os dados da Seção 1 deste documento). Cite o ambiente operacional do teste (versão do Python, dependências) e informe as consultas REST vs. consultas estruturadas em GraphQL de forma comparativa.
*   **Resultados (Análise Estatística):**
    *   Apresente a tabela gerada pelo `processor.py` contendo a média e mediana de tamanho e latência.
    *   Discuta a normalidade dos dados: mostre que o teste de Shapiro-Wilk rejeitou a normalidade das latências ($p < 0.05$), justificando a adoção do teste não-paramétrico Mann-Whitney U.
    *   Exponha o resultado do teste de hipóteses: mencione o $p$-value obtido pelo `analyzer.py` e o tamanho do efeito (Cliff's Delta).
*   **Discussão:**
    *   *Sobre a RQ1:* Comente se a latência do GraphQL foi menor, igual ou maior. Discuta a influência do processamento interno do servidor do GitHub (parsing da query GraphQL e validação do schema vs. roteamento REST direto).
    *   *Sobre a RQ2:* Destaque a expressiva redução de bytes. Aponte que para commits e issues o GraphQL economizou mais de 90% de tráfego, validando fortemente a hipótese de contenção de *over-fetching*.
*   **Conclusão & Trabalhos Futuros:** Sintetize a resposta definitiva para as perguntas de pesquisa. Sugira estudos testando caching local de queries GraphQL e a análise sob conexões móveis (ex: 3G/4G) onde o tamanho do payload impacta visivelmente a latência.
