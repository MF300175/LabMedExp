"""
Lab-02S03: testes estatisticos auxiliares.

- Normalidade (Shapiro-Wilk) para algumas metricas
- Spearman como confirmacao nao-parametrica
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from scipy import stats

S03_DIR = Path(__file__).resolve().parent
S02_DIR = S03_DIR.parent / "Lab-02S02"
INPUT_CSV = S02_DIR / "data" / "metrics_all_1000_repos_cleaned.csv"

DATA_DIR = S03_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
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

    lines = ["Validacao estatistica (Shapiro-Wilk + Spearman)", ""]

    for col in ["cbo_mean", "dit_mean", "lcom_mean", "stargazers", "loc", "comment_lines"]:
        series = df[col].dropna()
        if len(series) > 5000:
            series = series.sample(5000, random_state=42)
        stat, p = stats.shapiro(series)
        lines.append(f"Shapiro {col}: W={stat:.4f}, p={p:.4g} (n={len(series)})")

    # Exemplo Spearman global entre processo e qualidade
    for proc in ["stargazers", "age_years", "releases_count", "loc", "comment_lines"]:
        for qual in ["cbo_mean", "dit_mean", "lcom_mean"]:
            sub = df[[proc, qual]].dropna()
            if len(sub) < 3:
                continue
            r, p = stats.spearmanr(sub[proc], sub[qual])
            lines.append(f"Spearman {proc} vs {qual}: r={r:.4f}, p={p:.4g}, n={len(sub)}")

    (DATA_DIR / "VALIDACAO-ESTATISTICA.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
