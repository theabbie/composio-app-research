from __future__ import annotations

import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agent.config import RESEARCH_DIR, VERIFICATION_DIR, get_settings
from agent.schemas import (
    AccessModel,
    AppResearch,
    AutoVerification,
    FlagSeverity,
    Verdict,
    VerificationFlag,
)
from agent.websearch import JinaClient


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\\", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def quote_found(quote: str, page_text: str) -> bool:
    needle = normalize(quote)
    haystack = normalize(page_text)
    if not needle:
        return False
    if needle in haystack:
        return True
    if len(needle) > 160:
        return needle[:120] in haystack or needle[-120:] in haystack
    words = needle.split(" ")
    if len(words) > 8:
        return " ".join(words[:8]) in haystack and " ".join(words[-8:]) in haystack
    return False


def check_consistency(research: AppResearch) -> list[VerificationFlag]:
    flags: list[VerificationFlag] = []

    def flag(field: str, detail: str, severity: FlagSeverity = FlagSeverity.ERROR) -> None:
        flags.append(
            VerificationFlag(app_id=research.app_id, field=field, severity=severity, detail=detail)
        )

    gated_access = {
        AccessModel.PAID_PLAN_REQUIRED,
        AccessModel.ADMIN_APPROVAL,
        AccessModel.PARTNER_GATED,
        AccessModel.CONTACT_SALES,
        AccessModel.NO_PUBLIC_PROGRAM,
    }
    if research.verdict == Verdict.BUILDABLE_NOW and research.access in gated_access:
        flag("verdict", f"verdict=buildable_now contradicts access={research.access}")
    if research.verdict == Verdict.GATED and research.access not in gated_access | {
        AccessModel.UNKNOWN
    }:
        flag("verdict", f"verdict=gated but access={research.access}", FlagSeverity.WARNING)
    needs_blocker = research.verdict in (
        Verdict.GATED,
        Verdict.NO_API,
        Verdict.BUILDABLE_WITH_WORK,
    )
    if needs_blocker and not research.blocker:
        flag("blocker", f"verdict={research.verdict} requires a blocker")
    if research.verdict == Verdict.NO_API and research.api_breadth.value not in ("none", "unknown"):
        flag("api_breadth", "verdict=no_api but api_breadth is set", FlagSeverity.WARNING)
    if research.confidence >= 0.8 and any(
        value == "unknown"
        for value in [research.access.value, research.api_breadth.value]
    ):
        flag("confidence", "high confidence with unknown fields", FlagSeverity.WARNING)
    if research.official_mcp:
        mcp_evidence = [
            item for item in research.evidence if "mcp" in (item.quote + item.claim).lower()
        ]
        if not mcp_evidence:
            flag(
                "official_mcp",
                "official_mcp=true but no evidence quote or claim mentions MCP",
            )
    return flags


def verify_one(research: AppResearch, web: JinaClient) -> AutoVerification:
    flags = check_consistency(research)
    urls_ok = 0
    quotes_found = 0
    for item in research.evidence:
        page = web.fetch(item.url)
        if not page.ok or len(page.content) < 100:
            flags.append(
                VerificationFlag(
                    app_id=research.app_id,
                    field="evidence",
                    severity=FlagSeverity.ERROR,
                    detail=f"evidence URL failed to fetch: {item.url} ({page.error[:120]})",
                )
            )
            continue
        urls_ok += 1
        if quote_found(item.quote, page.content):
            quotes_found += 1
        else:
            flags.append(
                VerificationFlag(
                    app_id=research.app_id,
                    field="evidence",
                    severity=FlagSeverity.ERROR,
                    detail=f"quote not found on {item.url}: {item.quote[:100]!r}",
                )
            )
    return AutoVerification(
        app_id=research.app_id,
        app=research.app,
        evidence_urls_checked=len(research.evidence),
        evidence_urls_ok=urls_ok,
        quotes_checked=len(research.evidence),
        quotes_found=quotes_found,
        flags=flags,
    )


def load_research(directory: Path = RESEARCH_DIR, pass_number: int = 1) -> list[AppResearch]:
    results = []
    pattern = "*.json" if pass_number == 1 else f"*-p{pass_number}.json"
    for path in sorted(directory.glob(pattern)):
        if pass_number == 1 and re.search(r"-p\d+\.json$", path.name):
            continue
        results.append(AppResearch.model_validate(json.loads(path.read_text())))
    return results


def run_verify(directory: Path = RESEARCH_DIR, pass_number: int = 1) -> int:
    settings = get_settings()
    web = JinaClient(api_key=settings.jina_api_key)
    results = load_research(directory, pass_number)
    if not results:
        print("no research results found")
        return 1
    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    out_path = VERIFICATION_DIR / f"auto-pass{pass_number}.json"
    verifications: list[AutoVerification] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for verification in pool.map(lambda r: verify_one(r, web), results):
            verifications.append(verification)
    verifications.sort(key=lambda v: v.app_id)
    out_path.write_text(
        json.dumps([v.model_dump() for v in verifications], indent=1) + "\n"
    )
    total = len(verifications)
    clean = sum(1 for v in verifications if not any(f.severity == "error" for f in v.flags))
    flagged = [v for v in verifications if any(f.severity == "error" for f in v.flags)]
    quotes_total = sum(v.quotes_checked for v in verifications)
    quotes_ok = sum(v.quotes_found for v in verifications)
    print(f"verified {total} apps -> {out_path}")
    print(f"clean: {clean}/{total}; evidence quotes verified: {quotes_ok}/{quotes_total}")
    for item in flagged:
        errors = [f for f in item.flags if f.severity == "error"]
        detail = errors[0].detail[:110]
        print(f"  FLAG {item.app_id:3d} {item.app}: {len(errors)} error(s) - {detail}")
    return 0
