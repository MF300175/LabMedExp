# RELATORIO-S01 - Lab-02
## Laboratorio de Experimentacao de Software

**Projeto:** Lab-02 - Um estudo das caracteristicas de qualidade de sistemas Java  
**Sprint:** Lab-02S01  
**Data de execucao:** 23/03/2026  
**Repositorio:** MF300175/LabMedExp

---

## 1. Objetivo da Sprint S01

Materializar os entregaveis iniciais do Lab-02, conforme enunciado:

1. Lista dos 1.000 repositorios Java mais populares do GitHub.
2. Script de automacao para coleta e processamento inicial de metricas.
3. Arquivo CSV com o resultado das medicoes de 1 repositorio usando CK.

---

## 2. Escopo Implementado

Nesta sprint foi implementado e executado:

1. Coleta via GitHub GraphQL com paginacao e retentativas.
2. Persistencia dos dados em JSON e CSV.
3. Pipeline de prova de conceito para 1 repositorio:
   - leitura do dataset coletado
   - clone do repositorio
   - execucao da ferramenta CK
   - sumarizacao de CBO, DIT e LCOM (media, mediana e desvio padrao)
4. Script PowerShell de automacao ponta a ponta.

---

## 3. Artefatos Gerados

### 3.1 Scripts e configuracao

- `fetch_repos.py`
- `collect_sample_metrics.py`
- `query.graphql`
- `scripts/run_s01_pipeline.ps1`
- `.env.example`

### 3.2 Saidas da sprint

- `data/repos_1000.json`
- `data/repos_1000.csv`
- `data/sample_metrics.csv`

Observacao: logs de execucao podem ser gerados localmente durante novas rodadas, mas nao sao artefatos obrigatorios da entrega versionada.

---

## 4. Metodologia Aplicada

### 4.1 Coleta dos repositorios

1. Consulta GraphQL com filtro `language:Java sort:stars-desc`.
2. Paginas sequenciais ate atingir 1.000 repositorios.
3. Conversao e normalizacao dos campos de processo:
   - `stargazers`
   - `created_at`
   - `updated_at`
   - `age_years`
   - `releases_count`

### 4.2 Medicao de qualidade (prova de conceito)

1. Selecao do primeiro repositorio do CSV (`Snailclimb/JavaGuide`).
2. Clone local temporario.
3. Execucao do CK (`ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar`).
4. Leitura de `class.csv` e agregacao:
   - CBO: media, mediana, desvio padrao
   - DIT: media, mediana, desvio padrao
   - LCOM: media, mediana, desvio padrao
5. Geracao de `sample_metrics.csv`.

---

## 5. Resultados Obtidos

### 5.1 Coleta dos 1.000 repositorios

**Status:** Concluida com sucesso.

Evidencias:

- `repos_1000.json` com `"count": 1000`
- `repos_1000.csv` com 1000 linhas de dados

Amostra inicial do dataset (top por estrelas):

| # | name_with_owner | stars | age_years | releases_count |
|---|-----------------|-------|-----------|----------------|
| 1 | Snailclimb/JavaGuide | 154413 | 7.877 | 0 |
| 2 | krahets/hello-algo | 123744 | 3.381 | 10 |
| 3 | GrowingGit/GitHub-Chinese-Top-Charts | 107056 | 6.546 | 0 |
| 4 | iluwatar/java-design-patterns | 93832 | 11.619 | 0 |
| 5 | macrozheng/mall | 83221 | 7.967 | 3 |

### 5.2 Medicao de 1 repositorio com CK

**Repositorio de amostra:** `Snailclimb/JavaGuide`  
**Status:** Concluida com sucesso.

Resultado registrado em `data/sample_metrics.csv`:

| repositorio | stars | age_years | releases | cbo_mean | cbo_median | cbo_std | dit_mean | dit_median | dit_std | lcom_mean | lcom_median | lcom_std | classes_count |
|-------------|-------|-----------|----------|----------|------------|---------|----------|------------|---------|-----------|-------------|----------|---------------|
| Snailclimb/JavaGuide | 154413 | 7.877 | 0 | 2.3333 | 0.0 | 3.2998 | 1.0 | 1.0 | 0.0 | 14.3333 | 0.0 | 20.2704 | 3 |

---

## 6. Problemas Encontrados e Correcoes

### 6.1 Instabilidade da API GitHub (HTTP 502/504)

Problema:

- Em configuracoes de pagina maiores, ocorreram falhas recorrentes de gateway.

Acao tomada:

- Ajuste para configuracao mais estavel (padrao):
  - `LAB02_TARGET_REPOS=1000`
  - `LAB02_PAGE_SIZE=20`
  - `LAB02_TIMEOUT_SECS=90`
  - `LAB02_MAX_RETRIES=20`

Resultado:

- Coleta completa de 1.000 repositorios realizada com sucesso.

### 6.2 Erro de permissao no Windows durante limpeza de clone

Problema:

- `PermissionError [WinError 5]` ao remover arquivos em `.git/objects/pack`.

Acao tomada:

- Implementacao de limpeza robusta no `collect_sample_metrics.py`:
  - tratamento de arquivo read-only
  - retentativas com atraso progressivo

Resultado:

- Pipeline CK executado com sucesso e `sample_metrics.csv` gerado.

### 6.3 Disponibilizacao do CK

Problema:

- Nao havia CK instalado localmente.

Acao tomada:

1. Clone do repositorio oficial do CK.
2. Build com Maven.
3. Uso do jar gerado:
   - `C:\Users\LENOVO\tools\ck\ck-src\target\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar`

Resultado:

- Etapa de medicao local habilitada.

---

## 7. Validacao Contra os Criterios de Aceite do S01

| Criterio | Status | Evidencia |
|---------|--------|-----------|
| Lista de 1.000 repositorios Java | OK | `data/repos_1000.json`, `data/repos_1000.csv` |
| Script de automacao de coleta | OK | `fetch_repos.py`, `scripts/run_s01_pipeline.ps1` |
| Script de clone + CK + agregacao | OK | `collect_sample_metrics.py` |
| CSV de medicao de 1 repositorio | OK | `data/sample_metrics.csv` |
| Relatorio tecnico da sprint | OK | `docs/RELATORIO-S01.md` |

**Conclusao da validacao:** Sprint Lab-02S01 concluida com os entregaveis obrigatorios materializados.

---

## 8. Comentarios e Observacoes Tecnicas

1. A codificacao exibida no terminal em alguns momentos (ex.: `ConcluÝdo`) nao afetou os resultados.
2. O aviso do VS Code sobre `python.terminal.useEnvFile` nao bloqueia o pipeline, pois o script PowerShell carrega o `.env` explicitamente.
3. O dataset atual ja permite iniciar a Sprint S02 sem necessidade de nova coleta imediata.
4. A robustez do processo melhorou com:
   - parametros de coleta conservadores
   - retentativas
   - tratamento de limpeza em ambiente Windows

---

## 8.1 Tabela de Interpretacao Pratica das Metricas

| Metrica | Faixa | Interpretacao pratica | Sinal para qualidade |
|---------|-------|-----------------------|----------------------|
| CBO media | 0 a 5 | Baixo acoplamento entre classes | Favoravel |
| CBO media | 5 a 10 | Acoplamento moderado | Atencao |
| CBO media | > 10 | Acoplamento alto, maior risco de manutencao dificil | Desfavoravel |
| DIT media | 0 a 2 | Heranca rasa, estrutura simples | Favoravel |
| DIT media | 2 a 4 | Heranca moderada | Atencao |
| DIT media | > 4 | Heranca profunda, maior complexidade de entendimento | Desfavoravel |
| LCOM media | Baixa (proxima de 0) | Alta coesao entre metodos | Favoravel |
| LCOM media | Intermediaria | Coesao parcial | Atencao |
| LCOM media | Alta | Baixa coesao, possivel classe com responsabilidades excessivas | Desfavoravel |
| Desvio padrao (std) | Baixo | Comportamento homogeneo entre classes | Favoravel |
| Desvio padrao (std) | Alto | Grande variabilidade; pode haver outliers | Atencao analitica |
| classes_count | Muito baixo (ex.: < 10) | Amostra pequena para generalizar | Baixa confiabilidade estatistica |
| classes_count | Medio/alto | Maior robustez da sumarizacao | Melhor confiabilidade |

Observacao metodologica: esta tabela deve ser usada como guia inicial de leitura. Para conclusoes finais na S02 e S03, recomenda-se comparar os valores com os percentis da propria base de 1.000 repositorios (Q1, mediana e Q3), reduzindo risco de interpretacao fora do contexto da amostra.

---

## 9. Comandos de Execucao Utilizados

### 9.1 Pipeline completo S01

```powershell
cd C:\PUC_2026\LAbMed_2303\LabMedExp\Laboratorios\Lab-02\Lab-02S01
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_s01_pipeline.ps1
```

### 9.2 Pipeline apenas CK (sem nova coleta)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_s01_pipeline.ps1 -SkipFetch
```

---

## 10. Proximos Passos (S02)

1. Executar medicao em lote dos 1.000 repositorios.
2. Consolidar arquivo unico de metricas para toda a amostra.
3. Elaborar hipoteses informais para RQ01-RQ04.
4. Iniciar analise exploratoria e estatistica descritiva.

---

## 11. Conclusao

A Sprint Lab-02S01 foi concluida com sucesso. Os artefatos obrigatorios foram gerados e validados, incluindo:

1. base de 1.000 repositorios Java,
2. pipeline automatizado de coleta,
3. medicao CK de 1 repositorio com metricas agregadas em CSV.

O ambiente esta pronto para evolucao para a Sprint S02.
