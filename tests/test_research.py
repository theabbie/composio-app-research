from agent.research import rank_results, slugify
from agent.websearch import SearchResult


def test_slugify() -> None:
    assert slugify("Zoho CRM") == "zoho-crm"
    assert slugify("Otter AI") == "otter-ai"
    assert slugify("higgsfield") == "higgsfield"


def test_rank_results_prefers_official_docs() -> None:
    results = [
        SearchResult(title="blog", url="https://medium.com/x/pipedrive-api", highlights=""),
        SearchResult(
            title="official", url="https://developers.pipedrive.com/docs/api", highlights=""
        ),
        SearchResult(title="marketing", url="https://pipedrive.com/features", highlights=""),
    ]
    ranked = rank_results(results, "pipedrive.com")
    assert ranked[0].url == "https://developers.pipedrive.com/docs/api"
    assert ranked[-1].url == "https://medium.com/x/pipedrive-api"
