from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AppSeed(BaseModel):
    id: int = Field(ge=1, le=100)
    app: str
    category: str
    domain: str
    url: str = ""
    hint: str = ""


class AuthMethod(StrEnum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER_TOKEN = "bearer_token"
    SESSION_COOKIE = "session_cookie"
    NONE_PUBLIC = "none_public"
    OTHER = "other"
    UNKNOWN = "unknown"


class AccessModel(StrEnum):
    SELF_SERVE_FREE = "self_serve_free"
    SELF_SERVE_TRIAL = "self_serve_trial"
    PAID_PLAN_REQUIRED = "paid_plan_required"
    ADMIN_APPROVAL = "admin_approval"
    PARTNER_GATED = "partner_gated"
    CONTACT_SALES = "contact_sales"
    NO_PUBLIC_PROGRAM = "no_public_program"
    UNKNOWN = "unknown"


SELF_SERVE = {AccessModel.SELF_SERVE_FREE, AccessModel.SELF_SERVE_TRIAL}
GATED = {
    AccessModel.PAID_PLAN_REQUIRED,
    AccessModel.ADMIN_APPROVAL,
    AccessModel.PARTNER_GATED,
    AccessModel.CONTACT_SALES,
    AccessModel.NO_PUBLIC_PROGRAM,
}


class ApiStyle(StrEnum):
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    MIXED = "mixed"
    NONE = "none"
    UNKNOWN = "unknown"


class ApiBreadth(StrEnum):
    BROAD = "broad"
    MODERATE = "moderate"
    NARROW = "narrow"
    NONE = "none"
    UNKNOWN = "unknown"


class Verdict(StrEnum):
    BUILDABLE_NOW = "buildable_now"
    BUILDABLE_WITH_WORK = "buildable_with_work"
    GATED = "gated"
    NO_API = "no_api"
    UNKNOWN = "unknown"


class Evidence(BaseModel):
    claim: str
    url: str
    quote: str


class AppResearch(BaseModel):
    app_id: int = Field(ge=1, le=100)
    app: str
    category: str
    one_liner: str
    auth_methods: list[AuthMethod]
    access: AccessModel
    api_styles: list[ApiStyle]
    api_breadth: ApiBreadth
    official_mcp: bool = False
    verdict: Verdict
    blocker: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(min_length=1)
    notes: str = ""
    pass_number: int = 1
    researched_at: str = ""


class FlagSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class VerificationFlag(BaseModel):
    app_id: int
    field: str
    severity: FlagSeverity
    detail: str


class AutoVerification(BaseModel):
    app_id: int
    app: str
    evidence_urls_checked: int
    evidence_urls_ok: int
    quotes_checked: int
    quotes_found: int
    flags: list[VerificationFlag]


class HumanCheck(BaseModel):
    app_id: int
    app: str
    fields_correct_pass1: dict[str, bool] = Field(default_factory=dict)
    fields_correct_pass2: dict[str, bool] = Field(default_factory=dict)
    notes: str = ""
