"""
Lab01S02 – Coleta de 1.000 repositórios populares do GitHub via API GraphQL

- Coleta 10 páginas de 100 repositórios (total 1.000), ordenados por número de estrelas.
- Salva os dados em CSV para análise das questões de pesquisa do laboratório.

Requisitos:
- Token do GitHub em variável de ambiente GITHUB_TOKEN
- Python >=3.8
- requests

Colunas coletadas:
- name, nameWithOwner, url, stargazerCount, createdAt, pushedAt, primaryLanguage, pullRequestsMerged, releasesTotal, issuesTotal, issuesClosed
"""
import os
import sys
import csv
import time
import requests
from pathlib import Path
from datetime import datetime

GRAPHQL_URL = "https://api.github.com/graphql"
QUERY = """
query TopRepos($cursor: String, $first: Int = 100) {
  search(
    query: \"stars:>1\"
    type: REPOSITORY
    first: $first
    after: $cursor
  ) {
    repositoryCount
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        name
        nameWithOwner
        url
        stargazerCount
        createdAt
        pushedAt
        primaryLanguage { name }
        pullRequests(states: MERGED) { totalCount }
        releases { totalCount }
        issues { totalCount }
        issuesClosed: issues(states: CLOSED) { totalCount }
      }
    }
  }
}
"""

OUTPUT_CSV = Path(__file__).parent / "repositorios_1000.csv"

FIELDS = [
    "name", "nameWithOwner", "url", "stargazerCount", "createdAt", "pushedAt",
    "primaryLanguage", "pullRequestsMerged", "releasesTotal", "issuesTotal", "issuesClosed"
]

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina a variável de ambiente GITHUB_TOKEN com seu token do GitHub.", file=sys.stderr)
        sys.exit(1)
    return token

def fetch_page(token, cursor=None, max_retries=8, timeout=30):
    variables = {"cursor": cursor, "first": 100}
    headers = {"Authorization": f"Bearer {token}"}
    transient_statuses = {502, 503, 504}
    for attempt in range(max_retries):
        try:
            response = requests.post(GRAPHQL_URL, json={"query": QUERY, "variables": variables}, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            print(f"Erro de conexão: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                wait = min(60, 5 * (2**attempt))
                print(f"  Nova tentativa em {wait}s ({attempt + 2}/{max_retries})...", file=sys.stderr)
                time.sleep(wait)
                continue
            else:
                sys.exit(1)
        if response.status_code == 200:
            return response.json()
        elif response.status_code in transient_statuses:
            if attempt < max_retries - 1:
                wait = min(60, 5 * (2**attempt))
                print(f"  {response.status_code} Gateway error. Nova tentativa em {wait}s ({attempt + 2}/{max_retries})...", file=sys.stderr)
                time.sleep(wait)
                continue
        print(f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)
    print("Falha após múltiplas tentativas.", file=sys.stderr)
    sys.exit(1)

def parse_node(node):
    return {
        "name": node.get("name"),
        "nameWithOwner": node.get("nameWithOwner"),
        "url": node.get("url"),
        "stargazerCount": node.get("stargazerCount"),
        "createdAt": node.get("createdAt"),
        "pushedAt": node.get("pushedAt"),
        "primaryLanguage": (node.get("primaryLanguage") or {}).get("name"),
        "pullRequestsMerged": (node.get("pullRequests") or {}).get("totalCount"),
        "releasesTotal": (node.get("releases") or {}).get("totalCount"),
        "issuesTotal": (node.get("issues") or {}).get("totalCount"),
        "issuesClosed": (node.get("issuesClosed") or {}).get("totalCount"),
    }

def main():
    token = get_github_token()
    all_repos = []
    cursor = None
    for page in range(10):
        print(f"Buscando página {page+1}/10...")
        data = fetch_page(token, cursor, max_retries=8, timeout=30)
        search = data["data"]["search"]
        nodes = search["nodes"]
        for node in nodes:
            all_repos.append(parse_node(node))
        page_info = search["pageInfo"]
        cursor = page_info["endCursor"]
        if not page_info["hasNextPage"]:
            break
        time.sleep(1.5)  # Evita rate limit
    # Ordena por stargazerCount (desc) e pega os 1000 primeiros
    all_repos.sort(key=lambda r: r["stargazerCount"] or 0, reverse=True)
    all_repos = all_repos[:1000]
    # Salva CSV
    with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for repo in all_repos:
            writer.writerow(repo)
    print(f"Salvo: {OUTPUT_CSV} ({len(all_repos)} repositórios)")

if __name__ == "__main__":
    main()
