"""
Lab-02S02: estatísticas descritivas e correlação preliminar.

Entrada: data/metrics_all_1000_repos_cleaned.csv
Saídas:
- data/summary_statistics.txt
- data/correlation_matrix.csv
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
import time
from pathlib import Path

S02_DIR = Path(__file__).resolve().parent
DATA_DIR = S02_DIR / "data"
LOGS_DIR = S02_DIR / "logs"
INPUT_CSV = DATA_DIR / "metrics_all_1000_repos_cleaned.csv"
SUMMARY_TXT = DATA_DIR / "summary_statistics.txt"
CORR_CSV = DATA_DIR / "correlation_matrix.csv"
TIME_LOG = LOGS_DIR / "timing.log"
TIME_SUMMARY = LOGS_DIR / "timing_summary.txt"

METRICS = [
    "cbo_mean",
    "dit_mean",
    "lcom_mean",
]

PROCESS = [
    "stargazers",
    "releases_count",
    "loc",
    "comment_lines",
]


def _to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def _quantiles(values: list[float]) -> tuple[float, float, float]:
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return q1, q2, q3

def write_timing_summary() -> None:
    if not TIME_LOG.exists():
        return

    lines = TIME_LOG.read_text(encoding="utf-8").splitlines()
    start_idx = 0
    for idx, line in enumerate(lines):
        if "PIPELINE_START" in line:
            start_idx = idx + 1

    durations: list[tuple[str, float]] = []
    for line in lines[start_idx:]:
        if ":" not in line or "s" not in line:
            continue
        try:
            label_part = line.split("]", 1)[1].strip()
            label, value_part = label_part.split(":", 1)
            value = float(value_part.strip().rstrip("s"))
            durations.append((label.strip(), value))
        except (ValueError, IndexError):
            continue

    if not durations:
        return

    total = sum(value for _, value in durations)
    output = ["Resumo de tempos (ultima execucao):", ""]
    for label, value in durations:
        output.append(f"- {label}: {value:.2f}s")
    output.append("")
    output.append(f"Total pipeline: {total:.2f}s")
    TIME_SUMMARY.write_text("\n".join(output), encoding="utf-8")


def main() -> None:
    t0 = time.perf_counter()
    if not INPUT_CSV.exists():
        print(f"Erro: arquivo não encontrado: {INPUT_CSV}", file=sys.stderr)
        sys.exit(1)

    data: dict[str, list[float]] = {m: [] for m in METRICS + PROCESS}

    with INPUT_CSV.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in data:
                value = _to_float(row.get(key))
                if value is not None:
                    data[key].append(value)

    lines: list[str] = []
    lines.append("Resumo estatístico (amostra limpa)")
    lines.append("")
    for key, values in data.items():
        if not values:
            continue
        values_sorted = sorted(values)
        q1, q2, q3 = _quantiles(values_sorted)
        lines.append(f"{key}:")
        lines.append(f"  n={len(values_sorted)}")
        lines.append(f"  media={statistics.fmean(values_sorted):.4f}")
        lines.append(f"  mediana={statistics.median(values_sorted):.4f}")
        lines.append(f"  desvio={statistics.pstdev(values_sorted):.4f}")
        lines.append(f"  min={values_sorted[0]:.4f}")
        lines.append(f"  q1={q1:.4f}")
        lines.append(f"  q3={q3:.4f}")
        lines.append(f"  max={values_sorted[-1]:.4f}")
        lines.append("")

    SUMMARY_TXT.write_text("\n".join(lines), encoding="utf-8")

    # Correlação preliminar: métricas de processo vs. qualidade
    rows = []
    header = ["process_metric"] + METRICS
    rows.append(header)

    for p in PROCESS:
        row = [p]
        for m in METRICS:
            xs = data.get(p, [])
            ys = data.get(m, [])
            n = min(len(xs), len(ys))
            corr = _pearson(xs[:n], ys[:n])
            row.append("" if corr is None else f"{corr:.4f}")
        rows.append(row)

    with CORR_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Resumo: {SUMMARY_TXT}")
    print(f"Correlação: {CORR_CSV}")
    t1 = time.perf_counter()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with TIME_LOG.open("a", encoding="utf-8") as file:
        file.write(
            f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] summarize_statistics: {t1 - t0:.2f}s\n"
        )
    write_timing_summary()


if __name__ == "__main__":
    main()
