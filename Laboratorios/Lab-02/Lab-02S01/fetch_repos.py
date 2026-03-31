"""
Lab-02S01: Coleta dos top-1000 repositórios Java via GitHub GraphQL API.

Saídas:
- data/repos_1000.json
- data/repos_1000.csv
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

GRAPHQL_URL = "https://api.github.com/graphql"
SCRIPT_DIR = Path(__file__).resolve().parent
QUERY_FILE = SCRIPT_DIR / "query.graphql"
DATA_DIR = SCRIPT_DIR / "data"
LOGS_DIR = SCRIPT_DIR / "logs"
OUTPUT_JSON = DATA_DIR / "repos_1000.json"
OUTPUT_CSV = DATA_DIR / "repos_1000.csv"
TIME_LOG = LOGS_DIR / "timing.log"


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
            key = key.strip()
            value = value.strip()
            if key:
                os.environ.setdefault(key, value)


@dataclass
class Settings:
    token: str
    target_repos: int = 1000
    page_size: int = 20
    timeout_secs: int = 90
    max_retries: int = 20



def _get_int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        parsed = int(value)
    except ValueError:
        print(f"Erro: variável {name} deve ser um inteiro.", file=sys.stderr)
        sys.exit(1)
    return parsed



def get_settings() -> Settings:
    load_env()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("Erro: defina GITHUB_TOKEN no ambiente ou em Lab-02S01/.env.", file=sys.stderr)
        sys.exit(1)

    settings = Settings(
        token=token,
        target_repos=_get_int_env("LAB02_TARGET_REPOS", 1000),
        page_size=_get_int_env("LAB02_PAGE_SIZE", 20),
        timeout_secs=_get_int_env("LAB02_TIMEOUT_SECS", 90),
        max_retries=_get_int_env("LAB02_MAX_RETRIES", 20),
    )

    if not (1 <= settings.page_size <= 100):
        print("Erro: LAB02_PAGE_SIZE deve estar entre 1 e 100.", file=sys.stderr)
        sys.exit(1)
    if settings.target_repos < 1:
        print("Erro: LAB02_TARGET_REPOS deve ser >= 1.", file=sys.stderr)
        sys.exit(1)
    if settings.max_retries < 1:
        print("Erro: LAB02_MAX_RETRIES deve ser >= 1.", file=sys.stderr)
        sys.exit(1)

    return settings



def read_query() -> str:
    if not QUERY_FILE.exists():
        print(f"Erro: arquivo ausente: {QUERY_FILE}", file=sys.stderr)
        sys.exit(1)
    return QUERY_FILE.read_text(encoding="utf-8")



def _age_years_from_created_at(created_at: str) -> float:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    years = (now - created).days / 365.25
    return round(years, 3)



def fetch_page(settings: Settings, query: str, cursor: str | None) -> dict[str, Any]:
    query_string = "language:Java sort:stars-desc"
    payload = {
        "query": query,
        "variables": {
            "queryString": query_string,
            "first": settings.page_size,
            "cursor": cursor,
        },
    }
    headers = {
        "Authorization": f"Bearer {settings.token}",
        "Content-Type": "application/json",
        "User-Agent": "lab-experimentacao-github-api",
    }

    transient_statuses = {429, 502, 503, 504}

    for attempt in range(settings.max_retries):
        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=settings.timeout_secs,
        )

        if response.status_code in transient_statuses and attempt < settings.max_retries - 1:
            sleep_secs = min(60, 2 ** attempt)
            print(
                f"Aviso: HTTP {response.status_code}. Tentando novamente em {sleep_secs}s..."
            )
            time.sleep(sleep_secs)
            continue

        if response.status_code != 200:
            print(f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr)
            sys.exit(1)

        data = response.json()
        if "errors" in data:
            print("Erro GraphQL:", json.dumps(data["errors"], indent=2), file=sys.stderr)
            sys.exit(1)

        return data

    print("Erro: limite de tentativas atingido.", file=sys.stderr)
    sys.exit(1)



def normalize_repositories(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for repo in nodes:
        if not isinstance(repo, dict):
            continue
        if not repo.get("nameWithOwner") or not repo.get("createdAt"):
            continue

        created_at = str(repo.get("createdAt"))

        releases = repo.get("releases") or {}
        primary_language = repo.get("primaryLanguage") or {}

        row = {
            "name": repo.get("name"),
            "name_with_owner": repo.get("nameWithOwner"),
            "url": repo.get("url"),
            "stargazers": int(repo.get("stargazerCount", 0) or 0),
            "created_at": created_at,
            "updated_at": repo.get("pushedAt"),
            "age_years": _age_years_from_created_at(created_at),
            "releases_count": int(releases.get("totalCount", 0) or 0),
            "primary_language": primary_language.get("name"),
        }
        rows.append(row)

    # Garantia adicional de ordenação por popularidade.
    rows.sort(key=lambda item: item["stargazers"], reverse=True)
    return rows



def write_outputs(rows: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "repositories": rows,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    fieldnames = [
        "name",
        "name_with_owner",
        "url",
        "stargazers",
        "created_at",
        "updated_at",
        "age_years",
        "releases_count",
        "primary_language",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def log_timing(label: str, start: float, end: float) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    elapsed = end - start
    stamp = datetime.now(timezone.utc).isoformat()
    with TIME_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{stamp}] {label}: {elapsed:.2f}s\n")



def main() -> None:
    t0 = time.perf_counter()
    settings = get_settings()
    query = read_query()

    print(f"Coletando {settings.target_repos} repositórios Java...")

    all_nodes: list[dict[str, Any]] = []
    cursor: str | None = None
    has_next = True

    while has_next and len(all_nodes) < settings.target_repos:
        page = fetch_page(settings, query, cursor)
        search = page.get("data", {}).get("search", {})

        nodes = search.get("nodes", []) or []
        page_info = search.get("pageInfo", {})
        has_next = bool(page_info.get("hasNextPage"))
        cursor = page_info.get("endCursor")

        all_nodes.extend([node for node in nodes if isinstance(node, dict)])
        print(f"- coletados: {len(all_nodes)}")

    normalized = normalize_repositories(all_nodes)
    normalized = normalized[: settings.target_repos]

    write_outputs(normalized)

    print("Concluído.")
    print(f"JSON: {OUTPUT_JSON}")
    print(f"CSV : {OUTPUT_CSV}")
    t1 = time.perf_counter()
    log_timing("fetch_repos", t0, t1)


if __name__ == "__main__":
    main()
