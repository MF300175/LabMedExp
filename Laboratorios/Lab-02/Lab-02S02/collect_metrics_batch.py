"""
Lab-02S02: coleta em lote das métricas de qualidade (CK) e tamanho (cloc).

Fluxo:
1) Lê ../Lab-02S01/data/repos_1000.csv
2) Para cada repositório: clone → CK → cloc → sumariza métricas
3) Salva data/metrics_all_1000_repos.csv
4) Registra sucessos/falhas em logs/collection_log.txt
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import stat
import statistics
import subprocess
import sys
import time
import shutil as _shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
S01_DIR = ROOT_DIR / "Lab-02S01"
S02_DIR = Path(__file__).resolve().parent

INPUT_REPOS_CSV = S01_DIR / "data" / "repos_1000.csv"
DATA_DIR = S02_DIR / "data"
LOGS_DIR = S02_DIR / "logs"
OUTPUT_CSV = DATA_DIR / "metrics_all_1000_repos.csv"
LOG_FILE = LOGS_DIR / "collection_log.txt"
TIME_LOG = LOGS_DIR / "timing.log"
TIME_SUMMARY = LOGS_DIR / "timing_summary.txt"
TEMP_DIR = S02_DIR / "temp"
CK_OUTPUT_DIR = DATA_DIR / "ck_output"


@dataclass
class RepoInfo:
    name_with_owner: str
    url: str
    stargazers: int
    created_at: str
    releases_count: int


def load_env() -> None:
    candidate_paths = [S02_DIR / ".env", *[parent / ".env" for parent in S02_DIR.parents]]
    for path in candidate_paths:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _handle_remove_readonly(func, path, exc_info) -> None:
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


def run_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True)


def read_repos() -> list[RepoInfo]:
    if not INPUT_REPOS_CSV.exists():
        print(f"Erro: arquivo não encontrado: {INPUT_REPOS_CSV}", file=sys.stderr)
        sys.exit(1)
    repos: list[RepoInfo] = []
    with INPUT_REPOS_CSV.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            repos.append(
                RepoInfo(
                    name_with_owner=row["name_with_owner"],
                    url=row["url"],
                    stargazers=int(row["stargazers"]),
                    created_at=row["created_at"],
                    releases_count=int(row["releases_count"]),
                )
            )
    return repos


def clone_repository(repo: RepoInfo, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    repo_dir = destination / repo.name_with_owner.replace("/", "__")
    if repo_dir.exists():
        safe_rmtree(repo_dir)
    result = run_command(["git", "clone", "--depth", "1", repo.url, str(repo_dir)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return repo_dir


def run_ck(repo_dir: Path, ck_output_dir: Path) -> Path:
    load_env()
    ck_jar = os.environ.get("CK_JAR_PATH", "").strip()
    if not ck_jar:
        raise RuntimeError("CK_JAR_PATH não definido.")
    if not Path(ck_jar).exists():
        raise RuntimeError(f"CK_JAR_PATH inválido: {ck_jar}")

    ck_output_dir.mkdir(parents=True, exist_ok=True)
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
    result = run_command(command)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    class_csv = ck_output_dir / "class.csv"
    if not class_csv.exists():
        raise RuntimeError("class.csv não encontrado após CK.")
    return class_csv


def run_cloc(repo_dir: Path) -> tuple[int | None, int | None]:
    result = run_command(["cloc", "--json", str(repo_dir)])
    if result.returncode != 0:
        return None, None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, None
    summary = data.get("SUM", {})
    loc = summary.get("code")
    comments = summary.get("comment")
    if loc is None or comments is None:
        return None, None
    return int(loc), int(comments)


def _to_float(value: str | float | None) -> float:
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
            cbos.append(_to_float(row.get("cbo")))
            dits.append(_to_float(row.get("dit")))
            lcoms.append(_to_float(row.get("lcom")))

    if not cbos:
        raise RuntimeError("class.csv sem linhas para sumarização.")

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


def read_processed(output_csv: Path) -> set[str]:
    if not output_csv.exists():
        return set()
    processed: set[str] = set()
    with output_csv.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            processed.add(row.get("repository", ""))
    return processed


def append_row(output_csv: Path, row: dict[str, object]) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    exists = output_csv.exists()
    fieldnames = list(row.keys())
    with output_csv.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def log_line(message: str) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    LOG_FILE.write_text("", encoding="utf-8") if not LOG_FILE.exists() else None
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")

def log_timing(label: str, start: float, end: float) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    elapsed = end - start
    stamp = datetime.now().isoformat(timespec="seconds")
    with TIME_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{stamp}] {label}: {elapsed:.2f}s\n")

def log_pipeline_start() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    with TIME_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{stamp}] PIPELINE_START\n")
    TIME_SUMMARY.write_text("", encoding="utf-8")


def main() -> None:
    log_pipeline_start()
    t0 = time.perf_counter()
    if _shutil.which("java") is None:
        print("Erro: comando 'java' não encontrado no PATH.", file=sys.stderr)
        print("Instale o JRE/JDK ou ajuste o PATH antes de continuar.", file=sys.stderr)
        sys.exit(1)
    load_env()
    ck_jar = os.environ.get("CK_JAR_PATH", "").strip()
    if not ck_jar:
        print("Erro: CK_JAR_PATH não definido. Configure no .env ou exporte a variável.", file=sys.stderr)
        sys.exit(1)
    if not Path(ck_jar).exists():
        print(f"Erro: CK_JAR_PATH inválido: {ck_jar}", file=sys.stderr)
        sys.exit(1)
    repos = read_repos()
    processed = read_processed(OUTPUT_CSV)

    print(f"Repos totais: {len(repos)}")
    print(f"Repos já processados: {len(processed)}")

    for repo in repos:
        if repo.name_with_owner in processed:
            continue

        print(f"Processando {repo.name_with_owner}...")
        try:
            repo_dir = clone_repository(repo, TEMP_DIR)
            class_csv = run_ck(repo_dir, CK_OUTPUT_DIR)
            metrics = summarize_ck_metrics(class_csv)
            loc, comments = run_cloc(repo_dir)

            row = {
                "repository": repo.name_with_owner,
                "url": repo.url,
                "stargazers": repo.stargazers,
                "created_at": repo.created_at,
                "releases_count": repo.releases_count,
                "loc": loc if loc is not None else "",
                "comment_lines": comments if comments is not None else "",
                **metrics,
            }
            append_row(OUTPUT_CSV, row)
            log_line(f"OK: {repo.name_with_owner}")
        except Exception as exc:  # noqa: BLE001
            log_line(f"FAIL: {repo.name_with_owner} - {exc}")
        finally:
            if TEMP_DIR.exists():
                safe_rmtree(TEMP_DIR)

    print("Concluído.")
    print(f"Saída: {OUTPUT_CSV}")
    print(f"Log: {LOG_FILE}")
    t1 = time.perf_counter()
    log_timing("collect_metrics_batch", t0, t1)


if __name__ == "__main__":
    main()
