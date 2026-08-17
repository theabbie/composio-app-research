from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from agent.config import RESEARCH_DIR, ROOT, VERIFICATION_DIR
from agent.llm import load_usage
from agent.schemas import GATED, SELF_SERVE, AppResearch
from agent.verify import load_research

SITE_DATA = ROOT / "site" / "src" / "data"


def final_results(directory: Path = RESEARCH_DIR) -> list[AppResearch]:
    pass1 = {r.app_id: r for r in load_research(directory, pass_number=1)}
    pass2 = {r.app_id: r for r in load_research(directory, pass_number=2)}
    merged = dict(pass1)
    merged.update(pass2)
    return [merged[k] for k in sorted(merged)]


def _share(part: int, whole: int) -> float:
    return round(part / whole, 3) if whole else 0.0


JsonObject = dict[str, Any]


def analyze(results: list[AppResearch]) -> JsonObject:
    total = len(results)
    auth_counts: Counter[str] = Counter()
    for result in results:
        for method in result.auth_methods:
            auth_counts[method.value] += 1
    access_counts = Counter(r.access.value for r in results)
    verdict_counts = Counter(r.verdict.value for r in results)
    breadth_counts = Counter(r.api_breadth.value for r in results)
    style_counts: Counter[str] = Counter()
    for result in results:
        for style in result.api_styles:
            style_counts[style.value] += 1

    by_category: dict[str, JsonObject] = {}
    grouped: dict[str, list[AppResearch]] = defaultdict(list)
    for result in results:
        grouped[result.category].append(result)
    for category, rows in sorted(grouped.items()):
        self_serve = sum(1 for r in rows if r.access in SELF_SERVE)
        gated = sum(1 for r in rows if r.access in GATED)
        buildable = sum(1 for r in rows if r.verdict.value == "buildable_now")
        by_category[category] = {
            "apps": len(rows),
            "self_serve": self_serve,
            "gated": gated,
            "buildable_now": buildable,
            "self_serve_rate": _share(self_serve, len(rows)),
            "buildable_rate": _share(buildable, len(rows)),
        }

    blockers = Counter(
        (r.blocker or "").strip().lower() for r in results if r.blocker
    )
    blocker_taxonomy = _taxonomize_blockers(results)

    mcp_apps = [r.app for r in results if r.official_mcp]
    easy_wins = [
        r.app
        for r in results
        if r.verdict.value == "buildable_now" and r.access in SELF_SERVE
    ]
    needs_outreach: list[dict[str, str | None]] = [
        {"app": r.app, "category": r.category, "access": r.access.value, "blocker": r.blocker}
        for r in results
        if r.access in GATED
    ]
    needs_outreach.sort(key=lambda row: row["app"] or "")

    return {
        "total_apps": total,
        "auth_distribution": dict(auth_counts.most_common()),
        "access_distribution": dict(access_counts.most_common()),
        "verdict_distribution": dict(verdict_counts.most_common()),
        "api_breadth_distribution": dict(breadth_counts.most_common()),
        "api_style_distribution": dict(style_counts.most_common()),
        "by_category": by_category,
        "self_serve_rate": _share(
            sum(1 for r in results if r.access in SELF_SERVE), total
        ),
        "gated_rate": _share(sum(1 for r in results if r.access in GATED), total),
        "buildable_now_rate": _share(
            sum(1 for r in results if r.verdict.value == "buildable_now"), total
        ),
        "official_mcp_apps": sorted(mcp_apps),
        "easy_wins": sorted(easy_wins),
        "needs_outreach": needs_outreach,
        "blocker_taxonomy": blocker_taxonomy,
        "top_blockers_raw": dict(blockers.most_common(15)),
    }


BLOCKER_BUCKETS = [
    ("partnership / approval program", ("partner", "approval program", "partner_gated")),
    ("sales-contact gate", ("contact sales", "contact_sales", "sales")),
    ("paid plan required", ("paid", "pricing", "subscription", "paid_plan")),
    ("admin / enterprise approval", ("admin", "enterprise", "workspace admin")),
    ("no public API", ("no public api", "no_api", "no documented api", "undocumented")),
    ("auth friction", ("oauth app review", "verification", "scopes approval")),
    ("docs gaps", ("docs", "documentation")),
]


def _taxonomize_blockers(results: list[AppResearch]) -> dict[str, int]:
    taxonomy: defaultdict[str, int] = defaultdict(int)
    for result in results:
        text = ((result.blocker or "") + " " + result.access.value).lower()
        for bucket, needles in BLOCKER_BUCKETS:
            if any(needle in text for needle in needles):
                taxonomy[bucket] += 1
                break
        else:
            if result.blocker:
                taxonomy["other"] += 1
    return dict(sorted(taxonomy.items(), key=lambda kv: -kv[1]))


def _load_verification() -> JsonObject:
    out: JsonObject = {}
    for pass_number in (1, 2):
        path = VERIFICATION_DIR / f"auto-pass{pass_number}.json"
        if path.exists():
            rows = json.loads(path.read_text())
            clean = sum(
                1 for row in rows if not any(f["severity"] == "error" for f in row["flags"])
            )
            quotes_total = sum(row["quotes_checked"] for row in rows)
            quotes_ok = sum(row["quotes_found"] for row in rows)
            out[f"pass{pass_number}"] = {
                "apps": len(rows),
                "clean": clean,
                "quotes_checked": quotes_total,
                "quotes_found": quotes_ok,
            }
    summary = VERIFICATION_DIR / "summary.json"
    if summary.exists():
        out["human_sample"] = json.loads(summary.read_text())
    sample_path = VERIFICATION_DIR / "human_sample.json"
    if sample_path.exists():
        out["human_sample_rows"] = json.loads(sample_path.read_text())
    return out


def run_analyze() -> int:
    results = final_results()
    if not results:
        print("no research results found; run `agent research` first")
        return 1
    analysis = analyze(results)
    analysis["verification"] = _load_verification()
    usage: JsonObject = load_usage()
    analysis["llm_usage"] = usage
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / "analysis.json").write_text(json.dumps(analysis, indent=1) + "\n")
    apps_payload = [
        {
            **r.model_dump(),
            "auth_methods": [m.value for m in r.auth_methods],
            "api_styles": [s.value for s in r.api_styles],
            "access": r.access.value,
            "api_breadth": r.api_breadth.value,
            "verdict": r.verdict.value,
            "evidence": [e.model_dump() for e in r.evidence],
        }
        for r in results
    ]
    (SITE_DATA / "apps.json").write_text(json.dumps(apps_payload, indent=1) + "\n")
    print(
        f"analyzed {len(results)} apps -> {SITE_DATA}/analysis.json, apps.json\n"
        f"self-serve rate: {float(analysis['self_serve_rate']):.0%}, "
        f"buildable-now rate: {float(analysis['buildable_now_rate']):.0%}, "
        f"official MCP: {len(analysis['official_mcp_apps'])}"
    )
    return 0
