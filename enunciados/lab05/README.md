# Laboratório 05: GraphQL vs. REST - Um Experimento Controlado

Este diretório contém a estrutura completa para a condução de um experimento controlado comparando o desempenho e a eficiência das APIs **REST** e **GraphQL** do GitHub, utilizando como alvo o repositório público [official-stockfish/Stockfish](https://github.com/official-stockfish/Stockfish).

---

## 🎯 Objetivo e Perguntas de Pesquisa
O experimento visa responder de forma estatisticamente rigorosa a duas perguntas fundamentais:
*   **RQ1 (Tempo de Resposta):** As respostas às consultas GraphQL são mais rápidas do que às consultas REST?
*   **RQ2 (Tamanho do Payload):** As respostas às consultas GraphQL possuem tamanho menor (em bytes) do que às consultas REST?

---

## 📁 Estrutura do Projeto e Caminhos dos Dados

Toda a lógica operacional, scripts de consulta, processamento, análise e visualização estão localizados na pasta [code/](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code).

Abaixo estão os atalhos para os principais artefatos e dados tratados:

| Artefato | Descrição | Localização / Link |
| :--- | :--- | :--- |
| **Documentação Técnica** | Detalhes do Desenho Experimental, Hipóteses, Variáveis, Ameaças e Guia Executivo. | [code/README.md](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/README.md) |
| **Dados Brutos (Raw)** | Log temporal de todas as requisições bem-sucedidas com tempo de resposta (ms) e tamanho (bytes). | [data/raw_data.csv](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/data/raw_data.csv) |
| **Dados Tratados (Dashboard)** | Estatísticas descritivas calculadas (médias, medianas, totais de tráfego) prontas para importação em ferramentas de BI. | [data/processed_data.csv](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/data/processed_data.csv) |
| **Sumário JSON** | Dados descritivos estruturados em formato JSON para integração com dashboards web. | [data/processed_summary.json](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/data/processed_summary.json) |
| **Resultados Estatísticos** | Resultados detalhados dos testes de Shapiro-Wilk, Mann-Whitney U, Welch's T-Test e Cliff's Delta. | [data/statistical_results.txt](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/data/statistical_results.txt) |
| **Gráficos Gerados** | Boxplots de latência e gráficos de barra comparando o tamanho em KB dos payloads de rede. | [code/plots/](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/plots/) |

---

## 📊 Estrutura dos Dados Tratados para Dashboards

O arquivo [processed_data.csv](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/data/processed_data.csv) é o arquivo ideal para alimentar dashboards em ferramentas como **Power BI**, **Tableau**, **Metabase**, ou aplicações frontend (usando bibliotecas como Chart.js ou D3.js). 

A estrutura do arquivo contém as seguintes colunas calculadas:
*   `endpoint`: Recurso avaliado (`repo`, `commits`, `issues`, `pulls`).
*   `api_type`: Paradigma tecnológico (`REST` ou `GraphQL`).
*   `count_latency_ms`: Quantidade de medições bem-sucedidas efetuadas ($N$).
*   `mean_latency_ms`: Média aritmética do tempo de resposta (ms).
*   `median_latency_ms`: Mediana do tempo de resposta (ms) (ideal para mitigar efeitos de outliers de rede).
*   `std_latency_ms`: Desvio padrão do tempo de resposta.
*   `min_latency_ms` / `max_latency_ms`: Limites inferior e superior de latência obtidos.
*   `mean_size_bytes`: Média do tamanho da resposta em bytes.
*   `median_size_bytes`: Mediana do tamanho da resposta em bytes.
*   `std_size_bytes`: Desvio padrão do tamanho da resposta.
*   `min_size_bytes` / `max_size_bytes`: Limites inferior e superior de tamanho dos payloads.
*   `total_size_bytes`: Volume total de bytes trafegados durante o experimento (essencial para calcular a economia absoluta de banda).

---

## ⚡ Guia Rápido de Execução Manual

Para que você possa rodar o experimento manualmente na sua máquina e gerar todos os dados descritos acima, siga este roteiro de comandos na pasta [code/](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code):

1.  **Instalar dependências**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configurar credenciais**:
    *   Copie `.env.example` para `.env`
    *   Insira seu token do GitHub na variável `GITHUB_TOKEN` no arquivo `.env`.
3.  **Executar Coleta (Real)**:
    ```bash
    python collector.py
    ```
    *   *(Opcional - Simulação rápida)*: Para testar a visualização e estatísticas sem precisar criar tokens do GitHub, você pode gerar dados sintéticos estatisticamente realistas rodando: `python generate_samples.py`.
4.  **Processar Dados**:
    ```bash
    python processor.py
    ```
5.  **Executar Análise Estatística**:
    ```bash
    python analyzer.py
    ```
6.  **Gerar Gráficos**:
    ```bash
    python visualizer.py
    ```

Para ver explicações completas sobre a teoria estatística aplicada (teste de Shapiro-Wilk para normalidade, teste de Mann-Whitney U para significância e Cliff's Delta para efeito de tamanho), consulte o arquivo de [Metodologia e Desenho do Experimento](file:///c:/Git/%20Puc/lab-experimentacao/enunciados/lab05/code/README.md).
