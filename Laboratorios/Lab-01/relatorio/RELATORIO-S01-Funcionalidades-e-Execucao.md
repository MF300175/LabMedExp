# Lab01S01 — Relatório técnico (formato acadêmico)

## Resumo

Este relatório descreve a implementação e a execução da etapa **Lab01S01** do laboratório “Características de repositórios populares”. A etapa consiste em (i) definir uma **consulta GraphQL** que retorne, para cada repositório, os campos necessários para responder às questões de pesquisa **RQ01–RQ06**; e (ii) implementar um **script próprio** que consuma a API GraphQL do GitHub e realize a coleta automática de **100 repositórios**, gerando um artefato local de dados para validação.

## 1. Introdução

Repositórios open-source populares no GitHub podem apresentar padrões de maturidade, atividade e engajamento comunitário. Para caracterizar tais repositórios, o laboratório propõe a coleta de métricas associadas a seis questões de pesquisa (RQ01–RQ06). Nesta sprint, o foco está em viabilizar a coleta automática e reprodutível, respeitando a restrição de **não utilizar bibliotecas de terceiros que encapsulem consultas à API do GitHub**.

## 2. Objetivos (Lab01S01)

Os objetivos específicos desta etapa são:

1. Elaborar uma consulta **GraphQL** contendo os campos necessários para responder às RQ01–RQ06.
2. Implementar um script que execute requisições HTTP para `https://api.github.com/graphql` e colete dados de **100 repositórios**.
3. Gerar artefatos locais (JSON) que permitam auditoria/validação da coleta.

Arquivos centrais:

- `query.graphql`: consulta GraphQL utilizada na coleta.
- `fetch_repos.py`: script de coleta automática.

## 3. Materiais e Métodos

### 3.1 Ambiente e dependências

- Linguagem: Python 3.
- Dependência de HTTP: `requests` (instalada via `requirements.txt`).

Instalação:

```powershell
pip install -r requirements.txt
```

### 3.2 Fonte de dados e autenticação

As requisições são realizadas contra o endpoint da GitHub GraphQL API:

- URL: `https://api.github.com/graphql`
- Método: `POST`
- Autenticação: header `Authorization: Bearer <token>`

O token é lido de `GITHUB_TOKEN`, definido no ambiente ou em um arquivo `.env` local.

Configuração por sessão (PowerShell):

```powershell
$env:GITHUB_TOKEN = "<seu_token_aqui>"
```

Configuração por arquivo `.env` (local):

```env
GITHUB_TOKEN=<seu_token_aqui>
```

Observação: o `.env` é para uso local e não deve ser versionado.

### 3.3 Estratégia de coleta e robustez

A coleta é executada em páginas (“paginação”), acumulando resultados até atingir o alvo. Para melhorar a robustez em cenários de instabilidade de rede/servidor, o script aplica retentativas com **backoff exponencial** para erros transitórios (`502/503/504`).

Defaults utilizados (podem ser sobrescritos por variáveis de ambiente):

- `LAB01_TARGET_REPOS = 100`
- `LAB01_PAGE_SIZE = 10`
- `LAB01_MAX_RETRIES = 8`

## 4. Procedimento de execução

### 4.1 Execução padrão

Na pasta `Laboratorios/Lab-01`:

```powershell
cd LabMedExp\Laboratorios\Lab-01
python fetch_repos.py
```

Saída esperada (resumo):

- Progresso incremental (`Acumulado: x/100`)
- `Total coletado: 100`
- Indicação dos arquivos gerados (ver Seção 5)

### 4.2 Parâmetros opcionais (variáveis de ambiente)

Alterar número de repositórios:

```powershell
$env:LAB01_TARGET_REPOS = "100"
python fetch_repos.py
```

Alterar page size (regra: `1 <= LAB01_PAGE_SIZE <= 100`):

```powershell
$env:LAB01_PAGE_SIZE = "10"
python fetch_repos.py
```

Alterar número de retentativas:

```powershell
$env:LAB01_MAX_RETRIES = "8"
python fetch_repos.py
```

Logs opcionais:

```powershell
$env:LAB01_DEBUG = "1"
$env:LAB01_SHOW_SAMPLE = "1"
python fetch_repos.py
```

## 5. Artefatos gerados e organização dos dados

Ao término da execução, o script grava artefatos em `data/`:

- `data/repos_s01_100.json`: último resultado (sobrescrito a cada execução).
- `data/repos_s01_100_<timestamp>.json`: histórico (um novo arquivo por execução).

Os arquivos JSON contêm a lista de repositórios coletados e os campos necessários para as métricas das RQ01–RQ06.

## 6. Validação e testes

### 6.1 Validação interna (campos obrigatórios)

Após a coleta, é realizada uma validação leve para identificar repositórios que não contenham campos essenciais (por exemplo: `createdAt`, `pushedAt`, `pullRequests.totalCount`, etc.). Caso ocorram inconsistências, o script emite aviso em `stderr`.

### 6.2 Testes unitários (offline)

Os testes unitários validam parsing de `.env`, leitura de query e tratamento de respostas HTTP/JSON usando `mock` (sem acesso à rede):

```powershell
cd LabMedExp\Laboratorios\Lab-01
python -m unittest -v test_fetch_repos_unit.py
```

### 6.3 Testes de integração (opcionais)

Os testes de integração requerem `GITHUB_TOKEN` válido. O teste rápido verifica autenticação e `rateLimit`:

```powershell
cd LabMedExp\Laboratorios\Lab-01
$env:GITHUB_TOKEN = "<seu_token_aqui>"
python -m unittest -v test_integration_github_graphql.py
```

Opcionalmente, há um smoke test mais pesado com a query do laboratório:

```powershell
$env:RUN_SLOW_INTEGRATION = "1"
python -m unittest -v test_integration_github_graphql.py
```

## 7. Tratamento de erros e diagnósticos

- **HTTP 401 (Bad credentials):** indica token inválido/expirado/copiado incorretamente.
- **HTTP 403 (rate limit):** indica limitação de cota; recomenda-se aguardar o reset ou usar token com cota adequada.
- **HTTP 502/503/504:** indicam instabilidade temporária (GitHub/rede/proxy). O script aplica retentativas e backoff; caso persista, recomenda-se tentar outra rede, desativar VPN/proxy ou executar mais tarde.

## 8. Limitações e ameaças à validade

- **Dependência de infraestrutura externa:** a coleta depende da disponibilidade da API do GitHub e da qualidade da rede (possíveis `502/503/504`).
- **Variabilidade temporal:** os valores coletados podem variar com o tempo (ex.: `pushedAt`, issues e PRs), tornando natural que coletas em datas diferentes não sejam idênticas.
- **Autenticação e permissões:** tokens inválidos ou com restrições podem impedir a coleta adequada.

## 9. Conclusão e próximos passos

A etapa Lab01S01 foi concluída com (i) query GraphQL contendo os campos necessários para RQ01–RQ06 e (ii) script próprio de coleta de 100 repositórios com geração de artefatos JSON (incluindo histórico por timestamp). As próximas etapas (fora do escopo do S1) incluem expandir a coleta para 1.000 repositórios, exportação em CSV e elaboração do relatório v1/final com sumarizações e visualizações.
