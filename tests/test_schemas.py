import pytest
from pydantic import ValidationError

from agent.schemas import (
    AccessModel,
    ApiBreadth,
    ApiStyle,
    AppResearch,
    AuthMethod,
    Evidence,
    Verdict,
)


def valid_research() -> AppResearch:
    return AppResearch(
        app_id=1,
        app="Salesforce",
        category="CRM and Sales",
        one_liner="Cloud CRM platform",
        auth_methods=[AuthMethod.OAUTH2],
        access=AccessModel.SELF_SERVE_FREE,
        api_styles=[ApiStyle.REST],
        api_breadth=ApiBreadth.BROAD,
        official_mcp=False,
        verdict=Verdict.BUILDABLE_NOW,
        blocker=None,
        confidence=0.9,
        evidence=[
            Evidence(
                claim="OAuth2 supported",
                url="https://developer.salesforce.com/",
                quote="OAuth 2.0",
            )
        ],
    )


def test_valid_research_passes() -> None:
    research = valid_research()
    assert research.auth_methods == [AuthMethod.OAUTH2]


def test_evidence_is_required() -> None:
    research = valid_research()
    data = research.model_dump()
    data["evidence"] = []
    with pytest.raises(ValidationError):
        AppResearch.model_validate(data)


def test_confidence_bounds() -> None:
    data = valid_research().model_dump()
    data["confidence"] = 1.5
    with pytest.raises(ValidationError):
        AppResearch.model_validate(data)


def test_enums_reject_free_text() -> None:
    data = valid_research().model_dump()
    data["auth_methods"] = ["oauthish"]
    with pytest.raises(ValidationError):
        AppResearch.model_validate(data)
