# Relatório de Análise dos 1.000 Repositórios Populares do GitHub

## Introdução

Contextualização do estudo sobre repositórios open-source populares no GitHub. Apresentação do problema, questões de pesquisa (RQ01–RQ06), hipóteses e objetivos do experimento.

## Metodologia

- Passo a passo do experimento: coleta automática via API GraphQL, critérios de seleção (top 1.000 por estrelas), processamento dos dados.
- Decisões: escolha dos campos, tratamento de erros, paginação, ordenação.
- Materiais utilizados: Python, requests, scripts de coleta, CSV gerado.
- Métodos utilizados: análise estatística, visualização gráfica.
- Métricas e suas unidades: idade (anos), PRs aceitas (contagem), releases (contagem), issues (contagem/razão), linguagem (categoria).

## Visualização dos Resultados

- Tabelas e gráficos sumarizando os dados coletados.
- Estatísticas descritivas para cada métrica das RQs.
- Exemplos de visualização: boxplots, histogramas, gráficos de barras por linguagem.

## Discussão dos Resultados

- Confronto dos resultados com as questões de pesquisa:
  - RQ01: Idade dos repositórios (mediana, distribuição)
  - RQ02: Contribuição externa (PRs aceitas)
  - RQ03: Releases
  - RQ04: Atualização
  - RQ05: Linguagens mais populares
  - RQ06: Issues fechadas
- Insights, comparações, estatísticas relevantes.

## Conclusão

- Tomada de decisão sobre as hipóteses e questões de pesquisa.
- Sugestões para trabalhos futuros.
- Resultado conclusivo sucinto.

## Plus: Confronto com Literatura

- Comparação dos resultados obtidos com artigos ou trabalhos científicos relacionados.
- Discussão sobre corroborar ou contestar achados da literatura.
