"""
Lab-02S03: gera graficos de correlacao e distribuicao.

Entradas:
- ../Lab-02S02/data/metrics_all_1000_repos_cleaned.csv

Saidas:
- figs/ (scatter plots + heatmap + boxplots)
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

S03_DIR = Path(__file__).resolve().parent
S02_DIR = S03_DIR.parent / "Lab-02S02"
INPUT_CSV = S02_DIR / "data" / "metrics_all_1000_repos_cleaned.csv"

FIGS_DIR = S03_DIR / "figs"
FIGS_DIR.mkdir(parents=True, exist_ok=True)


def save_scatter(df: pd.DataFrame, x: str, y: str, filename: str) -> None:
    plt.figure(figsize=(6, 4))
    sns.regplot(data=df, x=x, y=y, scatter_kws={"s": 10, "alpha": 0.4}, line_kws={"color": "red"})
    plt.tight_layout()
    plt.savefig(FIGS_DIR / filename, dpi=150)
    plt.close()


def main() -> None:
    # Evita erro de cache do matplotlib em FS somente leitura
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
    if not INPUT_CSV.exists():
        raise SystemExit(f"Arquivo não encontrado: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    if "age_years" not in df.columns and "created_at" in df.columns:
        def _age_years(ts: str) -> float:
            try:
                created = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                return round((now - created).days / 365.25, 4)
            except Exception:
                return float("nan")

        df["age_years"] = df["created_at"].apply(_age_years)

    # Scatter plots por RQ
    save_scatter(df, "stargazers", "cbo_mean", "RQ01_scatter_stars_vs_cbo.png")
    save_scatter(df, "stargazers", "dit_mean", "RQ01_scatter_stars_vs_dit.png")
    save_scatter(df, "stargazers", "lcom_mean", "RQ01_scatter_stars_vs_lcom.png")

    save_scatter(df, "age_years", "cbo_mean", "RQ02_scatter_age_vs_cbo.png")
    save_scatter(df, "age_years", "dit_mean", "RQ02_scatter_age_vs_dit.png")
    save_scatter(df, "age_years", "lcom_mean", "RQ02_scatter_age_vs_lcom.png")

    save_scatter(df, "releases_count", "cbo_mean", "RQ03_scatter_releases_vs_cbo.png")
    save_scatter(df, "releases_count", "dit_mean", "RQ03_scatter_releases_vs_dit.png")
    save_scatter(df, "releases_count", "lcom_mean", "RQ03_scatter_releases_vs_lcom.png")

    save_scatter(df, "loc", "cbo_mean", "RQ04_scatter_loc_vs_cbo.png")
    save_scatter(df, "loc", "dit_mean", "RQ04_scatter_loc_vs_dit.png")
    save_scatter(df, "loc", "lcom_mean", "RQ04_scatter_loc_vs_lcom.png")

    # Heatmap de correlacao geral
    corr = df[["stargazers", "age_years", "releases_count", "loc", "comment_lines",
               "cbo_mean", "dit_mean", "lcom_mean"]].corr(numeric_only=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, cmap="coolwarm", annot=False)
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "correlation_heatmap.png", dpi=150)
    plt.close()

    # Boxplots de distribuicao
    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df[["cbo_mean", "dit_mean", "lcom_mean"]])
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "distribution_boxplots.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()
