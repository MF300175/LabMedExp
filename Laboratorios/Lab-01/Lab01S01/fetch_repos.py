"""
Lab 01 – Coleta de repositórios via GitHub GraphQL API (script próprio).

Processo de Desenvolvimento (enunciado):
  Lab01S01: Consulta GraphQL para 100 repositórios (dados/métricas das RQs) + requisição automática (3 pts)
  Lab01S02: Paginação (1000 repositórios) + dados em .csv + primeira versão do relatório (3 pts)
  Lab01S03: Análise e visualização + relatório final (9 pts)

Uso: python fetch_repos.py
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

import requests

GRAPHQL_URL = "https://api.github.com/graphql"
SCRIPT_DIR = Path(__file__).resolve().parent
QUERY_FILE = SCRIPT_DIR / "query.graphql"
DATA_DIR = SCRIPT_DIR / "data"
S01_OUTPUT_JSON = DATA_DIR / "repos_s01_100.json"
S01_OUTPUT_PREFIX = "repos_s01_100_"

DEFAULT_TARGET_REPOS = 100
DEFAULT_PAGE_SIZE = 10
DEFAULT_MAX_RETRIES = 8
DEFAULT_TIMEOUT_SECS = 30


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _timestamp_for_filename() -> str:
    """Timestamp local para nomes de arquivo (formato seguro para Windows)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _validate_required_fields(repos: list[dict]) -> None:
    """Valida (de forma leve) se os campos necessários para RQ01–RQ06 existem."""
    required_top_level = {
        "name",
        "nameWithOwner",
        "url",
        "createdAt",  # RQ01
        "pushedAt",  # RQ04
        "primaryLanguage",  # RQ05
        "pullRequests",  # RQ02
        "releases",  # RQ03
        "issues",  # RQ06 (total)
        "issuesClosed",  # RQ06 (closed)
    }

    missing_any = 0
    for repo in repos:
        missing = [k for k in required_top_level if k not in repo]
        if missing:
            missing_any += 1
            continue

        # valida subcampos mais críticos
        if repo.get("primaryLanguage") is not None and not isinstance(repo.get("primaryLanguage"), dict):
            missing_any += 1
            continue

        for conn_key in ("pullRequests", "releases", "issues", "issuesClosed"):
            conn = repo.get(conn_key)
            if not isinstance(conn, dict) or "totalCount" not in conn:
                missing_any += 1
                break

    if missing_any:
        print(
            f"Aviso: {missing_any} repositório(s) vieram sem todos os campos esperados. "
            "Isso pode indicar mudança na API, permissões do token ou inconsistência de rede.",
            file=sys.stderr,
        )


def load_env(path: Path | None = None) -> None:
    """Carrega variáveis do .env para os.environ (apenas GITHUB_TOKEN)."""
    if path is None:
        path = SCRIPT_DIR / ".env"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if key and value:
                    # Não sobrescreve variáveis já definidas no ambiente (ex.: definidas na sessão).
                    os.environ.setdefault(key, value)


def get_token() -> str:
    """Obtém GITHUB_TOKEN do ambiente (.env já carregado por load_env)."""
    load_env()
    token = os.environ.get("GITHUB_TOKEN")
    if not token or token == "seu_token_aqui":
        print("Erro: defina GITHUB_TOKEN no .env (copie de .env.example e preencha).", file=sys.stderr)
        sys.exit(1)
    return token


def read_query() -> str:
    """Lê o conteúdo de query.graphql."""
    if not QUERY_FILE.exists():
        print(f"Erro: arquivo não encontrado: {QUERY_FILE}", file=sys.stderr)
        sys.exit(1)
    return QUERY_FILE.read_text(encoding="utf-8")


def _get_int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        print(f"Erro: {name} deve ser um inteiro (recebido: {value!r}).", file=sys.stderr)
        sys.exit(1)


def fetch_page(
    token: str,
    query: str,
    cursor: str | None = None,
    first: int = 25,
    max_retries: int = 3,
) -> dict:
    """
    Envia uma página da busca GraphQL (Lab01S01/S02).
    Retorna o JSON da resposta. Faz retentativas em 502/503.
    """
    variables = {"cursor": cursor, "first": first}
    payload = {"query": query, "variables": variables}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "LabMedExp-Lab01",
    }

    transient_statuses = {502, 503, 504}
    debug = _env_flag("LAB01_DEBUG", default=False)

    for attempt in range(max_retries):
        resp = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=DEFAULT_TIMEOUT_SECS,
        )
        text = (resp.text or "").strip()
        if debug:
            print(f"  [debug] HTTP {resp.status_code}, corpo: {len(text)} chars", file=sys.stderr)

        if resp.status_code in transient_statuses:
            if attempt < max_retries - 1:
                # Backoff exponencial (cap em 60s) para erros transitórios.
                wait = min(60, 5 * (2**attempt))
                print(
                    f"  {resp.status_code} Gateway error. Nova tentativa em {wait}s ({attempt + 2}/{max_retries})...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            print(
                f"Erro: {resp.status_code} Gateway error (proxy/rede ou GitHub temporariamente indisponível).",
                file=sys.stderr,
            )
            print("Sugestão: tente outra rede, desative VPN/proxy ou execute mais tarde.", file=sys.stderr)
            if text and "<html" in text.lower():
                print(f"Corpo recebido (não é JSON): {text[:200]}...", file=sys.stderr)
            sys.exit(1)

        if not text:
            print(f"Erro: resposta vazia (HTTP {resp.status_code}).", file=sys.stderr)
            sys.exit(1)

        try:
            data = json.loads(text)
        except Exception as e:
            print(f"Erro: resposta não é JSON (HTTP {resp.status_code}): {e}", file=sys.stderr)
            print(f"Corpo (primeiros 500 chars): {text[:500]}", file=sys.stderr)
            if resp.status_code in transient_statuses:
                print(
                    f"{resp.status_code} costuma indicar proxy/firewall/instabilidade; tente outra rede ou mais tarde.",
                    file=sys.stderr,
                )
            sys.exit(1)
        break
    else:
        data = None  # não deve chegar aqui

    if data is None:
        sys.exit(1)

    if resp.status_code != 200:
        msg = data.get("message", resp.text)
        print(f"Erro HTTP {resp.status_code}: {msg}", file=sys.stderr)
        if resp.status_code == 403 and "rate limit" in str(msg).lower():
            print("Aguarde o rate limit ou use um token com maior cota.", file=sys.stderr)
        sys.exit(1)

    if "errors" in data:
        print("Erro GraphQL:", json.dumps(data["errors"], indent=2), file=sys.stderr)
        sys.exit(1)

    return data


def main() -> None:
    token = get_token()
    query = read_query()

    # Lab01S01: consulta GraphQL para 100 repositórios + requisição automática
    # Defaults ajustados para maior robustez em redes instáveis.
    # Você ainda pode sobrescrever via variáveis de ambiente.
    target_repos = _get_int_env("LAB01_TARGET_REPOS", DEFAULT_TARGET_REPOS)
    page_size = _get_int_env("LAB01_PAGE_SIZE", DEFAULT_PAGE_SIZE)
    max_retries = _get_int_env("LAB01_MAX_RETRIES", DEFAULT_MAX_RETRIES)

    if target_repos < 1:
        print("Erro: LAB01_TARGET_REPOS deve ser >= 1.", file=sys.stderr)
        sys.exit(1)
    if not (1 <= page_size <= 100):
        print("Erro: LAB01_PAGE_SIZE deve estar entre 1 e 100.", file=sys.stderr)
        sys.exit(1)
    if max_retries < 1:
        print("Erro: LAB01_MAX_RETRIES deve ser >= 1.", file=sys.stderr)
        sys.exit(1)

    print(f"Buscando {target_repos} repositórios em páginas de {page_size}...")

    all_nodes: list[dict] = []
    cursor: str | None = None
    has_next = True

    while has_next and len(all_nodes) < target_repos:
        data = fetch_page(token, query, cursor=cursor, first=page_size, max_retries=max_retries)

        search = data.get("data", {}).get("search", {})
        if not search:
            print("Resposta sem data.search.", file=sys.stderr)
            sys.exit(1)

        page_info = search.get("pageInfo", {})
        nodes = search.get("nodes", []) or []
        # filtra apenas dicts válidos
        page_nodes = [n for n in nodes if isinstance(n, dict) and n.get("name")]
        all_nodes.extend(page_nodes)

        cursor = page_info.get("endCursor")
        has_next = bool(page_info.get("hasNextPage")) and bool(cursor)

        print(f"  Acumulado: {min(len(all_nodes), target_repos)}/{target_repos}")

    nodes = all_nodes[:target_repos]
    repo_count = len(nodes)
    print(f"Total coletado: {repo_count}")

    _validate_required_fields(nodes)

    # Artefatos locais da etapa S01 (não versionados; salvar em data/)
    # - data/repos_s01_100.json: último resultado (sempre sobrescrito)
    # - data/repos_s01_100_<timestamp>.json: histórico de execuções (não sobrescrito)
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        latest_path = S01_OUTPUT_JSON
        timestamped_path = DATA_DIR / f"{S01_OUTPUT_PREFIX}{_timestamp_for_filename()}.json"

        payload = json.dumps(nodes, ensure_ascii=False, indent=2)
        latest_path.write_text(payload, encoding="utf-8")
        timestamped_path.write_text(payload, encoding="utf-8")

        print(f"Arquivo gerado (S01): {latest_path}")
        print(f"Arquivo gerado (S01 - histórico): {timestamped_path}")
    except Exception as e:
        print(f"Aviso: não foi possível salvar {S01_OUTPUT_JSON.name}: {e}", file=sys.stderr)

    if nodes and _env_flag("LAB01_SHOW_SAMPLE", default=False):
        first = nodes[0]
        if isinstance(first, dict) and first.get("name"):
            print("\nAmostra (primeiro repositório):")
            print(f"  name: {first.get('name')}")
            print(f"  nameWithOwner: {first.get('nameWithOwner')}")
            print(f"  createdAt: {first.get('createdAt')}")
            print(f"  pushedAt: {first.get('pushedAt')}")
            lang = first.get("primaryLanguage") or {}
            print(f"  primaryLanguage: {lang.get('name')}")
            print(f"  pullRequests.totalCount: {first.get('pullRequests', {}).get('totalCount')}")
            print(f"  releases.totalCount: {first.get('releases', {}).get('totalCount')}")
            print(f"  issues.totalCount: {first.get('issues', {}).get('totalCount')}")
            print(f"  issuesClosed.totalCount: {first.get('issuesClosed', {}).get('totalCount')}")

    # Lab01S02: paginação (consultar 1000 repositórios) + salvar .csv + relatório v1
    # TODO: loop com pageInfo.endCursor até 1000 repos; ordenar por stargazerCount; top 1000; exportar CSV


if __name__ == "__main__":
    main()
