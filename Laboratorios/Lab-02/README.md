# Lab-02 - Características de Qualidade de Sistemas Java

Espaço de trabalho do Lab-02 da disciplina Laboratório de Experimentação de Software.

## Estado Atual

- Sprint 1 (S01): concluída
- Sprint 2 (S02): executada com amostra válida de 972 repositórios
- Sprint 3 (S03): scripts de análise e gráficos implementados

## Estrutura da Pasta

- `enunciado_lab-2.md`: enunciado do laboratório
- `PLANO-IMPLEMENTACAO-Lab-02.md`: planejamento macro em sprints
- `Lab-02S01/`: implementação e artefatos da Sprint 1
- `Lab-02S02/`: implementação, análises e relatório da Sprint 2
- `Lab-02S03/`: scripts e figuras da Sprint 3

## Sprints e Funcionalidades

### Sprint 1 (S01)

Implementa a coleta dos top-1.000 repositórios Java e a prova de conceito com CK.

- `Lab-02S01/fetch_repos.py`: coleta GraphQL com paginação e retentativas
- `Lab-02S01/collect_sample_metrics.py`: clone + CK + sumarização CBO/DIT/LCOM
- `Lab-02S01/data/repos_1000.json` e `Lab-02S01/data/repos_1000.csv`: base dos repos
- `Lab-02S01/data/sample_metrics.csv`: métricas agregadas de 1 repositório
- `Lab-02S01/docs/RELATORIO-S01.md`: relatório técnico da sprint

### Sprint 2 (S02)

Consolida métricas para a amostra e executa validação e análise exploratória.

- `Lab-02S02/collect_metrics_batch.py`: coleta em lote (CK + cloc)
- `Lab-02S02/collect_metrics_retry_failed.py`: reprocessa repos faltantes
- `Lab-02S02/validate_data.py`: limpeza e validação do CSV consolidado
- `Lab-02S02/summarize_statistics.py`: estatísticas e correlação preliminar
- `Lab-02S02/RELATORIO-S02.md`: relatório técnico com achados e limitações
- `Lab-02S02/TUTORIAL-S02.md`: comandos e explicação das funções

### Sprint 3 (S03)

Automatiza a análise estatística e a geração de gráficos.

- `Lab-02S03/analyze_correlations.py`: Pearson e Spearman por RQ
- `Lab-02S03/generate_plots.py`: gráficos (scatter, heatmap, boxplots)
- `Lab-02S03/validate_statistics.py`: Shapiro-Wilk e Spearman
- `Lab-02S03/figs/`: figuras geradas

## Relacao com as Questoes de Pesquisa

As questões de pesquisa do enunciado (`enunciado_lab-2.md`) são respondidas pelas métricas
coletadas nas sprints:

- **RQ01 (popularidade vs qualidade):** `stargazers` vs `cbo_mean`, `dit_mean`, `lcom_mean`
- **RQ02 (maturidade vs qualidade):** `age_years` vs `cbo_mean`, `dit_mean`, `lcom_mean`
- **RQ03 (atividade vs qualidade):** `releases_count` vs `cbo_mean`, `dit_mean`, `lcom_mean`
- **RQ04 (tamanho vs qualidade):** `loc` e `comment_lines` vs `cbo_mean`, `dit_mean`, `lcom_mean`

Essas relações são analisadas em `Lab-02S02` e aprofundadas em `Lab-02S03`.

## Observação de Organização

Arquivos auxiliares de execução local (cache, temporários e saídas intermediárias) foram
higienizados para manter apenas os artefatos relevantes da entrega.
