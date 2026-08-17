import json

from agent.websearch import FetchedPage, JinaClient, parse_search_output

SEARCH_OUTPUT = """\
[1] Title: Pipedrive API Reference and Documentation
[1] URL Source: https://developers.pipedrive.com/docs/api/v1
[1] Description: RESTful Pipedrive API reference for developers building integrations.

[2] Title: Authentication
[2] URL Source: https://pipedrive.readme.io/docs/core-api-concepts-authentication
[2] Description: All requests to our API need authentication.
[2] Date: Jun 10, 2022
"""


def test_parse_search_output() -> None:
    results = parse_search_output(SEARCH_OUTPUT)
    assert len(results) == 2
    assert results[0].title == "Pipedrive API Reference and Documentation"
    assert results[0].url == "https://developers.pipedrive.com/docs/api/v1"
    assert "RESTful" in results[0].highlights
    assert results[1].title == "Authentication"


def test_parse_search_output_ignores_junk() -> None:
    assert parse_search_output("") == []
    assert parse_search_output("no fields here") == []


def test_fetch_caches_failures(tmp_path) -> None:
    client = JinaClient(api_key="dummy", cache_dir=tmp_path, max_attempts=1, timeout=1)
    page = client.fetch("https://nonexistent.invalid/..")
    assert not page.ok
    cache_files = list(tmp_path.glob("fetch-*.json"))
    assert len(cache_files) == 1
    cached = json.loads(cache_files[0].read_text())
    assert cached["ok"] is False
    again = client.fetch("https://nonexistent.invalid/..")
    assert again == page


def test_search_uses_cache(tmp_path) -> None:
    client = JinaClient(api_key="dummy", cache_dir=tmp_path)
    path = client._cache_path("search", "q|5")
    path.write_text(json.dumps([{"title": "T", "url": "https://x.com", "highlights": "h"}]))
    results = client.search("q", 5)
    assert results[0].title == "T"


def test_fetched_page_model() -> None:
    page = FetchedPage(url="https://x.com", content="hello")
    assert page.ok
