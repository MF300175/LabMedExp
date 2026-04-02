# Lab-02S03

Sprint 3 do Lab-02: analise estatistica, graficos e relatorio final.

## Entradas

- `../Lab-02S02/data/metrics_all_1000_repos_cleaned.csv`

## Saidas esperadas

- `data/RQ01_correlacao_popularidade.csv`
- `data/RQ02_correlacao_maturidade.csv`
- `data/RQ03_correlacao_atividade.csv`
- `data/RQ04_correlacao_tamanho.csv`
- `data/statistical_summary.txt`
- `data/VALIDACAO-ESTATISTICA.txt`
- `figs/` com graficos (scatter, heatmap, boxplots)

## Scripts

- `analyze_correlations.py`: correlacoes Pearson/Spearman + p-values
- `generate_plots.py`: graficos de correlacao e distribuicao
- `validate_statistics.py`: testes adicionais (normalidade + validacao)

## Execucao

```bash
cd Laboratorios/Lab-02/Lab-02S03
python ./analyze_correlations.py
python ./generate_plots.py
python ./validate_statistics.py
```
