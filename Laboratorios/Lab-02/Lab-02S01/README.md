# Lab-02S01

Sprint 1 do Lab-02: coleta dos top-1000 repositórios Java e prova de conceito com CK em 1 repositório.

## Estrutura Organizada

- `fetch_repos.py`: coleta paginada no GitHub GraphQL
- `collect_sample_metrics.py`: clone + execução CK + agregação das métricas
- `query.graphql`: query base para busca de repositórios Java
- `scripts/run_s01_pipeline.ps1`: automação ponta a ponta da S01
- `docs/RELATORIO-S01.md`: relatório consolidado da sprint
- `data/repos_1000.json`: base coletada em JSON
- `data/repos_1000.csv`: base coletada em CSV
- `data/sample_metrics.csv`: métricas de amostra (CBO, DIT, LCOM)
- `.env.example`: modelo de variáveis de ambiente

## Entregáveis desta etapa

- `data/repos_1000.json`: lista bruta dos 1000 repositórios Java populares
- `data/repos_1000.csv`: lista tabular para pipeline das próximas sprints
- `data/sample_metrics.csv`: métricas agregadas de 1 repositório (CBO, DIT, LCOM)
- `docs/RELATORIO-S01.md`: relatório técnico da execução

## Arquivos

- `fetch_repos.py`: coleta paginada no GitHub GraphQL
- `query.graphql`: query base para busca de repositórios Java
- `collect_sample_metrics.py`: clone + execução CK + agregação das métricas
- `.env.example`: exemplo de configuração
- `requirements.txt`: dependência Python (`requests`)

## Higienização aplicada

- Removidos diretórios auxiliares: `__pycache__/`, `temp/`, `data/ck_output/`.
- Mantidos apenas artefatos que evidenciam os entregáveis da Sprint 1.

## Pré-requisitos

- Python 3.9+
- Git
- Java (para rodar o CK)
- CK jar local (informado em `CK_JAR_PATH`)

## Configuração

1. Instale dependências:

```powershell
cd Laboratorios/Lab-02/Lab-02S01
python -m pip install -r requirements.txt
```

2. Crie um arquivo `.env` em `Lab-02S01/` com as variáveis abaixo:

```dotenv
GITHUB_TOKEN=seu_token_github
CK_JAR_PATH=C:\tools\ck\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar
LAB02_TARGET_REPOS=1000
LAB02_PAGE_SIZE=20
LAB02_TIMEOUT_SECS=90
LAB02_MAX_RETRIES=20
```

## Execução

### Execução automática (recomendado)

```powershell
cd Laboratorios/Lab-02/Lab-02S01
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_s01_pipeline.ps1
```

Flags úteis:

```powershell
# Pula a coleta dos 1000 (usa CSV já existente)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_s01_pipeline.ps1 -SkipFetch

# Pula a etapa CK (somente coleta + validação dos 1000)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_s01_pipeline.ps1 -SkipCK
```

### 1) Coleta top-1000 repositórios Java

```powershell
cd Laboratorios/Lab-02/Lab-02S01
python fetch_repos.py
```

Saídas esperadas:

- `data/repos_1000.json`
- `data/repos_1000.csv`

### 2) Prova de conceito CK em 1 repositório

```powershell
cd Laboratorios/Lab-02/Lab-02S01
python collect_sample_metrics.py
```

Saída esperada:

- `data/sample_metrics.csv`

## Observações

- O script de amostra usa a primeira linha de `repos_1000.csv`.
- O clone local é removido ao final para economizar disco.
- Se o CK mudar o nome/estrutura dos CSVs, ajuste o parse em `collect_sample_metrics.py`.
- Logs de execução são gerados localmente quando necessário e não são parte obrigatória da entrega versionada.
- O `sample_metrics.csv` é apenas uma prova de conceito; amostras muito pequenas (ex.: poucas classes) não são representativas para análise de qualidade.
- O pipeline automático (`run_s01_pipeline.ps1`) é voltado para ambiente Windows/PowerShell.
