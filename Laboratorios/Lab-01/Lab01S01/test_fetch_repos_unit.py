import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import fetch_repos


class FakeResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class LoadEnvTests(unittest.TestCase):
    def test_load_env_ignores_comments_and_blanks(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                """
                # comment\n
                GITHUB_TOKEN=abc123\n
                INVALID_LINE\n
                KEY_WITH_SPACES = value\n
                """.strip(),
                encoding="utf-8",
            )

            with mock.patch.dict(os.environ, {}, clear=True):
                fetch_repos.load_env(env_path)
                self.assertEqual(os.environ.get("GITHUB_TOKEN"), "abc123")
                self.assertEqual(os.environ.get("KEY_WITH_SPACES"), "value")

    def test_load_env_does_not_override_existing_env(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("GITHUB_TOKEN=from_file", encoding="utf-8")

            with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "from_session"}, clear=True):
                fetch_repos.load_env(env_path)
                self.assertEqual(os.environ.get("GITHUB_TOKEN"), "from_session")


class GetTokenTests(unittest.TestCase):
    def test_get_token_exits_when_missing(self):
        with mock.patch.object(fetch_repos, "load_env") as _:
            with mock.patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(SystemExit):
                    fetch_repos.get_token()

    def test_get_token_returns_when_present(self):
        with mock.patch.object(fetch_repos, "load_env") as _:
            with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "t"}, clear=True):
                self.assertEqual(fetch_repos.get_token(), "t")

    def test_get_token_exits_when_placeholder(self):
        with mock.patch.object(fetch_repos, "load_env") as _:
            with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "seu_token_aqui"}, clear=True):
                with self.assertRaises(SystemExit):
                    fetch_repos.get_token()


class ReadQueryTests(unittest.TestCase):
    def test_read_query_exits_when_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "query.graphql"
            with mock.patch.object(fetch_repos, "QUERY_FILE", missing):
                with self.assertRaises(SystemExit):
                    fetch_repos.read_query()

    def test_read_query_reads_file(self):
        with tempfile.TemporaryDirectory() as td:
            qf = Path(td) / "query.graphql"
            qf.write_text("query { viewer { login } }", encoding="utf-8")
            with mock.patch.object(fetch_repos, "QUERY_FILE", qf):
                self.assertIn("viewer", fetch_repos.read_query())


class FetchPageTests(unittest.TestCase):
    def test_fetch_page_returns_data_on_success(self):
        payload = {"data": {"search": {"nodes": []}}}
        resp = FakeResponse(200, json.dumps(payload))
        with mock.patch("fetch_repos.requests.post", return_value=resp):
            data = fetch_repos.fetch_page("token", "query")
            self.assertEqual(data, payload)

    def test_fetch_page_exits_on_graphql_errors(self):
        payload = {"errors": [{"message": "bad"}]}
        resp = FakeResponse(200, json.dumps(payload))
        with mock.patch("fetch_repos.requests.post", return_value=resp):
            with self.assertRaises(SystemExit):
                fetch_repos.fetch_page("token", "query")

    def test_fetch_page_exits_on_non_200(self):
        payload = {"message": "Forbidden"}
        resp = FakeResponse(403, json.dumps(payload))
        with mock.patch("fetch_repos.requests.post", return_value=resp):
            with self.assertRaises(SystemExit):
                fetch_repos.fetch_page("token", "query")

    def test_fetch_page_exits_on_empty_body(self):
        resp = FakeResponse(200, "")
        with mock.patch("fetch_repos.requests.post", return_value=resp):
            with self.assertRaises(SystemExit):
                fetch_repos.fetch_page("token", "query")

    def test_fetch_page_exits_on_non_json_body(self):
        resp = FakeResponse(200, "<html>nope</html>")
        with mock.patch("fetch_repos.requests.post", return_value=resp):
            with self.assertRaises(SystemExit):
                fetch_repos.fetch_page("token", "query")

    def test_fetch_page_retries_on_502_then_succeeds(self):
        ok_payload = {"data": {"search": {"nodes": []}}}
        responses = [
            FakeResponse(502, "<html>bad gateway</html>"),
            FakeResponse(200, json.dumps(ok_payload)),
        ]

        with mock.patch("fetch_repos.time.sleep") as sleep_mock:
            with mock.patch("fetch_repos.requests.post", side_effect=responses) as post_mock:
                data = fetch_repos.fetch_page("token", "query", cursor=None, max_retries=3)

        self.assertEqual(data, ok_payload)
        self.assertEqual(post_mock.call_count, 2)
        sleep_mock.assert_called()


if __name__ == "__main__":
    unittest.main()
