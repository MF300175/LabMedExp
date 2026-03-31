"""
Lab-02S02: validação e limpeza de dados.

Entrada: data/metrics_all_1000_repos.csv
Saída : data/metrics_all_1000_repos_cleaned.csv
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

S02_DIR = Path(__file__).resolve().parent
DATA_DIR = S02_DIR / "data"
LOGS_DIR = S02_DIR / "logs"
INPUT_CSV = DATA_DIR / "metrics_all_1000_repos.csv"
OUTPUT_CSV = DATA_DIR / "metrics_all_1000_repos_cleaned.csv"
TIME_LOG = LOGS_DIR / "timing.log"

ESSENTIAL_FIELDS = [
    "repository",
    "url",
    "stargazers",
    "created_at",
    "releases_count",
    "cbo_mean",
    "dit_mean",
    "lcom_mean",
]


def _to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _to_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def main() -> None:
    t0 = time.perf_counter()
    if not INPUT_CSV.exists():
        print(f"Erro: arquivo não encontrado: {INPUT_CSV}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    kept = 0
    seen: set[str] = set()

    with INPUT_CSV.open("r", encoding="utf-8") as infile, OUTPUT_CSV.open(
        "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            print("Erro: CSV sem cabeçalho.", file=sys.stderr)
            sys.exit(1)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1

            if any(not row.get(field) for field in ESSENTIAL_FIELDS):
                continue

            repo = row.get("repository", "")
            if repo in seen:
                continue

            # Validações básicas de faixa
            cbo = _to_float(row.get("cbo_mean"))
            dit = _to_float(row.get("dit_mean"))
            lcom = _to_float(row.get("lcom_mean"))
            if cbo is None or cbo < 0:
                continue
            if dit is None or dit < 0:
                continue
            if lcom is None or lcom < 0:
                continue

            # Campos numéricos opcionais
            row["stargazers"] = _to_int(row.get("stargazers")) or 0
            row["releases_count"] = _to_int(row.get("releases_count")) or 0

            writer.writerow(row)
            seen.add(repo)
            kept += 1

    print(f"Total de linhas: {total}")
    print(f"Linhas mantidas: {kept}")
    print(f"CSV limpo: {OUTPUT_CSV}")
    t1 = time.perf_counter()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with TIME_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] validate_data: {t1 - t0:.2f}s\n")


if __name__ == "__main__":
    main()
