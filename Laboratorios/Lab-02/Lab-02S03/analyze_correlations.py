"""
Lab-02S03: correlacoes Pearson e Spearman por RQ.

Entradas:
- ../Lab-02S02/data/metrics_all_1000_repos_cleaned.csv

Saidas:
- data/RQ01_correlacao_popularidade.csv
- data/RQ02_correlacao_maturidade.csv
- data/RQ03_correlacao_atividade.csv
- data/RQ04_correlacao_tamanho.csv
- data/statistical_summary.txt
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from scipy import stats

S03_DIR = Path(__file__).resolve().parent
S02_DIR = S03_DIR.parent / "Lab-02S02"
INPUT_CSV = S02_DIR / "data" / "metrics_all_1000_repos_cleaned.csv"

DATA_DIR = S03_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _pair_corr(df: pd.DataFrame, x: str, y: str) -> dict[str, float]:
    series = df[[x, y]].dropna()
    if series.empty or len(series) < 3:
        return {"n": 0, "pearson_r": float("nan"), "pearson_p": float("nan"),
                "spearman_r": float("nan"), "spearman_p": float("nan")}

    pearson_r, pearson_p = stats.pearsonr(series[x], series[y])
    spearman_r, spearman_p = stats.spearmanr(series[x], series[y])
    return {
        "n": int(len(series)),
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_r": spearman_r,
        "spearman_p": spearman_p,
    }


def analyze_rq(df: pd.DataFrame, process_cols: str | list[str], out_name: str) -> None:
    rows = []
    if isinstance(process_cols, str):
        process_cols = [process_cols]
    for process_col in process_cols:
        for metric in ["cbo_mean", "dit_mean", "lcom_mean"]:
            corr = _pair_corr(df, process_col, metric)
            rows.append(
                {
                    "process_metric": process_col,
                    "quality_metric": metric,
                    **corr,
                }
            )
    out_path = DATA_DIR / out_name
    pd.DataFrame(rows).to_csv(out_path, index=False)


def main() -> None:
    if not INPUT_CSV.exists():
        raise SystemExit(f"Arquivo não encontrado: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    # Garante age_years para RQ02. Se não existir, calcula via created_at.
    if "age_years" not in df.columns and "created_at" in df.columns:
        def _age_years(ts: str) -> float:
            try:
                created = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                return round((now - created).days / 365.25, 4)
            except Exception:
                return float("nan")

        df["age_years"] = df["created_at"].apply(_age_years)

    analyze_rq(df, "stargazers", "RQ01_correlacao_popularidade.csv")
    analyze_rq(df, "age_years", "RQ02_correlacao_maturidade.csv")
    analyze_rq(df, "releases_count", "RQ03_correlacao_atividade.csv")
    analyze_rq(df, ["loc", "comment_lines"], "RQ04_correlacao_tamanho.csv")

    # Resumo geral
    summary_lines = [
        "Resumo estatistico - correlacoes (Pearson/Spearman)",
        f"n_total={len(df)}",
        "",
        "Arquivos gerados:",
        "- RQ01_correlacao_popularidade.csv",
        "- RQ02_correlacao_maturidade.csv",
        "- RQ03_correlacao_atividade.csv",
        "- RQ04_correlacao_tamanho.csv",
    ]
    (DATA_DIR / "statistical_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
