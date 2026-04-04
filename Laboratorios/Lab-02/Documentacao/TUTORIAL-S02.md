# Tutorial de Execucao - Sprint S02

Este tutorial descreve **os comandos** e **as funcionalidades implementadas** para a Sprint S02.
Use no WSL (bash) ou ajuste os comandos para PowerShell.

---

## 1. Objetivo da S02

Consolidar as métricas de qualidade (CBO, DIT, LCOM) para os repositórios Java,
limpar os dados e gerar estatísticas descritivas e correlações preliminares.

---

## 2. Pré-requisitos

- Python 3.9+
- Java (JDK/JRE) disponível no PATH
- CK gerado localmente (jar)
- `cloc` instalado (opcional, mas recomendado)

### 2.1 Verificações rápidas

```bash
java -version
cloc --version
```

### 2.2 Variáveis obrigatórias

No arquivo `.env` da S02 (ou via `export`):

```
CK_JAR_PATH=/home/user/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar
```

---

## 3. Comandos principais

### 3.1 Coleta em lote (S02)

```bash
cd /home/m3001/LabExp_02/LabMedExp/Laboratorios/Lab-02/Lab-02S02
python ./collect_metrics_batch.py
```

**O que faz:**  
- Clona repositórios (shallow clone)  
- Executa CK para CBO/DIT/LCOM  
- Executa `cloc` para LOC e comentários  
- Salva `data/metrics_all_1000_repos.csv`  
- Registra logs em `logs/collection_log.txt`

### 3.2 Validação/limpeza do CSV

```bash
python ./validate_data.py
```

**O que faz:**  
Remove linhas inválidas e gera:
`data/metrics_all_1000_repos_cleaned.csv`

### 3.3 Estatísticas descritivas e correlação preliminar

```bash
python ./summarize_statistics.py
```

**Gera:**
- `data/summary_statistics.txt`
- `data/correlation_matrix.csv`
- `logs/timing_summary.txt` (se o pipeline completo foi executado)

---

## 4. Execução em teste (poucos repositórios)

Para validar rapidamente:

```bash
export LAB02_MAX_REPOS=5
python ./collect_metrics_batch.py
unset LAB02_MAX_REPOS
```

---

## 5. Retry de repositórios faltantes

Se alguns repos falharem:

```bash
python ./collect_metrics_retry_failed.py
```

**O que faz:**  
Lê `/tmp/repos_faltantes.txt` e tenta apenas os repos faltantes.

---

## 6. Principais arquivos gerados

- `data/metrics_all_1000_repos.csv`
- `data/metrics_all_1000_repos_cleaned.csv`
- `data/summary_statistics.txt`
- `data/correlation_matrix.csv`
- `logs/collection_log.txt`
- `logs/timing.log`

---

## 7. Observações importantes

- Se `cloc` não estiver instalado, o script continua, mas `loc` e `comment_lines`
  ficam vazios.
- Se o CK não gerar `class.csv`, o repositório é registrado como FAIL.
- Atualmente a amostra válida ficou com **972 repositórios** (28 falharam).

---

## 8. Próximos passos (S03)

Para análise final e gráficos:

```bash
cd ../Lab-02S03
python ./analyze_correlations.py
python ./generate_plots.py
python ./validate_statistics.py
```

**Gráficos adicionais incluídos (RQ04):**
- `figs/RQ04_scatter_comments_vs_cbo_2026-04-03.png`
- `figs/RQ04_scatter_comments_vs_dit_2026-04-03.png`
- `figs/RQ04_scatter_comments_vs_lcom_2026-04-03.png`
