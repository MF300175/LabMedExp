# RELATORIO-S02

## Introdução

Este relatório consolida a coleta e o tratamento de métricas de qualidade interna em repositórios Java populares no GitHub, seguindo o enunciado do Lab-02. O foco é construir uma base empírica consistente para responder as questões de pesquisa sobre como fatores de processo (popularidade, maturidade, atividade e tamanho) se relacionam com métricas de qualidade (CBO, DIT, LCOM).

## Contextualização

Repositórios open-source evoluem por contribuições diversas, o que pode impactar atributos como modularidade, manutenibilidade e coesão. A literatura recomenda o uso de métricas e análise estatística para observar tendências e orientar interpretações. Neste laboratório, o CK é usado para extrair métricas de qualidade por classe, e os resultados são sumarizados por repositório.

## Problema foco do experimento

Avaliar se características do processo de desenvolvimento de repositórios Java (popularidade, maturidade, atividade e tamanho) possuem relação com métricas de qualidade interna (CBO, DIT e LCOM) calculadas pelo CK.

## Questões-problema ou Questões-Pesquisa

- **RQ01**: Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?
- **RQ02**: Qual a relação entre a maturidade dos repositórios e as suas características de qualidade?
- **RQ03**: Qual a relação entre a atividade dos repositórios e as suas características de qualidade?
- **RQ04**: Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?

## Hipóteses

Hipóteses informais (pre-análise) conforme `HIPOTESES-S02.md`:

- **H1a**: Repositórios com mais estrelas tendem a ter menor CBO.
- **H1b**: Repositórios muito populares podem ter LCOM mais alto por crescimento acelerado.
- **H2a**: Repositórios mais antigos apresentam CBO maior por acumularem dependência histórica.
- **H2b**: Maturidade maior tende a estabilizar DIT.
- **H3a**: Projetos com mais releases apresentam LCOM menor.
- **H3b**: Alta atividade pode aumentar CBO.
- **H4a**: Projetos com maior LOC tendem a ter CBO mais elevado.
- **H4b**: Maior volume de comentários pode correlacionar com menor LCOM.

## Objetivo (principal e específicos)

**Objetivo principal**

Avaliar características de qualidade interna de repositórios Java populares e relacioná-las com aspectos do processo de desenvolvimento (popularidade, maturidade, atividade e tamanho).

**Objetivos específicos**

- Identificar a relação entre popularidade e CBO/DIT/LCOM.
- Investigar a relação entre maturidade e CBO/DIT/LCOM.
- Examinar a relação entre atividade e CBO/DIT/LCOM.
- Verificar a relação entre tamanho e CBO/DIT/LCOM.

## Metodologia

### Passo a passo do experimento

1. Leitura do dataset `Lab-02S01/data/repos_1000.csv`.
2. Coleta em lote: clone shallow -> CK -> cloc -> sumarização por repositório.
3. Registro de sucesso/falha em `logs/collection_log.txt`.
4. Limpeza e validação da base em `metrics_all_1000_repos_cleaned.csv`.
5. Estatísticas descritivas e correlações preliminares.
6. Análise estatística final e gráficos na S03 (Pearson/Spearman).

### Decisões

- Não substituir repositórios que falharam no CK para manter a amostra original do top-1000.
- Preferência por Spearman devido a não normalidade (Shapiro-Wilk).
- Uso de clone shallow e remoção do `temp` para reduzir consumo de disco.

### Materiais utilizados

- Python 3.9+
- JDK/JRE para executar o CK
- CK (jar local)
- cloc (opcional para LOC e comment_lines)
- Scripts S02 e S03

### Métodos utilizados

- Coleta automatizada por scripts Python.
- Sumarização por repositório (média, mediana, desvio).
- Testes de normalidade (Shapiro-Wilk).
- Correlação Pearson e Spearman.

### Métricas e suas Unidades

**Processo**

- Popularidade: `stargazers` (contagem).
- Maturidade: `age_years` (anos, derivado de `created_at`).
- Atividade: `releases_count` (contagem).
- Tamanho: `loc` e `comment_lines` (linhas).

**Qualidade (CK)**

- CBO: `cbo_mean`, `cbo_median`, `cbo_std`.
- DIT: `dit_mean`, `dit_median`, `dit_std`.
- LCOM: `lcom_mean`, `lcom_median`, `lcom_std`.
- Volume de classes: `classes_count`.

## Visualização dos Resultados

Visualizações geradas na S03 (arquivos com sufixo de data para evitar sobrescrita):

**Visão geral**

![Heatmap de correlação](Lab-02S03/figs/correlation_heatmap_2026-04-03.png)

![Boxplots de distribuição](Lab-02S03/figs/distribution_boxplots_2026-04-03.png)

**RQ01: Popularidade vs Qualidade**

![RQ01 - Stars vs CBO](Lab-02S03/figs/RQ01_scatter_stars_vs_cbo_2026-04-03.png)

![RQ01 - Stars vs DIT](Lab-02S03/figs/RQ01_scatter_stars_vs_dit_2026-04-03.png)

![RQ01 - Stars vs LCOM](Lab-02S03/figs/RQ01_scatter_stars_vs_lcom_2026-04-03.png)

**RQ02: Maturidade vs Qualidade**

![RQ02 - Age vs CBO](Lab-02S03/figs/RQ02_scatter_age_vs_cbo_2026-04-03.png)

![RQ02 - Age vs DIT](Lab-02S03/figs/RQ02_scatter_age_vs_dit_2026-04-03.png)

![RQ02 - Age vs LCOM](Lab-02S03/figs/RQ02_scatter_age_vs_lcom_2026-04-03.png)

**RQ03: Atividade vs Qualidade**

![RQ03 - Releases vs CBO](Lab-02S03/figs/RQ03_scatter_releases_vs_cbo_2026-04-03.png)

![RQ03 - Releases vs DIT](Lab-02S03/figs/RQ03_scatter_releases_vs_dit_2026-04-03.png)

![RQ03 - Releases vs LCOM](Lab-02S03/figs/RQ03_scatter_releases_vs_lcom_2026-04-03.png)

**RQ04: Tamanho vs Qualidade**

![RQ04 - LOC vs CBO](Lab-02S03/figs/RQ04_scatter_loc_vs_cbo_2026-04-03.png)

![RQ04 - LOC vs DIT](Lab-02S03/figs/RQ04_scatter_loc_vs_dit_2026-04-03.png)

![RQ04 - LOC vs LCOM](Lab-02S03/figs/RQ04_scatter_loc_vs_lcom_2026-04-03.png)

![RQ04 - Comments vs CBO](Lab-02S03/figs/RQ04_scatter_comments_vs_cbo_2026-04-03.png)

![RQ04 - Comments vs DIT](Lab-02S03/figs/RQ04_scatter_comments_vs_dit_2026-04-03.png)

![RQ04 - Comments vs LCOM](Lab-02S03/figs/RQ04_scatter_comments_vs_lcom_2026-04-03.png)

## Sumarização por RQ (medidas centrais)

Base: `Lab-02S02/data/metrics_all_1000_repos_cleaned.csv` (n = 972).  
Para maturidade (`age_years`), o valor foi calculado a partir de `created_at` usando a data de referência **2026-04-04**, com a fórmula **(data_ref − created_at).days / 365.25**.  
O desvio‑padrão apresentado é **populacional** (σ, `pstdev`), e não amostral (n−1).

**RQ01 – Popularidade**

| Variável | Média | Mediana | Desvio Padrão |
|---|---:|---:|---:|
| `stargazers` | 9622.253 | 5792.000 | 11777.978 |
| `cbo_mean` | 5.317 | 5.274 | 1.848 |
| `dit_mean` | 1.453 | 1.390 | 0.361 |
| `lcom_mean` | 116.099 | 24.527 | 1753.629 |

**RQ02 – Maturidade**

| Variável | Média | Mediana | Desvio Padrão |
|---|---:|---:|---:|
| `age_years` | 10.112 | 10.282 | 3.162 |
| `cbo_mean` | 5.317 | 5.274 | 1.848 |
| `dit_mean` | 1.453 | 1.390 | 0.361 |
| `lcom_mean` | 116.099 | 24.527 | 1753.629 |

**RQ03 – Atividade**

| Variável | Média | Mediana | Desvio Padrão |
|---|---:|---:|---:|
| `releases_count` | 40.445 | 11.000 | 88.462 |
| `cbo_mean` | 5.317 | 5.274 | 1.848 |
| `dit_mean` | 1.453 | 1.390 | 0.361 |
| `lcom_mean` | 116.099 | 24.527 | 1753.629 |

**RQ04 – Tamanho**

| Variável | Média | Mediana | Desvio Padrão |
|---|---:|---:|---:|
| `loc` | 221492.987 | 32645.000 | 622457.772 |
| `comment_lines` | 39270.286 | 5956.000 | 101819.817 |
| `cbo_mean` | 5.317 | 5.274 | 1.848 |
| `dit_mean` | 1.453 | 1.390 | 0.361 |
| `lcom_mean` | 116.099 | 24.527 | 1753.629 |


## Discussão dos resultados

### Confrontar Questões-pesquisa

**RQ01 (Popularidade)**

- Spearman: valores próximos de zero e sem significância estatística.
- Interpretação: popularidade não se relaciona de forma clara com CBO, DIT ou LCOM.

**RQ02 (Maturidade)**

- Spearman aponta relação positiva fraca a moderada com DIT e fraca com LCOM.
- Interpretação: repositórios mais antigos tendem a apresentar hierarquias mais profundas e leve aumento de falta de coesão.

**RQ03 (Atividade)**

- Spearman indica relação positiva moderada com CBO e LCOM, e fraca com DIT.
- Interpretação: maior atividade pode vir acompanhada de aumento de acoplamento e menor coesão.

**RQ04 (Tamanho)**

- Spearman indica relação positiva moderada com CBO e LCOM para **`loc`** e **`comment_lines`**, e relação fraca com DIT.
- Interpretação: repositórios maiores (mais código e comentários) tendem a ter maior acoplamento e menor coesão.

### Insights

- A maioria das relações e fraca a moderada, sugerindo influência limitada de variáveis de processo sobre qualidade.
- LCOM apresenta alta assimetria, o que reforça o uso de medidas robustas.

### Gráficos

Os gráficos de dispersão e o heatmap de correlação facilitam a identificação de tendências e outliers, principalmente para LCOM e LOC.

### Comparações

- Popularidade apresentou o menor nível de associação com qualidade.
- Atividade e tamanho mostraram as associações mais consistentes com CBO e LCOM.

### Estatísticas

Testes de normalidade (Shapiro-Wilk):

| Métrica | W | p | n |
|---|---:|---:|---:|
| `cbo_mean` | 0.9481 | 5.494e-18 | 972 |
| `dit_mean` | 0.7814 | 4.062e-34 | 972 |
| `lcom_mean` | 0.0255 | 1.16e-56 | 972 |
| `stargazers` | 0.4784 | 1.618e-46 | 972 |
| `loc` | 0.3597 | 3.253e-49 | 945 |
| `comment_lines` | 0.4030 | 4.117e-48 | 945 |

Principais coeficientes Spearman (S03):

- `releases_count` vs `cbo_mean`: r=0.3973
- `releases_count` vs `lcom_mean`: r=0.3335
- `loc` vs `cbo_mean`: r=0.3711
- `loc` vs `lcom_mean`: r=0.4086
- `comment_lines` vs `cbo_mean`: r=0.3826
- `comment_lines` vs `dit_mean`: r=0.2114
- `comment_lines` vs `lcom_mean`: r=0.4454
- `age_years` vs `dit_mean`: r=0.2822

## Conclusão

### Tomada de decisão

Os resultados indicam que **atividade** e **tamanho** são os fatores com maior associação com CBO e LCOM, enquanto **popularidade** não apresenta relação significativa. Isso sugere que a complexidade estrutural e mais sensível a dinâmica de evolução e escala do que ao reconhecimento social.

### Sugestões futuras

- Explorar outras métricas de qualidade (ex.: WMC, RFC) para validar o padrão observado.
- Reavaliar com amostras menores e segmentadas por domínio de aplicação.
- Realizar análise longitudinal para observar mudanças ao longo do tempo.

### Resultado conclusivo sucinto

A análise estatística indica **associações fracas a moderadas** entre qualidade interna e fatores de processo, com destaque para atividade e tamanho como os melhores preditores entre as variáveis analisadas.

### Plus: Confrontar com artigos ou trabalhos científicos

A confrontação com a literatura foi realizada de forma **corroborativa** e **contestadora**, usando os fichamentos disponíveis em `Artigos/Fichamentos`:

- **Corroborativa**:  
  O estudo de Subramanyam e Krishnan (2003) sobre métricas CK mostra associação significativa entre métricas de design OO e qualidade/defeitos, mesmo controlando tamanho. Isso fortalece a escolha de CBO/DIT/LCOM como proxies relevantes de qualidade interna no nosso experimento.  
  Trabalhos como SmellyCode++ (ferramentas e estratégias de detecção baseadas em métricas) e o estudo de Palomba et al. (2018) sobre code smells em larga escala reforçam o uso de análise estática e métricas para avaliar qualidade em repositórios reais, alinhado ao nosso pipeline de coleta.

- **Contestadora/nuançadora**:  
  O estudo sobre métricas em software ágil (Destefanis et al.) indica que distribuições de métricas CK podem não variar fortemente entre contextos de desenvolvimento distintos. Isso sugere cautela ao interpretar relações de processo como determinantes fortes de qualidade, o que é consistente com as correlações fracas observadas para popularidade e algumas associações moderadas nas demais variáveis.  
  O trabalho de Tufano et al. (2015) mostra que a introdução de problemas de qualidade (smells) pode ocorrer por motivos não triviais e não necessariamente ligados apenas à atividade de desenvolvimento, o que reforça a interpretação de que correlação não implica causalidade.

Em síntese, a literatura **sustenta o uso de métricas CK** como indicadores de qualidade, mas também **reforça a necessidade de interpretar associações com cautela**, especialmente quando as correlações são fracas ou moderadas.

## Referências (APA)

- Subramanyam, R., & Krishnan, M. S. (2003). Empirical analysis of CK metrics for object-oriented design complexity: Implications for software defects. *IEEE Transactions on Software Engineering, 29*(4), 297–310.
- Palomba, F., Bavota, G., Di Penta, M., Fasano, F., Oliveto, R., & De Lucia, A. (2018). On the diffuseness and the impact on maintainability of code smells: A large scale empirical investigation. *Empirical Software Engineering, 23*(3), 1188–1221.
- Tufano, M., Palomba, F., Bavota, G., Oliveto, R., Di Penta, M., De Lucia, A., & Poshyvanyk, D. (2015). When and why your code starts to smell bad. In *Proceedings of ICSE 2015*.
- Destefanis, G., Counsell, S., Concas, G., & Tonelli, R. (s.d.). *Software metrics in agile software: An empirical study*. University of Cagliari / Brunel University.
