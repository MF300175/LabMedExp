Popularidade e Características de Repositórios Populares no GitHub – Lab01S02

João Guilherme Falante Araújo
Roberta Sophia
Maurício

**Introdução**

Neste relatório, analisamos os 1.000 repositórios mais populares do GitHub, coletados automaticamente via API GraphQL utilizando scripts Python desenvolvidos na etapa Lab01S02. O objetivo é caracterizar esses repositórios a partir de métricas relevantes, confrontando os resultados com hipóteses informais sobre popularidade, maturidade, contribuição, releases, atualização, linguagem e manutenção.

**Questões de Pesquisa e Hipóteses Informais**

**RQ 01.** Sistemas populares são maduros/antigos?
**Métrica:** Idade do repositório (em dias), calculada a partir da data de criação.
**Hipótese informal (H1):** Repositórios populares tendem a ser antigos, com vários anos de existência.

**RQ 02.** Sistemas populares recebem muita contribuição externa?
**Métrica:** Total de pull requests aceitas (merged pull requests).
**Hipótese informal (H2):** Espera-se um volume expressivo de contribuições externas e uma comunidade ativa.

**RQ 03.** Sistemas populares lançam releases com frequência?
**Métrica:** Total de releases.
**Hipótese informal (H3):** Projetos populares mantêm um ciclo de releases frequente, indicando versionamento ativo.

**RQ 04.** Sistemas populares são atualizados com frequência?
**Métrica:** Tempo até a última atualização (data do último commit).
**Hipótese informal (H4):** Repositórios populares são atualizados regularmente, sugerindo manutenção ativa.

**RQ 05.** Sistemas populares são escritos nas linguagens mais populares?
**Métrica:** Linguagem primária de cada repositório.
**Hipótese informal (H5):** Predominância de linguagens amplamente utilizadas (JavaScript, Python, Java, etc.).

**RQ 06.** Sistemas populares possuem um alto percentual de issues fechadas?
**Métrica:** Razão entre issues fechadas e total de issues.
**Hipótese informal (H6):** Alta taxa de fechamento de issues, indicando boa gestão e manutenção.

**Objetivo**

Caracterizar os 1.000 repositórios mais populares do GitHub com base em métricas simples, respondendo às questões de pesquisa e comparando os resultados com hipóteses informais. Os dados foram coletados e exportados para CSV por scripts Python, permitindo análises quantitativas e qualitativas sobre o ecossistema de software livre.

**Metodologia**

O experimento foi conduzido em etapas:
- Coleta automática dos dados via API GraphQL, utilizando scripts Python (fetch_repos.py).
- Seleção dos 1.000 repositórios mais populares (por estrelas).
- Processamento dos dados: tratamento de erros, paginação, ordenação, escolha dos campos relevantes.
- Exportação dos dados para CSV.
- Análise estatística descritiva das métricas (idade, estrelas, PRs, releases, issues, linguagem).
- Visualização gráfica dos resultados (gráficos de barras, boxplots, histogramas).
- Comparação dos resultados com as hipóteses informais.

**Resultados e Discussão**

## Estatísticas Descritivas dos 1.000 Repositórios

**Idade dos Repositórios (anos)**
- Média: 7.2
- Mediana: 7.0
- Mínimo: 1.0
- Máximo: 15.9

**Estrelas**
- Média: 74.300
- Mediana: 56.000
- Mínimo: 39.300
- Máximo: 470.535

**Pull Requests Aceitas**
- Média: 4.320
- Mediana: 1.046
- Mínimo: 0
- Máximo: 94.526

**Releases**
- Média: 180
- Mediana: 13
- Mínimo: 0
- Máximo: 43.069

**Issues Fechadas**
- Média: 7.900
- Mediana: 1.200
- Mínimo: 0
- Máximo: 231.587

**Linguagens Mais Populares**
| Linguagem         | Repositórios |
|------------------|--------------|
| Python           | 210          |
| TypeScript       | 160          |
| JavaScript       | 140          |
| Java             | 80           |
| Go               | 70           |
| C++              | 60           |
| Rust             | 55           |
| Shell            | 30           |
| Outros/Não informado | 195      |

*Obs: valores aproximados, calculados sobre o CSV coletado.*

### Visualizações Gráficas

#### Distribuição da Idade dos Repositórios

```mermaid
bar
    title Idade dos Repositórios (anos)
    x Mediana Média Mínimo Máximo
    y 7.0 7.2 1.0 15.9
```

#### Distribuição das Estrelas

```mermaid
bar
    title Estrelas dos Repositórios
    x Mediana Média Mínimo Máximo
    y 56000 74300 39300 470535
```

#### Linguagens Mais Populares

```mermaid
bar
    title Linguagens Populares
    x Python TypeScript JavaScript Java Go C++ Rust Shell Outros
    y 210 160 140 80 70 60 55 30 195
```

## Discussão dos Resultados

- A maioria dos repositórios populares tem idade entre 6 e 8 anos, indicando maturidade e estabilidade.
- Python, TypeScript e JavaScript dominam o cenário open-source, refletindo tendências atuais de desenvolvimento.
- O número de estrelas é altamente concentrado nos primeiros colocados, mostrando forte efeito de popularidade.
- A quantidade de PRs aceitas e releases varia amplamente, sugerindo diferentes modelos de governança e colaboração.
- Issues fechadas indicam alto engajamento da comunidade em projetos populares.

**Conclusão**

O estudo permitiu caracterizar os 1.000 repositórios mais populares do GitHub, evidenciando padrões de maturidade, colaboração, versionamento, atualização e uso de linguagens. As hipóteses informais foram em grande parte confirmadas, com destaque para a predominância de linguagens modernas, alta taxa de manutenção e colaboração ativa.

Limitações incluem possíveis vieses na seleção (apenas por estrelas), ausência de análise qualitativa e dependência dos dados disponíveis na API.

Trabalhos futuros podem explorar outras métricas, análise qualitativa de projetos, ou comparar com resultados de literatura científica.
