"""Testes de integração (REAIS) com a GitHub GraphQL API.

Por padrão estes testes são pulados (skipped) se não houver `GITHUB_TOKEN` válido.

- Não imprime token.
- Úteis para validar: autenticação, conectividade, e que a API responde com JSON.

Execução:
  python -m unittest -v test_integration_github_graphql.py

Opcional (teste mais pesado com a query do lab):
  $env:RUN_SLOW_INTEGRATION="1"
  python -m unittest -v test_integration_github_graphql.py
"""

from __future__ import annotations

import os
import time
import unittest
from typing import Any

import requests

import fetch_repos


def _get_token_or_none() -> str | None:
    # Permite carregar de .env (se existir) para facilitar uso local.
    try:
        fetch_repos.load_env()
    except Exception:
        # Nunca falha por causa de loader de env.
        pass

    token = os.environ.get("GITHUB_TOKEN")
    if not token or token.strip() in {"", "seu_token_aqui"}:
        return None
    return token.strip()


def _post_graphql(token: str, query: str, variables: dict[str, Any] | None = None) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {"query": query}
    if variables is not None:
        payload["variables"] = variables

    return requests.post(fetch_repos.GRAPHQL_URL, json=payload, headers=headers, timeout=30)


def _post_graphql_with_retries(
    token: str,
    query: str,
    variables: dict[str, Any] | None = None,
    max_retries: int = 3,
    retry_statuses: set[int] | None = None,
) -> requests.Response:
    """POST com retentativas para erros transitórios (ex.: 502/503/504)."""
    if retry_statuses is None:
        retry_statuses = {502, 503, 504}

    last_resp: requests.Response | None = None
    for attempt in range(max_retries):
        resp = _post_graphql(token, query, variables)
        last_resp = resp
        if resp.status_code not in retry_statuses:
            return resp
        # backoff simples
        time.sleep(2 * (attempt + 1))
    return last_resp  # type: ignore[return-value]


def _assert_http_200_or_explain(testcase: unittest.TestCase, resp: requests.Response) -> None:
    if resp.status_code == 200:
        return

    body_preview = (resp.text or "")[:400]
    if resp.status_code == 401:
        testcase.fail(
            "HTTP 401 (Bad credentials). O token está inválido/expirado/copiado errado.\n"
            "Ações sugeridas:\n"
            "- Gere um novo PAT no GitHub (Settings → Developer settings → Personal access tokens).\n"
            "- Defina na sessão: $env:GITHUB_TOKEN = \"<token>\" (sem espaços).\n"
            "- Valide rapidamente via REST (PowerShell):\n"
            "  Invoke-RestMethod -Headers @{ Authorization = \"Bearer $env:GITHUB_TOKEN\" } -Uri https://api.github.com/user\n"
            f"Resposta (preview): {body_preview}"
        )

    testcase.fail(f"HTTP {resp.status_code}: {body_preview}")


class GitHubGraphQLIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        token = _get_token_or_none()
        if token is None:
            self.skipTest("GITHUB_TOKEN não definido (ou placeholder). Defina para rodar testes reais.")
        self.token = token

    def test_viewer_login_and_rate_limit(self):
        query = """
        query {
          viewer { login }
          rateLimit { limit cost remaining resetAt }
        }
        """.strip()

        resp = _post_graphql(self.token, query)
        _assert_http_200_or_explain(self, resp)

        data = resp.json()
        self.assertNotIn("errors", data, f"GraphQL errors: {data.get('errors')}")

        viewer = data.get("data", {}).get("viewer", {})
        self.assertTrue(viewer.get("login"), "viewer.login vazio; token pode ser inválido")

        rl = data.get("data", {}).get("rateLimit", {})
        self.assertIn("remaining", rl)

    def test_lab01_query_smoke_optional(self):
        if os.environ.get("RUN_SLOW_INTEGRATION") != "1":
            self.skipTest("Teste slow: defina RUN_SLOW_INTEGRATION=1 para rodar")

        query = fetch_repos.read_query()
        resp = _post_graphql_with_retries(
            self.token,
            query,
            variables={"cursor": None, "first": fetch_repos.DEFAULT_PAGE_SIZE},
            max_retries=3,
        )

        # Se persistir erro transitório, não falha o build local: apenas sinaliza.
        if resp.status_code in (502, 503, 504):
            self.skipTest(
                f"GitHub respondeu {resp.status_code} após retentativas (instabilidade/proxy). Tente novamente mais tarde."
            )

        _assert_http_200_or_explain(self, resp)

        data = resp.json()
        self.assertNotIn("errors", data, f"GraphQL errors: {data.get('errors')}")

        search = data.get("data", {}).get("search", {})
        self.assertIn("nodes", search)
        nodes = search.get("nodes") or []
        self.assertTrue(len(nodes) > 0, "Nenhum node retornado na primeira página")

        # Checagem mínima de campos esperados no primeiro repo.
        first = next((n for n in nodes if isinstance(n, dict) and n.get("name")), None)
        self.assertIsNotNone(first, "Primeiro repositório não encontrado em nodes")

        for key in [
            "name",
            "nameWithOwner",
            "url",
            "stargazerCount",
            "createdAt",
            "pushedAt",
            "primaryLanguage",
            "pullRequests",
            "releases",
            "issues",
            "issuesClosed",
        ]:
            self.assertIn(key, first, f"Campo ausente no repo: {key}")

        # Não martelar rate limit se a query ficou cara: pausa breve opcional.
        time.sleep(0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
