# Query GraphQL – Lab 01: Características de repositórios populares

Este documento detalha a **query GraphQL** da API do GitHub necessária para coletar os dados das RQs do Laboratório 01. O consumo deve ser feito por **script próprio** (ex.: Python com `requests`), **sem** bibliotecas de terceiros que realizem consultas à API do GitHub.

---

## 1. Endpoint e autenticação

| Item | Valor |
|------|--------|
| **URL** | `https://api.github.com/graphql` |
| **Método** | `POST` |
| **Header** | `Authorization: Bearer <SEU_TOKEN>` |
| **Header** | `Content-Type: application/json` |
| **Corpo** | `{ "query": "<sua query em string>" }` |

O token é um **Personal Access Token** (classic ou fine-grained) com permissão de leitura para repositórios públicos. Criação: GitHub → Settings → Developer settings → Personal access tokens.

---

## 2. Mapeamento RQ → campos da API

| RQ | Métrica | Campo GraphQL no tipo `Repository` |
|----|---------|-------------------------------------|
| RQ01 | Idade do repositório | `createdAt` (depois: idade = hoje − createdAt) |
| RQ02 | Total de PRs aceitas | `pullRequests(states: MERGED) { totalCount }` |
| RQ03 | Total de releases | `releases(first: 1) { totalCount }` |
| RQ04 | Tempo até última atualização | `pushedAt` (depois: dias desde pushedAt) |
| RQ05 | Linguagem primária | `primaryLanguage { name }` |
| RQ06 | Razão issues fechadas / total | `issues(first: 1) { totalCount }` e `issues(first: 1, states: [CLOSED]) { totalCount }` (usar alias) |
| — | Ordenação "maior nº de estrelas" | `stargazerCount` (ordenar no script e tomar os 1.000 maiores) |

**Observação:** Em conexões (connections) do GraphQL do GitHub é obrigatório informar `first` ou `last`. Usar `first: 1` só para obter `totalCount` reduz o volume de dados.

---

## 3. Busca: repositórios por estrelas

A raiz da consulta é o campo **`search`**:

- **`query`**: string de busca no mesmo formato da busca no site (ex.: `stars:>1` para repos com ao menos 1 estrela).
- **`type`**: `REPOSITORY`.
- **`first`**: quantidade por página (máx. 100).
- **`after`**: cursor para paginação (valor de `pageInfo.endCursor` da página anterior).

Para obter os **1.000 repositórios com mais estrelas**, use uma string que priorize estrelas. A busca padrão pode ordenar por relevância; para maior alinhamento com “top por estrelas”, use um limite alto de estrelas (ex.: `stars:>100`) e pagine até 1.000, ou use `stars:>1` e até 10 páginas de 100, aceitando que a ordem pode não ser estritamente por estrelas. Alternativa: consultar a REST `GET /search/repositories?q=stars:>1&sort=stars&order=desc&per_page=100` e depois, para cada repo, usar GraphQL para os detalhes (o enunciado exige uso da GraphQL; a busca em si pode ser adaptada conforme documentação atual).

**Reavaliação (enunciado: "1.000 com maior número de estrelas"):** A busca GraphQL não ordena por estrelas. Incluir **`stargazerCount`** na query; buscar várias páginas (ex.: 15–20); no script **ordenar por stargazerCount decrescente** e tomar os **primeiros 1.000**.

---

## 4. Query GraphQL completa (uma página – 100 repositórios)

Query para **uma página** de 100 repositórios. Para a primeira página não envie `after`; para as seguintes, use `after: "cursor_retornado"`.

```graphql
query TopRepos($cursor: String) {
  search(
    query: "stars:>1"
    type: REPOSITORY
    first: 100
    after: $cursor
  ) {
    repositoryCount
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        name
        nameWithOwner
        url
        createdAt
        pushedAt
        primaryLanguage {
          name
        }
        pullRequests(first: 1, states: [MERGED]) {
          totalCount
        }
        releases(first: 1) {
          totalCount
        }
        issues(first: 1) {
          totalCount
        }
        issuesClosed: issues(first: 1, states: [CLOSED]) {
          totalCount
        }
      }
    }
  }
}
```

**Variáveis (primeira página):**

```json
{
  "cursor": null
}
```

**Variáveis (próximas páginas):** use o valor de `pageInfo.endCursor` da resposta anterior em `"cursor": "Y3Vyc29yOnYyO..."`.

---

## 5. Uso de alias para `issues`

O tipo `Repository` tem um único campo `issues`, com argumentos opcionais. Para obter **total de issues** e **total de issues fechadas** na mesma consulta, é necessário usar **alias** em uma das chamadas:

- `issues(first: 1) { totalCount }` → total de issues (todas).
- `issuesClosed: issues(first: 1, states: [CLOSED]) { totalCount }` → total de issues fechadas.

Na resposta JSON:

- `issues.totalCount` → RQ06 (denominador).
- `issuesClosed.totalCount` → RQ06 (numerador da razão).

**RQ06:** razão = `issuesClosed.totalCount / issues.totalCount` (tratar `issues.totalCount === 0` para não dividir por zero).

---

## 6. Estrutura da resposta (exemplo)

Trecho esperado por repositório dentro de `data.search.nodes[]`:

```json
{
  "name": "freeCodeCamp",
  "nameWithOwner": "freeCodeCamp/freeCodeCamp",
  "url": "https://github.com/freeCodeCamp/freeCodeCamp",
  "createdAt": "2014-12-24T17:49:19Z",
  "pushedAt": "2025-02-18T12:00:00Z",
  "primaryLanguage": { "name": "JavaScript" },
  "pullRequests": { "totalCount": 25000 },
  "releases": { "totalCount": 15 },
  "issues": { "totalCount": 10000 },
  "issuesClosed": { "totalCount": 9500 }
}
```

---

## 7. Paginação (1.000 repositórios)

1. Enviar a query com `first: 100` e `after: null` (ou omitir `after`).
2. Ler `data.search.pageInfo.hasNextPage` e `data.search.pageInfo.endCursor`.
3. Enquanto `hasNextPage === true` e ainda não tiver 1.000 repositórios:
   - Enviar nova requisição com `after: endCursor`.
   - Acumular `nodes` de cada página (filtrar apenas nós que são `Repository`).
4. Parar ao atingir 1.000 repositórios ou quando `hasNextPage === false`.

---

## 8. Rate limit e boas práticas

- **GraphQL:** 5.000 pontos por hora (contagem por nó/connection; a busca consome pontos).
- Incluir tratamento de HTTP 403 (rate limit) e cabeçalho `Retry-After` ou espera antes de nova tentativa.
- Não versionar o token: usar variável de ambiente (ex.: `GITHUB_TOKEN`).
- Manter intervalo entre requisições (ex.: 1–2 s) para reduzir risco de atingir o limite.

---

## 9. Mapeamento para o CSV (Lab01S02)

Sugestão de colunas a partir dos campos da query:

| Coluna no CSV | Origem na resposta |
|----------------|--------------------|
| `name` | `node.name` |
| `nameWithOwner` | `node.nameWithOwner` |
| `url` | `node.url` |
| `stargazerCount` | `node.stargazerCount` (para ordenar e selecionar top 1.000) |
| `createdAt` | `node.createdAt` (RQ01) |
| `pushedAt` | `node.pushedAt` (RQ04) |
| `primaryLanguage` | `node.primaryLanguage.name` ou vazio (RQ05) |
| `pullRequestsMerged` | `node.pullRequests.totalCount` (RQ02) |
| `releasesTotal` | `node.releases.totalCount` (RQ03) |
| `issuesTotal` | `node.issues.totalCount` (RQ06) |
| `issuesClosed` | `node.issuesClosed.totalCount` (RQ06) |

Colunas derivadas (calcular no script ou na análise): `age_days`, `days_since_last_push`, `issuesClosedRatio`.

---

## 10. Referências

- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [Search (query syntax)](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
- [Using pagination in the GraphQL API](https://docs.github.com/en/graphql/guides/using-pagination-in-the-graphql-api)
- [Rate limits (GraphQL)](https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits)
