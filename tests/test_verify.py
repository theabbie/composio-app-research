from agent.schemas import (
    AccessModel,
    ApiBreadth,
    ApiStyle,
    AppResearch,
    AuthMethod,
    Evidence,
    FlagSeverity,
    Verdict,
)
from agent.verify import check_consistency, normalize, quote_found


def make_research(**overrides) -> AppResearch:
    data = dict(
        app_id=1,
        app="X",
        category="CRM and Sales",
        one_liner="thing",
        auth_methods=[AuthMethod.OAUTH2],
        access=AccessModel.SELF_SERVE_FREE,
        api_styles=[ApiStyle.REST],
        api_breadth=ApiBreadth.BROAD,
        official_mcp=False,
        verdict=Verdict.BUILDABLE_NOW,
        blocker=None,
        confidence=0.9,
        evidence=[Evidence(claim="c", url="https://x.com", quote="q")],
    )
    data.update(overrides)
    return AppResearch.model_validate(data)


def test_normalize_collapses_whitespace_and_case() -> None:
    assert normalize("  Hello\n  World  ") == "hello world"


def test_quote_found_exact_and_fuzzy() -> None:
    page = "The API token must be provided in the x-api-token header for all requests."
    assert quote_found("api token must be provided", page)
    assert quote_found("API token   must be\nprovided", page)
    assert not quote_found("graphql subscriptions supported", page)


def test_quote_found_long_quote_partial() -> None:
    page = " ".join(["alpha"] * 200) + " needle in a haystack " + " ".join(["omega"] * 200)
    quote = " ".join(["alpha"] * 100) + " needle in a haystack " + " ".join(["omega"] * 100)
    assert quote_found(quote, page)


def test_consistency_buildable_now_with_gate_is_error() -> None:
    research = make_research(access=AccessModel.PARTNER_GATED)
    flags = check_consistency(research)
    assert any(f.severity == FlagSeverity.ERROR and f.field == "verdict" for f in flags)


def test_consistency_gated_requires_blocker() -> None:
    research = make_research(verdict=Verdict.GATED, access=AccessModel.CONTACT_SALES, blocker=None)
    flags = check_consistency(research)
    assert any(f.field == "blocker" for f in flags)


def test_consistency_clean_record_has_no_errors() -> None:
    research = make_research()
    flags = check_consistency(research)
    assert not [f for f in flags if f.severity == FlagSeverity.ERROR]
