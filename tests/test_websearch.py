import json

from agent.websearch import ExaClient, FetchedPage, parse_search_output

SEARCH_OUTPUT = """\
Title: Authentication
URL: https://pipedrive.readme.io/docs/core-api-concepts-authentication
Published: N/A
Author: N/A
Highlights:
# Authentication

All requests need auth.

---

Title: OAuth
URL: https://developers.pipedrive.com/docs/api/v1/Oauth
Published: N/A
Author: Pipedrive
Highlights:
OAuth 2.0 content here
"""


def test_parse_search_output() -> None:
    results = parse_search_output(SEARCH_OUTPUT)
    assert len(results) == 2
    assert results[0].title == "Authentication"
    assert results[0].url == "https://pipedrive.readme.io/docs/core-api-concepts-authentication"
    assert "All requests need auth." in results[0].highlights
    assert results[1].title == "OAuth"


def test_parse_search_output_ignores_junk() -> None:
    assert parse_search_output("") == []
    assert parse_search_output("no fields here") == []


def test_fetch_caches_failures(tmp_path) -> None:
    client = ExaClient(exa_bin="definitely-not-a-real-binary", cache_dir=tmp_path)
    page = client.fetch("https://example.com")
    assert not page.ok
    cache_files = list(tmp_path.glob("fetch-*.json"))
    assert len(cache_files) == 1
    cached = json.loads(cache_files[0].read_text())
    assert cached["ok"] is False
    again = client.fetch("https://example.com")
    assert again == page


def test_search_uses_cache(tmp_path) -> None:
    client = ExaClient(exa_bin="definitely-not-a-real-binary", cache_dir=tmp_path)
    path = client._cache_path("search", "q|5")
    path.write_text(json.dumps([{"title": "T", "url": "https://x.com", "highlights": "h"}]))
    results = client.search("q", 5)
    assert results[0].title == "T"


def test_fetched_page_model() -> None:
    page = FetchedPage(url="https://x.com", content="hello")
    assert page.ok
