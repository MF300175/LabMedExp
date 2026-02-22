# Lab 01 – Características de repositórios populares

**Sprint 1** da disciplina Laboratório de Experimentação de Software.

## Objetivo

Coletar dados dos **1.000 repositórios** com maior número de estrelas no GitHub e analisar características (idade, PRs, releases, issues, linguagem, etc.) com base em questões de pesquisa (RQs) e métricas definidas.

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `README.md` | Este arquivo |
| [docs/LABORATÓRIO 01 - Características de repositórios populares.pdf](docs/LABORATÓRIO%2001%20-%20Características%20de%20repositórios%20populares.pdf) | Enunciado oficial |
| [docs/PLANO-IMPLEMENTACAO-Lab01.md](docs/PLANO-IMPLEMENTACAO-Lab01.md) | Plano de implementação por etapa (S01, S02, S03) |
| [docs/QUERY-GRAPHQL-Lab01.md](docs/QUERY-GRAPHQL-Lab01.md) | Query GraphQL detalhada e mapeamento para as RQs |
| `.env.example` | Modelo para variável `GITHUB_TOKEN` (copiar para `.env` local; não versionar `.env`) |
| `data/` | Saídas locais de coleta (ex.: JSON do S01, CSV do S02); não versionar |
| `figs/` | Gráficos para o relatório (S03) |
| `relatorio/` | Relatório v1 (S02) e relatório final (S03) |

Relatório detalhado do S1 (funcionalidades e comandos):

- [relatorio/RELATORIO-S01-Funcionalidades-e-Execucao.md](relatorio/RELATORIO-S01-Funcionalidades-e-Execucao.md)

A criar nas etapas: `repos_1000.csv`, `analyze.py` (ou notebook) e os PDFs dos relatórios. Detalhes em **PLANO-IMPLEMENTACAO-Lab01.md** (seção 4).

## Material de apoio

- `Artigos/Fichamentos/` — fichamentos (GQM, GitHub API, métricas, etc.).
- Token do GitHub em variável de ambiente (ex.: `GITHUB_TOKEN`); não versionar.

## Testes

## Execução (Lab01S01)

O script `fetch_repos.py` configurado para ser mais estável em redes instáveis:

- `LAB01_PAGE_SIZE=10` (padrão)
- `LAB01_MAX_RETRIES=8` (padrão)

Sobrescrever esses valores via variáveis de ambiente se quiser.

Flags úteis (opcionais):

- `LAB01_DEBUG=1` (logs de debug da requisição)
- `LAB01_SHOW_SAMPLE=1` (imprime uma amostra do primeiro repositório)

### Testes unitários (offline, sem chamar a API)

Roda apenas testes com `mock`, validando parsing de `.env`, leitura da query e tratamento de respostas HTTP/JSON.

- `python -m unittest -v test_fetch_repos_unit.py`

### Testes reais (integração com GitHub GraphQL)

Os testes em `test_integration_github_graphql.py` **só rodam** se `GITHUB_TOKEN` estiver definido (caso contrário ficam como *skipped*).

- Defina o token (exemplo só para a sessão atual do PowerShell):
  - `$env:GITHUB_TOKEN = "<seu_token>"`
- Rode:
  - `python -m unittest -v test_integration_github_graphql.py`

Opcional (mais pesado): smoke test com a query do lab (primeira página, 100 repos):

- `$env:RUN_SLOW_INTEGRATION = "1"`
- `python -m unittest -v test_integration_github_graphql.py`
