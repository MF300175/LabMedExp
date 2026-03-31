# Plano de Implementação – Lab-02
## Estudo de Características de Qualidade de Sistemas Java

**Disciplina:** Laboratório de Experimentação de Software  
**Período:** 6º período  
**Avaliação:** 20 pontos  
**Data de Criação:** 23 de março de 2026

---

## 1. Objetivo Geral

Analisar aspectos de qualidade interna de repositórios Java através de métricas de produto (CBO, DIT, LCOM) correlacionando-os com características do processo de desenvolvimento (popularidade, maturidade, atividade, tamanho), respondendo a 4 questões de pesquisa definidas no enunciado.

---

## 2. Questões de Pesquisa (RQs)

| RQ | Questão | Métrica de Processo | Métrica de Qualidade |
|---|---------|---------------------|---------------------|
| **RQ 01** | Qual a relação entre a popularidade dos repositórios e as suas características de qualidade? | Estrelas (★) | CBO, DIT, LCOM |
| **RQ 02** | Qual a relação entre a maturidade do repositórios e as suas características de qualidade? | Idade (anos) | CBO, DIT, LCOM |
| **RQ 03** | Qual a relação entre a atividade dos repositórios e as suas características de qualidade? | Nº de releases | CBO, DIT, LCOM |
| **RQ 04** | Qual a relação entre o tamanho dos repositórios e as suas características de qualidade? | LOC + Comentários | CBO, DIT, LCOM |

---

## 3. Definições de Métricas

### 3.1 Métricas de Processo (Características do Repositório)

- **Popularidade:** número de estrelas (★)
- **Maturidade:** idade em anos do repositório (desde criação)
- **Atividade:** número total de releases
- **Tamanho:** linhas de código (LOC) e linhas de comentários
  - Medição planejada via `cloc` durante a Sprint S02 (após o clone local).

### 3.2 Métricas de Qualidade (Ferramenta CK)

- **CBO (Coupling Between Objects):** Número de classes distintas às quais uma classe está acoplada
- **DIT (Depth of Inheritance Tree):** Profundidade máxima da hierarquia de herança de uma classe
- **LCOM (Lack of Cohesion Of Methods):** Medida de coesão entre métodos de uma classe

### 3.3 Estatísticas por Repositório

Para cada métrica de qualidade, calcular:
- **Mediana**
- **Média**
- **Desvio Padrão**

---

## 4. Estrutura de Sprints

O projeto é divisível em **3 sprints principais** alinhados com a estrutura de pastas:

```
Lab-02/
├── Lab-02S01/  (Sprint 1: Preparação e coleta inicial)
├── Lab-02S02/  (Sprint 2: Coleta em massa e análise exploratória)
└── Lab-02S03/  (Sprint 3: Análise, visualização e relatório final)
```

### 4.1 Timeline de Entregas

| Sprint | Nome | Pontos | Prazo | Descrição |
|--------|------|--------|-------|-----------|
| **S01** | Coleta Inicial e Automação | 5 | ~40% do projeto | Lista dos 1.000 repositórios + Script + CSV (1 repo) |
| **S02** | Coleta em Massa e Hipóteses | 5 | ~70% do projeto | CSV com 1.000 repositórios + Hipóteses para RQs |
| **S03** | Análise Final e Relatório | 10 | 100% do projeto | Análise exploratória + Gráficos + Relatório final |

---

## 5. Sprint 1 – Lab-02S01: Coleta Inicial e Automação

**Duração:** ~2 semanas  
**Pontos:** 5 pontos  
**Objetivo:** Estabelecer pipeline de coleta de dados e validar processo com 1 repositório

### 5.1 Tarefas Sequenciais

#### **Tarefa 1.1:** Recuperar Lista de 1.000 Repositórios Java
- **Descrição:** Utilizar a API GitHub (GraphQL ou REST) para obter os top-1.000 repositórios Java mais populares
- **Entrada:** GitHub Token (variável de ambiente `GITHUB_TOKEN`)
- **Saída:** 
  - `data/repos_1000.json` – Lista em JSON com dados brutos (name, url, stars, created_at, updated_at, releases count, etc.)
  - `data/repos_1000.csv` – Versão resumida em CSV (repositório, URL, estrelas, data criação, releases, linguagem primária)
- **Tecnologia:** Python + `requests` ou `PyGithub` library
- **Observações:**
  - Implementar paginação para respeitar limites da API
  - Adicionar retentativas (backoff exponencial) em caso de rate-limiting
  - Registrar logs de execução (timestamp, repositórios coletados, erros)

#### **Tarefa 1.2:** Instalar e Configurar Ferramenta CK
- **Descrição:** Fazer download e validar instalação da ferramenta CK (Java)
- **Inputs:** Nenhum (ferramenta externa)
- **Saída:**
  - CK instalado, versão verificada
  - Script `run_ck.sh` / `run_ck.bat` (conforme SO)
  - Validação: CK consegue analisar code sample e gerar CSVs
- **Tecnologia:** CK (ferramenta em Java)
- **Observações:**
  - Verificar dependência com JDK; instalar se necessário
  - Testar em um repositório pequeno primeiro

#### **Tarefa 1.3:** Implementar Script de Automação (Clone + CK)
- **Descrição:** Criar script Python para: clonar 1 repositório → analisar com CK → coletar métricas
- **Entrada:** URL do repositório, diretório de trabalho
- **Saída:**
  - Repositório clonado em diretório temporário
  - Arquivos CSV do CK (class.csv, method.csv, field.csv, etc.)
  - Arquivo `metrics_summary.csv` consolidado com estatísticas
- **Tecnologia:** Python (`os`, `subprocess`, `pandas`)
- **Estrutura:**
  ```python
  # script: collect_sample_metrics.py
  def clone_repo(url, dest):
      # git clone ...
      
  def run_ck_analysis(repo_path):
      # executa CK
      # retorna caminhos dos CSVs
      
  def aggregate_metrics(csv_files):
      # sumariza CBO, DIT, LCOM (média, mediana, desvio padrão)
      # retorna dict com estatísticas
      
  def main(repo_url, output_file):
      # orquestra as 3 etapas
  ```
- **Observações:**
  - Limpar repositório clonado após análise (espaço em disco)
  - Tratar exceções (clone falha, CK falha)
  - Salvar logs detalhados

#### **Tarefa 1.4:** Validação com 1 Repositório (Prova de Conceito)
- **Descrição:** Executar o pipeline completo (clone + CK + agregação) em 1 repositório da lista
- **Entrada:** URL de 1 repositório (ex.: `junit-team/junit4`)
- **Saída:**
  - `data/sample_metrics.csv` com métricas agregadas
  - Log opcional de execução local (não obrigatório para versionamento)
- **Validação:**
  - Arquivo CSV possui todas as colunas esperadas (CBO, DIT, LCOM, média, mediana, desvio)
  - Valores são numéricos e plausíveis
  - Execução completa sem erros críticos
- **Observações:**
  - Documentar comando exato e parâmetros usados
  - Capturar tempo de execução (benchmark)

#### **Tarefa 1.5:** Documentação de Sprint 1
- **Descrição:** Elaborar relatório técnico do Sprint 1
- **Saída:**
  - `Lab-02S01/docs/RELATORIO-S01.md`
  - Seções: (i) objetivo, (ii) metodologia, (iii) scripts criados, (iv) CSV de 1 repositório, (v) desafios encontrados
- **Conteúdo:**
  - Listagem dos 1.000 repositórios (sumário em tabela)
  - Descrição dos scripts criados (input/output)
  - Exemplo de resultado (métricas do repositório sample)
  - Próximos passos (S02)

### 5.2 Arquivo da Estrutura S01

```
Lab-02S01/
├── README.md                  (overview e quick start)
├── docs/
│   └── RELATORIO-S01.md      (relatório técnico – entrega)
├── fetch_repos.py            (script principal de coleta GitHub)
├── collect_sample_metrics.py (clone + CK + agregação de métricas)
├── query.graphql             (consulta GraphQL versionada)
├── requirements.txt          (dependências Python)
├── .env.example              (template para GITHUB_TOKEN)
├── data/
│   ├── repos_1000.json       (lista bruta do GitHub)
│   ├── repos_1000.csv        (lista formatada)
│   └── sample_metrics.csv    (métricas de 1 repo – prova de conceito)
└── scripts/
  └── run_s01_pipeline.ps1  (orquestrador da Sprint 1)
```

### 5.3 Critério de Aceição (S01)

- ✓ Lista de 1.000 repositórios Java disponível em JSON e CSV
- ✓ Ferramenta CK instalada e testada
- ✓ Script de automação (clone + CK + agregação) implementado
- ✓ 1 repositório processado com sucesso; CSV de métricas gerado
- ✓ Relatório técnico elaborado com documentação clara

---

## 6. Sprint 2 – Lab-02S02: Coleta em Massa e Hipóteses

**Duração:** ~2 semanas  
**Pontos:** 5 pontos  
**Objetivo:** Processar os 1.000 repositórios e formular hipóteses para análise

### 6.1 Tarefas Sequenciais

#### **Tarefa 2.1:** Paralelo: Processamento dos 1.000 Repositórios
- **Descrição:** Executar script de coleta em batch para todos os 1.000 repositórios
- **Entrada:**
  - `data/repos_1000.csv` (de S01)
  - Script `collect_metrics_batch.py`
- **Saída:**
  - `data/metrics_all_1000_repos.csv` – Consolidação de todas as métricas
    - Colunas: `repository`, `url`, `stars`, `created_at`, `releases`, `loc`, `comment_lines`, `cbo_mean`, `cbo_median`, `cbo_std`, `dit_mean`, `dit_median`, `dit_std`, `lcom_mean`, `lcom_median`, `lcom_std`
- **Tecnologia:** Python + multiprocessing (paralelização)
- **Observações:**
  - Implementar **checkpoint resumption** (caso um repositório falhe, não reiniciar do 0)
  - Respeitar rate-limits da API GitHub
  - Monitorar consumo de disco (repositórios temporários)
  - Relatório de sucesso/falha por repositório
  - Medição de tamanho via `cloc` por repositório (LOC e linhas de comentários)
- **Tempo estimado:** 3–7 dias (dependendo de recursos)

#### **Tarefa 2.2:** Validação e Limpeza de Dados
- **Descrição:** Remover repositórios com dados incompletos ou inválidos
- **Entrada:** `data/metrics_all_1000_repos.csv` (bruto)
- **Saída:** `data/metrics_all_1000_repos_cleaned.csv`
- **Critérios de Limpeza:**
  - Remover linhas com valores nulos em métricas essenciais
  - Validar ranges (CBO > 0, DIT ≥ 0, LCOM ≥ 0)
  - Remover duplicatas
- **Tecnologia:** Python (`pandas`)
- **Observações:**
  - Documentar número de registros removidos
  - Justificar decisões de limpeza

#### **Tarefa 2.3:** Análise Exploratória Inicial
- **Descrição:** Calcular estatísticas descritivas globais
- **Saída:**
  - `data/summary_statistics.txt`
  - Seções:
    - Tamanho da amostra validada (N)
    - Média, mediana, desvio padrão para cada métrica (CBO, DIT, LCOM)
    - Distribuição: min, Q1, Q3, max
    - Correlação preliminar (Pearson) entre métricas de processo e qualidade
- **Tecnologia:** Python (`pandas`, `scipy.stats`)

#### **Tarefa 2.4:** Formular Hipóteses Informais
- **Descrição:** Elaborar hipóteses **a priori** para cada RQ
- **Saída:** `HIPOTESES-S02.md`
- **Estrutura por RQ:**
  ```markdown
  ## RQ 01: Popularidade vs. Qualidade
  
  **Hipótese H1a:** Repositórios com maior número de estrelas tendem a ter 
  **menor CBO** (acoplamento reduzido) devido a práticas rigorosas de code review.
  
  **Hipótese H1b:** Idade pode ser fator confundidor; repositórios antigos 
  podem acumular débito técnico.
  
  **Justificativa:** [baseada em leitura de artigos, senso comum, etc.]
  ```
- **Observações:**
  - Mínimo 2 hipóteses por RQ (total: 8+)
  - Baseadas em literatura e análise exploratória prévia

#### **Tarefa 2.5:** Documentação de Sprint 2
- **Descrição:** Elaborar relatório técnico do Sprint 2
- **Saída:**
  - `Lab-02S02/RELATORIO-S02.md`
  - Seções:
    - (i) Processo de coleta em massa (tempo, desafios)
    - (ii) Estatísticas de sucesso/falha
    - (iii) Sumário das métricas coletadas
    - (iv) Hipóteses informais (RQ 01–04)
    - (v) Análise exploratória preliminar
    - (vi) Próximos passos (S03)

### 6.2 Arquivo da Estrutura S02

```
Lab-02S02/
├── README.md                               (overview)
├── RELATORIO-S02.md                       (relatório técnico – entrega)
├── HIPOTESES-S02.md                       (hipóteses informais por RQ)
├── collect_metrics_batch.py               (coleta paralela)
├── validate_data.py                       (limpeza de dados)
├── data/
│   ├── metrics_all_1000_repos.csv         (todas as métricas – bruto)
│   ├── metrics_all_1000_repos_cleaned.csv (validado)
│   ├── summary_statistics.txt             (estatísticas descritivas)
│   ├── correlation_matrix.csv             (correlações preliminares)
│   └── collection_log.txt                 (relatório de sucesso/falha)
└── logs/
    └── execution_s02.log
```

### 6.3 Critério de Aceição (S02)

- ✓ Coleta paralela de 1.000 repositórios concluída (com logs de sucesso/falha)
- ✓ CSV consolidado e validado disponível
- ✓ Estatísticas descritivas calculadas
- ✓ Mínimo 8 hipóteses informais elaboradas (2 por RQ)
- ✓ Relatório técnico elaborado
- ✓ Dados prontos para análise de correlação (S03)

---

## 7. Sprint 3 – Lab-02S03: Análise Final e Relatório Executivo

**Duração:** ~3 semanas  
**Pontos:** 10 pontos (valor maior)  
**Objetivo:** Responder às 4 RQs através de análise estatística, gráficos e relatório final

### 7.1 Tarefas Sequenciais

#### **Tarefa 3.1:** Análise de Correlação por RQ
- **Descrição:** Para cada RQ, calcular correlação entre métrica de processo e métricas de qualidade
- **Entrada:** `data/metrics_all_1000_repos_cleaned.csv`
- **Saída:**
  - `RQ01_correlacao_popularidade.csv` – Correlação entre `stars` e `(cbo, dit, lcom)`
  - `RQ02_correlacao_maturidade.csv` – Correlação entre `age_years` e `(cbo, dit, lcom)`
  - `RQ03_correlacao_atividade.csv` – Correlação entre `releases` e `(cbo, dit, lcom)`
  - `RQ04_correlacao_tamanho.csv` – Correlação entre `loc, comments` e `(cbo, dit, lcom)`
- **Estatísticas:**
  - **Coeficiente de Pearson** (correlação linear)
  - **Coeficiente de Spearman** (correlação monotônica)
  - **p-value** (significância estatística)
  - **Intervalo de confiança 95%**
- **Tecnologia:** Python (`scipy.stats`, `pandas`)
- **Observações:**
  - Documentar premissas (normalidade, etc.)
  - Considerar transformações (log) se distribuição for enviesada

#### **Tarefa 3.2:** Geração de Gráficos de Correlação (Bônus +1)
- **Descrição:** Visualizar correlações para facilitar interpretação
- **Saída:** `figs/` com gráficos para cada RQ
  ```
  figs/
  ├── RQ01_scatter_stars_vs_cbo.png
  ├── RQ01_scatter_stars_vs_dit.png
  ├── RQ01_scatter_stars_vs_lcom.png
  ├── RQ02_scatter_age_vs_cbo.png
  ├── RQ02_scatter_age_vs_dit.png
  ├── RQ02_scatter_age_vs_lcom.png
  ├── RQ03_scatter_releases_vs_cbo.png
  ├── RQ03_scatter_releases_vs_dit.png
  ├── RQ03_scatter_releases_vs_lcom.png
  ├── RQ04_scatter_loc_vs_cbo.png
  ├── RQ04_scatter_loc_vs_dit.png
  ├── RQ04_scatter_loc_vs_lcom.png
  ├── correlation_heatmap.png        (matriz de correlação geral)
  └── distribution_boxplots.png      (distribuição das métricas)
  ```
- **Tipos de Gráficos:**
  - Scatter plots (com linhas de tendência)
  - Heatmap de correlação
  - Box plots (distribuição por quartis)
- **Tecnologia:** Python (`matplotlib`, `seaborn`)

#### **Tarefa 3.3:** Interpretação de Resultados
- **Descrição:** Comparar resultados observados com hipóteses (S02)
- **Saída:**
  - `INTERPRETACAO-RESULTADOS.md`
  - Seções por RQ:
    ```markdown
    ## RQ 01: Popularidade vs. Qualidade
    
    **Correlação Observada:**
    - Pearson(stars, CBO) = 0.XX (p < 0.05)
    - Interpretação: [aceita/rejeita H1a e H1b]
    - Surpresas: [o que diferiu das hipóteses?]
    
    **Discussão:**
    - Que fatores podem explicar esse padrão?
    - Como alinha com teoria de qualidade de software?
    ```
- **Pontos a Cobrir:**
  - Significância estatística (p-value)
  - Força da correlação (fraca/moderada/forte)
  - Possíveis explicações e confundidores
  - Limitações do estudo

#### **Tarefa 3.4:** Validação Estatística (Bônus considerado)
- **Descrição:** Realizar testes de significância apropriados
- **Saída:** `VALIDACAO-ESTATISTICA.md`
- **Testes:**
  - **Teste de Normalidade (Shapiro-Wilk):**
    - Aplicar em cada métrica para verificar adequação de Pearson vs. Spearman
  - **Teste de Correlação (Spearman):**
    - Confirmação de padrões via método não-paramétrico
  - **Teste de Tendência Linear:**
    - Regressão linear simples para cada RQ
- **Interpretação:**
  - p-value < 0.05: correlação significante
  - p-value ≥ 0.05: sem evidência de correlação
- **Tecnologia:** Python (`scipy.stats`)

#### **Tarefa 3.5:** Elaboração do Relatório Final
- **Descrição:** Documento ejecutivo completo respondendo às 4 RQs
- **Saída:** `Lab-02S03/RELATORIO-FINAL.md` (ou `.pdf`)
- **Estrutura:**
  1. **Introdução**
     - Contexto (qualidade de software, code smells, open-source)
     - Hipóteses informais (~500 palavras)
  2. **Metodologia**
     - Seleção de repositórios (top-1.000 Java)
     - Coleta de dados (APIs, CK, período temporal)
     - Análise estatística (Pearson, Spearman, p-values)
  3. **Resultados**
     - RQ 01–04, cada um com:
       - Tabela de correlações
       - Gráfico scatter plot
       - Valor de p-value e interpretação
  4. **Discussão**
     - Comparação com hipóteses
     - Implicações práticas
     - Limitações (viés de seleção, confundidores, etc.)
     - Oportunidades de pesquisa futura
  5. **Conclusão**
     - Síntese das respostas às RQs
  6. **Referências**
     - Artigos (GQM, CK metrics, empirical SE)
     - Documentação (GitHub API, CK ferramenta)
- **Recomendações de Conteúdo:**
  - Mínimo 3.000–4.000 palavras
  - Gráficos embutidos (figs/)
  - Tabelas com resultados quantitativos
  - Tomadas de decisão justificadas

#### **Tarefa 3.6:** Preparação para Apresentação
- **Descrição:** Criar slides para apresentação em aula
- **Saída:**
  - `Lab-02S03/APRESENTACAO-Lab02.pptx` (ou `.pdf`)
  - Slides:
    1. Capa (título, grupo, data)
    2. Motivação e RQs (problema)
    3. Metodologia (dados, métricas, análise)
    4. Resultados por RQ (gráficos principales)
    5. Discussão (hipóteses vs. realidade)
    6. Conclusões (resposta às RQs)
    7. Referências
- **Tempo de apresentação:** ~15 minutos (conforme cronograma)

### 7.2 Arquivo da Estrutura S03

```
Lab-02S03/
├── README.md                         (overview)
├── RELATORIO-FINAL.md               (entrega principal – análise completa)
├── INTERPRETACAO-RESULTADOS.md      (interpretação por RQ)
├── VALIDACAO-ESTATISTICA.md         (testes estatísticos)
├── APRESENTACAO-Lab02.pptx          (slides – entrega secundária)
├── analyze_correlations.py          (script de análise – RQ 01–04)
├── generate_plots.py                (script de visualização)
├── validate_statistics.py           (testes estatísticos)
├── data/
│   ├── RQ01_correlacao_popularidade.csv
│   ├── RQ02_correlacao_maturidade.csv
│   ├── RQ03_correlacao_atividade.csv
│   ├── RQ04_correlacao_tamanho.csv
│   └── statistical_summary.txt      (todos os p-values, r-values)
├── figs/                            (gráficos para relatório)
│   ├── RQ01_scatter_stars_vs_cbo.png
│   ├── RQ02_scatter_age_vs_dit.png
│   ├── RQ03_scatter_releases_vs_lcom.png
│   ├── RQ04_scatter_loc_vs_cbo.png
│   ├── correlation_heatmap.png
│   └── distribution_boxplots.png
└── logs/
    └── execution_s03.log
```

### 7.3 Critério de Aceição (S03)

- ✓ Análise de correlação para todas as 4 RQs concluída
- ✓ Gráficos de scatter plot (mínimo 3) com linhas de tendência
- ✓ Testes estatísticos (Pearson, Spearman, p-values) aplicados
- ✓ Relatório final estruturado (min. 3.000 palavras, gráficos embutidos)
- ✓ Hipóteses iniciais comparadas com resultados (aceitas/rejeitadas)
- ✓ Discussão e limitações documentadas
- ✓ Slides de apresentação preparados
- ✓ **(BÔNUS)** +1 ponto se gráficos de correlação e testes estatísticos inclusos

### 7.4 Distribuição de Pontos

| Entrega | Pontos |
|---------|--------|
| Relatório Final (RQ 01–04 respondidas) | 8 |
| Análise Exploratória + Gráficos | 1 |
| Apresentação em aula | 1 |
| **BÔNUS:** Gráficos + Testes Estatísticos | +1 |
| **Total** | **10 (+ 1 bônus)** |

---

## 8. Dependências Entre Sprints

```
Sprint 1 (S01)
│
├─> Lista 1.000 repos (JSON/CSV)
├─> Ferramenta CK instalada e testada
├─> Script de automação criado
└─> Prova de conceito (1 repositório)
       │
       ▼
Sprint 2 (S02)
│
├─> Processamento paralelo dos 1.000 repos
├─> CSV consolidado (métricas_all)
├─> Validação de dados
└─> Hipóteses informais (8+)
       │
       ▼
Sprint 3 (S03)
│
├─> Análise de correlação (4 RQs)
├─> Gráficos de visualização
├─> Testes estatísticos
├─> Relatório Final (3.000+ palavras)
└─> Apresentação em aula (15 min)
```

---

## 9. Recursos e Ferramentas Necessárias

### 9.1 Desenvolvimento

| Ferramenta | Versão | Propósito |
|-----------|--------|----------|
| **Python** | ≥ 3.9 | Scripts de coleta e análise |
| **CK** | Latest | Análise estática de métricas Java |
| **Git** | Latest | Clone de repositórios |
| **JDK** | ≥ 11 | Dependência do CK |
| **pandas** | Latest | Manipulação de dados (CSV) |
| **scipy** | Latest | Análise estatística |
| **matplotlib/seaborn** | Latest | Visualização de gráficos |

### 9.2 Infraestrutura

- **Espaço em disco:** Mínimo 500 GB (armazenar ~1.000 repositórios temporariamente)
- **Memória RAM:** Recomendado ≥ 16 GB (paralelização)
- **Conexão de rede:** Estável (coleta de API pode levar dias)
- **Sistema Operacional:** Linux/macOS/Windows (com WSL)

### 9.3 Credenciais e Configuração

```bash
# .env
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
CK_PATH=/path/to/ck/
TEMP_DIR=/path/to/repos_temp/
OUTPUT_DIR=./data/
```

---

## 10. Critérios de Qualidade e Entrega

### 10.1 Por Sprint

| Sprint | Critério | Peso |
|--------|----------|------|
| **S01** | Lista + Script + 1 CSV | 5% |
| **S02** | CSV 1.000 + Hipóteses + Análise Exploratória | 5% |
| **S03** | Relatório Final + Gráficos + Apresentação | 10% |

### 10.2 Qualidade Geral

- ✓ Código comentado (docstrings, explicações inline)
- ✓ README.md em cada subpasta com instruções de execução
- ✓ Logs detalhados de execução (tempo, erros, sucessos)
- ✓ Tratamento de exceções (rede, disco, permissões)
- ✓ Dados validados e limpos (sem valores faltantes críticos)
- ✓ Gráficos legíveis (legendas, eixos nomeados, cores contrastantes)
- ✓ Relatório estruturado (seções claras, referências citadas)

---

## 11. Riscos e Mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| **Taxa de falha na coleta** | Alto (inviabiliza S02) | Implementar checkpoints e retentativas; monitorar logs |
| **Falta de espaço em disco** | Alto | Limpeza automática de repos clonados; usar storage externo |
| **Rate-limiting da API GitHub** | Médio | Usar GraphQL (mais eficiente); spreader requisições |
| **Correlação espúria** | Médio | Aplicar testes estatísticos rigorosos; documentar confundidores |
| **Atraso em análise estatística** | Baixo | Iniciar S03 assim que S02 validado; usar parallelização |

---

## 12. Referências Bibliográficas Recomendadas

- **GQM Approach:** Basili et al. (fichamento 01)
- **GitHub API:** Documentação GitHub GraphQL (fichamento 02)
- **CK Metrics:** Lanza & Marinescu (fichamento 03 – Empirical CK metrics)
- **Evidence-based SE:** Kitchenham et al. (fichamento 04)
- **Code Smells:** Fowler & Beck (fichamentos 09–11)
- **Empirical Studies:** Kitchenham et al. (fichamento 15)

---

## 13. Checklist Final (Pré-Entrega)

### S01
- [ ] Lista de 1.000 repositórios exportada (JSON + CSV)
- [ ] CK instalado e testado (versão verificada)
- [ ] Script de coleta implementado e funcionando
- [ ] 1 repositório processado com sucesso
- [ ] CSV de métricas exibindo valores válidos
- [ ] Documentação (README + docs/RELATORIO-S01.md) completa

### S02
- [ ] Processamento paralelo dos 1.000 repositórios concluído
- [ ] CSV consolidado validado (sem linhas nulas)
- [ ] Estatísticas descritivas calculadas (média, mediana, desvio)
- [ ] Hipóteses informais elaboradas (mínimo 8)
- [ ] Logs de sucesso/falha disponíveis
- [ ] Documentação (README + RELATORIO-S02.md + HIPOTESES-S02.md) completa

### S03
- [ ] Análise de correlação (Pearson + Spearman) para 4 RQs realizada
- [ ] Gráficos scatter plot gerados (mínimo 3)
- [ ] Testes estatísticos realizados (p-values, intervalos de confiança)
- [ ] Relatório Final estruturado (introdução, metodologia, resultados, discussão, conclusão)
- [ ] Hipóteses comparadas com resultados (interpretação)
- [ ] Slides de apresentação preparados
- [ ] Documentação (README + RELATORIO-FINAL.md) completa
- [ ] **(BÔNUS)** Gráficos de correlação + testes estatísticos inclusos (+1 ponto)

---

## 14. Cronograma Proposto

(Consulte também: https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/tree/main/CRONOGRAMA_)

| Período | Atividade | Sprint |
|---------|-----------|--------|
| Semana 1–2 | Preparação (CK, API GitHub), Script piloto | **S01** |
| Semana 3–4 | Coleta paralela 1.000 repos, validação, hipóteses | **S02** |
| Semana 5–6 | Análise correlação, gráficos, testes estatísticos | **S03 (início)** |
| Semana 7 | Relatório final, slides, revisão | **S03 (fim)** |
| Data da Entrega | Apresentação oral em aula | — |

---

## 15. Contato e Suporte

- **Professor:** João Paulo Carneiro Aramuni
- **Material de Apoio:** `Artigos/Fichamentos/`
- **Cronograma Oficial:** GitHub ([link acima](#14-cronograma-proposto))

---

**Documento Revisado:** 23 de março de 2026  
**Status:** Pronto para Execução
