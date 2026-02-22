# Plano de Implementação – Laboratório 01: Características de repositórios populares

**Disciplina:** Laboratório de Experimentação de Software  
**Objetivo do lab:** Coletar dados dos **1.000 repositórios com maior número de estrelas** no GitHub e discutir as características com base em questões de pesquisa (RQs) e métricas definidas. A busca GraphQL não ordena por estrelas; incluir `stargazerCount` na query e **ordenar no script** por estrelas (decrescente), tomando os primeiros 1.000 após juntar várias páginas.

**Restrição:** Não é permitido usar bibliotecas de terceiros que realizem consultas à API do GitHub. É necessário escrever a **query GraphQL** e consumi-la por **script próprio** (ex.: `requests` em Python apenas para HTTP, sem wrapper da API).

---

## 1. Visão geral das entregas

| Etapa | Pontos | Entregas |
|-------|--------|----------|
| **Lab01S01** | 3 | Query GraphQL para 100 repos + requisição automática (todos os dados para as RQs) |
| **Lab01S02** | 3 | Paginação (1000 repos) + dados em .csv + primeira versão do relatório (hipóteses informais) |
| **Lab01S03** | 9 | Análise e visualização dos dados + relatório final |
| **Bônus** | +1 | RQ07: análise por linguagem (contribuição, releases, atualização) |

**Total:** 15 pontos (+1 bônus). Desconto de 1,0 ponto por dia de atraso.

---

## 2. Métricas por questão de pesquisa

| RQ | Questão | Métrica (dado a coletar) | Cálculo/uso |
|----|---------|---------------------------|--------------|
| **RQ01** | Sistemas populares são maduros/antigos? | Data de criação do repositório | Idade = (hoje − data criação) em anos/meses |
| **RQ02** | Muita contribuição externa? | Total de pull requests **aceitas** (merged) | Contagem total por repo |
| **RQ03** | Lançam releases com frequência? | Total de releases | Contagem total por repo |
| **RQ04** | Atualizados com frequência? | Data da última atualização (push/commit) | Tempo até última atualização (ex.: dias desde último push) |
| **RQ05** | Escritos nas linguagens mais populares? | Linguagem primária | Campo `primaryLanguage` (ou equivalente) por repo |
| **RQ06** | Alto percentual de issues fechadas? | Issues fechadas e total de issues | Razão = (issues fechadas) / (total de issues) |
| **RQ07** (bônus) | Por linguagem: mais contribuição, releases e atualização? | Mesmos de RQ02, RQ03, RQ04 | Agrupar por linguagem; comparar medianas/contagens |

---

## 3. Plano por etapa

### 3.1 Lab01S01 – Consulta GraphQL (100 repositórios) + requisição automática (3 pts)

**Objetivo:** Obter uma query GraphQL que retorne, para cada repositório, todos os campos necessários para responder às RQs, e um script que execute a requisição automaticamente.

**Passos sugeridos:**

1. **Criar conta/token no GitHub** (se ainda não tiver)
   - Acessar GitHub → Settings → Developer settings → Personal access tokens.
   - Gerar token com escopo `public_repo` (ou mínimo necessário para leitura de dados públicos).
   - Guardar o token em variável de ambiente (ex.: `GITHUB_TOKEN`) e não versionar no repositório.

2. **Definir a query GraphQL**
   - Usar a API GraphQL do GitHub: `https://api.github.com/graphql` (POST).
   - Query de busca: `search` com `query: "stars:>1"` (ou critério que retorne repos populares) e `type: REPOSITORY`.
   - Pedir `first: 100` na primeira página.
   - Para cada nó (repositório), solicitar no fragment/selection:
     - `createdAt` (RQ01 – idade)
     - `pushedAt` ou equivalente (RQ04 – última atualização)
     - `primaryLanguage { name }` (RQ05)
     - Contagens que exigem campos específicos:
       - **PRs aceitas:** usar `pullRequests(states: MERGED)` e pedir `totalCount` (ou paginar se a API não retornar total).
       - **Releases:** `releases { totalCount }` ou equivalente.
       - **Issues:** `issues { totalCount }` e `issues(states: CLOSED) { totalCount }` (ou equivalente) para RQ06.
   - Consultar a documentação oficial: [GitHub GraphQL API](https://docs.github.com/en/graphql).

3. **Script de requisição automática**
   - Linguagem livre (ex.: Python com `requests` para POST em JSON).
   - Cabeçalho: `Authorization: Bearer <token>`.
   - Corpo: `{ "query": "<sua query GraphQL>" }`.
   - Tratar status HTTP e possíveis erros (rate limit, token inválido).
   - Salvar resposta em arquivo JSON (para depuração) e/ou já extrair campos para uma estrutura em memória.

4. **Validar**
   - Garantir que os 100 repositórios retornados contêm todos os campos necessários para preencher as 6 métricas (e já pensar em RQ07 para S02).

**Entregáveis S01:**
- Arquivo com a query GraphQL (ex.: `query.graphql` ou string no script).
- Script que executa a consulta e obtém dados de 100 repositórios (ex.: `fetch_repos.py`).
- (Opcional) Exemplo de resposta ou amostra de dados para conferência.

---

### 3.2 Lab01S02 – Paginação (1000 repositórios) + CSV + primeira versão do relatório (3 pts)

**Objetivo:** Escalar para 1.000 repositórios via paginação da API, persistir dados em CSV e entregar primeira versão do relatório com hipóteses informais.

**Passos sugeridos:**

1. **Implementar paginação**
   - Na query GraphQL, usar `search` com `first: 100` e `after: <cursor>` para as páginas seguintes.
   - Extrair `pageInfo { endCursor, hasNextPage }` e repetir até `hasNextPage == false` ou até atingir 1.000 repositórios (10 páginas de 100).
   - Respeitar rate limit da API (ex.: 5.000 pontos/hora para GraphQL); pode ser necessário intervalo entre requisições.

2. **Estrutura do CSV**
   - Colunas sugeridas: `name`, `url`, `createdAt`, `pushedAt`, `primaryLanguage`, `pullRequestsMerged`, `releasesTotal`, `issuesTotal`, `issuesClosed` (ou nomes equivalentes aos campos da API).
   - Colunas derivadas (opcional já no CSV ou na análise): `age_days`, `days_since_last_push`, `issuesClosedRatio`.
   - Um registro por repositório.

3. **Script único ou em etapas**
   - Um script que: (a) faz todas as páginas da busca; (b) para cada repo, se necessário, faz requisições adicionais para contagens (PRs, releases, issues) se a busca não retornar tudo; (c) grava o CSV.
   - Tratar erros e timeouts; considerar salvar progresso (ex.: CSV incremental) para não perder dados.

4. **Primeira versão do relatório**
   - **Introdução:** contexto (repositórios populares no GitHub), objetivo do estudo.
   - **Hipóteses informais:** para cada RQ, redigir o que você espera (ex.: “Esperamos que repos populares sejam em média antigos”; “Esperamos que a maioria use JavaScript ou Python”).
   - **Metodologia (rascunho):** fonte dos dados (API GraphQL GitHub), critério (top 1000 por estrelas), métricas escolhidas por RQ.
   - Pode deixar resultados e discussão para S03.

**Entregáveis S02:**
- Script com paginação que gera dados dos 1.000 repositórios.
- Arquivo `.csv` com os dados.
- Documento (PDF ou MD) com primeira versão do relatório: introdução, hipóteses informais e metodologia.

---

### 3.3 Lab01S03 – Análise, visualização e relatório final (9 pts)

**Objetivo:** Sumarizar os dados (medianas e contagens por categoria), gerar visualizações e concluir o relatório com resultados e discussão.

**Passos sugeridos:**

1. **Análise por RQ**
   - **RQ01:** Calcular idade (ex.: em anos) para cada repo; sumarizar com **mediana** (e opcional: média, min, max).
   - **RQ02:** Mediana do total de PRs aceitas; distribuição se útil.
   - **RQ03:** Mediana do total de releases.
   - **RQ04:** Mediana do “tempo até última atualização” (ex.: dias desde `pushedAt`).
   - **RQ05:** **Contagem por categoria** (linguagem primária); ordenar por frequência; talvez top 10 ou 15.
   - **RQ06:** Calcular razão (issues fechadas / total issues) por repo; mediana da razão; cuidado com repos com 0 issues (definir como tratar).

2. **Visualizações**
   - Gráficos adequados a cada tipo de dado: ex. boxplot ou histograma para RQ01–RQ04 e RQ06; barras para RQ05 (contagem por linguagem).
   - Ferramentas: Python (matplotlib, seaborn, pandas) ou R, ou planilha; exportar figuras para o relatório.

3. **Bônus – RQ07**
   - Filtrar/agrupar por linguagem (ex.: top 5 linguagens vs. “outras”).
   - Para cada grupo: mediana de PRs aceitas (RQ02), mediana de releases (RQ03), mediana de “dias desde última atualização” (RQ04).
   - Comparar: “linguagens mais populares” vs. “outras” (conforme dica do enunciado).
   - Incluir tabela e/ou gráficos e breve discussão.

4. **Relatório final**
   - **(i) Introdução** com hipóteses informais (pode revisar a partir de S02).
   - **(ii) Metodologia:** critério de seleção (1000 repos, mais estrelas), fonte (GitHub GraphQL), métricas por RQ, ferramentas de análise.
   - **(iii) Resultados:** para cada RQ, apresentar sumarização (mediana; para RQ05, contagem por categoria) e visualizações.
   - **(iv) Discussão:** confrontar “o que você esperava” (hipóteses) com “o que foi obtido”; interpretar padrões e possíveis limitações.

**Entregáveis S03:**
- Código/script de análise e geração de gráficos (ex.: `analyze.py` ou notebook).
- Figuras/tabelas usadas no relatório.
- Relatório final em PDF (ou formato combinado com MD + PDF) com as quatro partes acima e, se fizer, RQ07.

---

## 4. Estrutura sugerida de pastas e arquivos

**Contexto do repositório (raiz):**
- `Artigos/` — material de apoio e Fichamentos
- `Laboratorios/` — Lab-01 a Lab-05 (5 sprints)

```
Laboratorios/Lab-01/
├── README.md
├── LABORATÓRIO 01 - Características de repositórios populares.pdf   # Enunciado
├── PLANO-IMPLEMENTACAO-Lab01.md                                    # Este plano
├── QUERY-GRAPHQL-Lab01.md                                          # Documentação da query
├── query.graphql                    # (S01) Query em arquivo para fetch_repos.py
├── fetch_repos.py                   # (S01/S02) Requisição automática + paginação
├── .env.example                     # Modelo; usar .env local (não versionar)
├── repos_1000.csv                   # (S02) Dados 1000 repos
├── analyze.py                       # (S03) Análise e gráficos [ou .ipynb]
├── figs/                            # (S03) Gráficos para o relatório
│   ├── rq01_idade.png
│   ├── rq05_linguagens.png
│   └── ...
└── relatorio/
    ├── relatorio_v1.pdf             # (S02) Primeira versão
    └── relatorio_final.pdf          # (S03) Relatório final
```

---

## 5. Checklist de conferência

- [ ] **S01:** Query GraphQL retorna, para cada repo, dados para RQ01–RQ06 (criação, última atualização, linguagem, PRs merged, releases, issues total e fechadas).
- [ ] **S01:** Script faz requisição automática (sem biblioteca que “ encapsule” a API do GitHub; uso de `requests`/fetch para HTTP está ok).
- [ ] **S02:** Paginação implementada e resultado com 1.000 repositórios.
- [ ] **S02:** CSV gerado com colunas consistentes e sem perda de dados.
- [ ] **S02:** Relatório v1 com introdução, hipóteses informais e metodologia.
- [ ] **S03:** Sumarização por mediana (e contagem por categoria para RQ05) para todas as RQs.
- [ ] **S03:** Visualizações para cada RQ (e para RQ07 se fizer bônus).
- [ ] **S03:** Relatório final com (i) introdução, (ii) metodologia, (iii) resultados, (iv) discussão.
- [ ] **Bônus (opcional):** RQ07 com análise por linguagem e comparação.

---

## 6. Referências rápidas

- **GitHub GraphQL API:** https://docs.github.com/en/graphql  
- **Search (repositórios por estrelas):** `search(query: "stars:>X", type: REPOSITORY, first: 100)`.  
- **Rate limit:** https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits  
- **Fichamentos:** `Artigos/Fichamentos/` — ver `01-GQM`, `02-GitHub-API` e `00-INDICE-FICHAMENTOS.md` para alinhamento com GQM e uso da API.
