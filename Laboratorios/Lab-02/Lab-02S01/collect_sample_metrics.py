"""
Lab-02S01: pipeline de prova de conceito para 1 repositório.

Fluxo:
1) Lê data/repos_1000.csv
2) Faz clone do repositório selecionado
3) Executa CK
4) Agrega CBO/DIT/LCOM (média, mediana, desvio padrão)
5) Salva data/sample_metrics.csv
"""

from __future__ import annotations

import csv
import os
import shutil
import stat
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
LOGS_DIR = SCRIPT_DIR / "logs"
TEMP_DIR = SCRIPT_DIR / "temp"
INPUT_REPOS_CSV = DATA_DIR / "repos_1000.csv"
OUTPUT_SAMPLE_CSV = DATA_DIR / "sample_metrics.csv"
CK_OUTPUT_DIR = DATA_DIR / "ck_output"
TIME_LOG = LOGS_DIR / "timing.log"


@dataclass
class RepoInfo:
    name_with_owner: str
    url: str
    stargazers: int
    age_years: float
    releases_count: int



def load_env() -> None:
    candidate_paths = [SCRIPT_DIR / ".env", *[parent / ".env" for parent in SCRIPT_DIR.parents]]

    for path in candidate_paths:
        if not path.exists():
            continue

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())



def read_first_repo() -> RepoInfo:
    if not INPUT_REPOS_CSV.exists():
        print(
            f"Erro: arquivo {INPUT_REPOS_CSV} não encontrado. Rode fetch_repos.py primeiro.",
            file=sys.stderr,
        )
        sys.exit(1)

    with INPUT_REPOS_CSV.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        first = next(reader, None)

    if not first:
        print("Erro: repos_1000.csv está vazio.", file=sys.stderr)
        sys.exit(1)

    return RepoInfo(
        name_with_owner=first["name_with_owner"],
        url=first["url"],
        stargazers=int(first["stargazers"]),
        age_years=float(first["age_years"]),
        releases_count=int(first["releases_count"]),
    )



def run_command(command: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Erro ao executar comando:", " ".join(command), file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


def _handle_remove_readonly(func, path, exc_info) -> None:
    # On Windows, git pack files can be marked read-only.
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def safe_rmtree(path: Path, retries: int = 5, delay_secs: float = 1.5) -> None:
    if not path.exists():
        return

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            shutil.rmtree(path, onexc=_handle_remove_readonly)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(delay_secs * attempt)

    print(f"Aviso: não foi possível remover {path}: {last_error}", file=sys.stderr)



def clone_repository(repo: RepoInfo, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    repo_dir = destination / repo.name_with_owner.replace("/", "__")

    if repo_dir.exists():
        safe_rmtree(repo_dir)

    run_command(["git", "clone", "--depth", "1", repo.url, str(repo_dir)])
    return repo_dir



def run_ck(repo_dir: Path, ck_output_dir: Path) -> Path:
    load_env()
    ck_jar = os.environ.get("CK_JAR_PATH", "").strip()
    if not ck_jar:
        print(
            "Erro: defina CK_JAR_PATH no ambiente ou em Lab-02S01/.env para executar o CK.",
            file=sys.stderr,
        )
        sys.exit(1)

    ck_output_dir.mkdir(parents=True, exist_ok=True)

    # CK CLI: java -jar <jar> <projectPath> <useJars> <maxFiles> <useLambdas> <outputDir>
    command = [
        "java",
        "-jar",
        ck_jar,
        str(repo_dir),
        "false",
        "0",
        "false",
        str(ck_output_dir),
    ]
    run_command(command)

    class_csv = ck_output_dir / "class.csv"
    if not class_csv.exists():
        print(
            f"Erro: class.csv não encontrado em {ck_output_dir}. Verifique versão/parâmetros do CK.",
            file=sys.stderr,
        )
        sys.exit(1)
    return class_csv



def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0



def _std_or_zero(values: Iterable[float]) -> float:
    seq = list(values)
    if len(seq) < 2:
        return 0.0
    return statistics.pstdev(seq)



def summarize_ck_metrics(class_csv: Path) -> dict[str, float]:
    cbos: list[float] = []
    dits: list[float] = []
    lcoms: list[float] = []

    with class_csv.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cbos.append(_to_float(row.get("cbo", "0")))
            dits.append(_to_float(row.get("dit", "0")))
            lcoms.append(_to_float(row.get("lcom", "0")))

    if not cbos:
        print("Erro: class.csv sem linhas para sumarização.", file=sys.stderr)
        sys.exit(1)

    return {
        "cbo_mean": round(statistics.fmean(cbos), 4),
        "cbo_median": round(statistics.median(cbos), 4),
        "cbo_std": round(_std_or_zero(cbos), 4),
        "dit_mean": round(statistics.fmean(dits), 4),
        "dit_median": round(statistics.median(dits), 4),
        "dit_std": round(_std_or_zero(dits), 4),
        "lcom_mean": round(statistics.fmean(lcoms), 4),
        "lcom_median": round(statistics.median(lcoms), 4),
        "lcom_std": round(_std_or_zero(lcoms), 4),
        "classes_count": len(cbos),
    }



def write_sample_metrics(repo: RepoInfo, metrics: dict[str, float]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    row = {
        "repository": repo.name_with_owner,
        "url": repo.url,
        "stargazers": repo.stargazers,
        "age_years": repo.age_years,
        "releases_count": repo.releases_count,
        **metrics,
    }

    fieldnames = list(row.keys())
    with OUTPUT_SAMPLE_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)

def log_timing(label: str, start: float, end: float) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    elapsed = end - start
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    with TIME_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{stamp}] {label}: {elapsed:.2f}s\n")



def main() -> None:
    t0 = time.perf_counter()
    repo = read_first_repo()
    print(f"Repositório de amostra: {repo.name_with_owner}")

    repo_dir = clone_repository(repo, TEMP_DIR)
    class_csv = run_ck(repo_dir, CK_OUTPUT_DIR)
    metrics = summarize_ck_metrics(class_csv)
    write_sample_metrics(repo, metrics)

    # Limpa clone local após medição para economizar espaço.
    if repo_dir.exists():
        safe_rmtree(repo_dir)

    print("Concluído.")
    print(f"Saída: {OUTPUT_SAMPLE_CSV}")
    t1 = time.perf_counter()
    log_timing("collect_sample_metrics", t0, t1)


if __name__ == "__main__":
    main()
