from __future__ import annotations

import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from agent.config import APPS_JSON, RESEARCH_DIR, get_settings
from agent.llm import ChatClient, LLMError, extract_json_object
from agent.schemas import AppResearch, AppSeed
from agent.websearch import ExaClient, SearchResult

PAGE_EXCERPT_CHARS = 6000
HIGHLIGHT_CHARS = 2500
MAX_PAGES_PER_APP = 3

SYSTEM_PROMPT = """\
You are an API-research analyst at an integrations company (like Composio) deciding
whether an app can become an agent-callable toolkit. You research exactly one app per
request and answer with ONE JSON object only.

Rules:
- Base every factual claim ONLY on the supplied search snippets and page excerpts.
- Every evidence quote MUST be a verbatim substring (copy-paste, <= 200 chars) of the
  supplied material, paired with the URL of the page it came from.
- If the material does not answer a field, use "unknown" (never guess).
- Prefer the app's official docs over blogs or forums.
- Output JSON only. No markdown fences, no commentary.

Output schema:
{
  "one_liner": string,                    // what the app does, <= 12 words
  "auth_methods": string[],               // subset of: oauth2, api_key, basic,
                                          // bearer_token, session_cookie, none_public,
                                          // other, unknown
  "access": string,                       // exactly one of:
                                          // self_serv
                                          // e_free
                                          // (free dev
                                          // account /
                                          // free tier
                                          // gives cre
                                          // dentials)
                                          // self_serv
                                          // e_trial
                                          // (time-
                                          // limited
                                          // trial
                                          // gives cre
                                          // dentials)
                                          //   paid_plan_required (API/credentials need a paid plan)
                                          // admin_app
                                          // roval    
                                          // (workspac
                                          // e admin
                                          // must appr
                                          // ove/insta
                                          // ll)
                                          // partner_g
                                          // ated     
                                          // (partners
                                          // hip or
                                          // approval
                                          // program
                                          // required)
                                          //   contact_sales     (credentials only via sales)
                                          // no_public
                                          // _program
                                          // (no
                                          // public
                                          // developer
                                          // program
                                          // at all)
                                          //   unknown
  "api_styles": string[],                 // subset of: rest, graphql, soap, mixed, none, unknown
  "api_breadth": string,                  // broad (>50 endpoints/objects), moderate (10-50),
                                          // narrow (<10), none, unknown
  "official_mcp": boolean,
  // true only if an OFFICIAL MCP server from the vendor is documented
  "verdict": string,
  // buildable_now | buildable_with_work | gated | no_api | unknown
                                          // buildable
                                          // _now: doc
                                          // umented
                                          // public
                                          // API +
                                          // self-
                                          // serve cre
                                          // dentials
                                          // buildable
                                          // _with_wor
                                          // k: public
                                          // API but
                                          // friction
                                          // (paid
                                          // plan,
                                          //     approval, weird auth, thin docs)
                                          // gated: pa
                                          // rtnership
                                          // /sales/ad
                                          // min gate
                                          // blocks a
                                          // developer
                                          // today
                                          //   no_api: no meaningful public API
  "blocker": string | null,               // main blocker when not buildable_now, else null
  "confidence": number,                   // 0..1
  "evidence": [                           // 2-5 items covering auth, access, API surface at minimum
    {"claim": string, "url": string, "quote": string}
  ],
  "notes": string
  // anything unusual: MCP hints, deprecations, gotchas (may be "")
}
"""

USER_TEMPLATE = """\
App under research: {app}
Category: {category}
Website hint from the assignment: {domain}{hint_suffix}

Below are web search snippets and fetched page excerpts about this app's developer
API, authentication, and access model. Research the app and answer with the JSON
object described in the system prompt.

{materials}
"""


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def result_path(app: AppSeed, directory: Path = RESEARCH_DIR, pass_number: int = 1) -> Path:
    suffix = f"-p{pass_number}" if pass_number > 1 else ""
    return directory / f"{app.id:03d}-{slugify(app.app)}{suffix}.json"


def load_seeds(path: Path = APPS_JSON) -> list[AppSeed]:
    rows = json.loads(path.read_text())
    return [AppSeed.model_validate(row) for row in rows]


OFFICIAL_DOMAIN_HINTS = ("developer.", "developers.", "docs.", "api.", "help.", "support.")


def rank_results(results: list[SearchResult], domain: str) -> list[SearchResult]:
    bare = domain.split("/")[0]

    def score(result: SearchResult) -> int:
        value = 0
        host = re.sub(r"^https?://", "", result.url).split("/")[0]
        if bare and bare in host:
            value += 3
        if any(hint in host for hint in OFFICIAL_DOMAIN_HINTS):
            value += 2
        lowered = result.url.lower()
        if any(word in lowered for word in ("auth", "api", "oauth", "reference", "docs")):
            value += 1
        if any(bad in host for bad in ("stackoverflow.", "medium.", "reddit.", "quora.")):
            value -= 4
        return value

    return sorted(results, key=score, reverse=True)


def build_materials(app: AppSeed, exa: ExaClient) -> tuple[str, list[str]]:
    queries = [
        f"{app.app} API authentication documentation for developers ({app.domain})",
        f"{app.app} developer platform get API key or OAuth app credentials pricing access",
        f"{app.app} official MCP server or GraphQL REST API reference",
    ]
    chunks: list[str] = []
    source_urls: list[str] = []
    candidates: dict[str, SearchResult] = {}
    for query in queries:
        for result in exa.search(query, num_results=5):
            candidates.setdefault(result.url, result)
            snippet = result.highlights[:HIGHLIGHT_CHARS]
            chunks.append(f"### Search result: {result.title}\nURL: {result.url}\n{snippet}")
    ranked = rank_results(list(candidates.values()), app.domain)
    fetched = 0
    for result in ranked:
        if fetched >= MAX_PAGES_PER_APP:
            break
        page = exa.fetch(result.url)
        if not page.ok or len(page.content) < 200:
            continue
        fetched += 1
        source_urls.append(result.url)
        excerpt = page.content[:PAGE_EXCERPT_CHARS]
        chunks.append(f"### Fetched page: {result.title}\nURL: {result.url}\n{excerpt}")
    return "\n\n".join(chunks), source_urls


def research_app(
    app: AppSeed,
    exa: ExaClient,
    llm: ChatClient,
    pass_number: int = 1,
    feedback: str = "",
) -> AppResearch:
    materials, _ = build_materials(app, exa)
    hint_suffix = f" ({app.hint})" if app.hint else ""
    user = USER_TEMPLATE.format(
        app=app.app,
        category=app.category,
        domain=app.domain,
        hint_suffix=hint_suffix,
        materials=materials,
    )
    if feedback:
        user += (
            "\n\nA verifier rejected your previous answer for these reasons. "
            "Fix every issue while staying truthful to the supplied material:\n"
            + feedback
        )
    last_error = ""
    for _attempt in range(2):
        response = llm.chat(
            SYSTEM_PROMPT, user, max_tokens=4096, purpose=f"research-p{pass_number}"
        )
        try:
            payload = extract_json_object(response.content)
            payload["app_id"] = app.id
            payload["app"] = app.app
            payload["category"] = app.category
            research = AppResearch.model_validate(payload)
            break
        except (LLMError, ValidationError) as exc:
            last_error = str(exc)
            user += (
                "\n\nYour previous reply was not valid. Error: "
                + last_error[:600]
                + "\nReply with a corrected JSON object only."
            )
    else:
        raise LLMError(f"extraction failed for {app.app}: {last_error}")
    research.pass_number = pass_number
    research.researched_at = datetime.now(UTC).isoformat(timespec="seconds")
    return research


_print_lock = threading.Lock()


def run_research(
    only: list[int] | None = None,
    limit: int | None = None,
    force: bool = False,
    concurrency: int = 4,
    pass_number: int = 1,
    directory: Path = RESEARCH_DIR,
    feedback_by_id: dict[int, str] | None = None,
) -> int:
    settings = get_settings()
    exa = ExaClient(exa_bin=settings.exa_bin)
    llm = ChatClient(settings)
    seeds = load_seeds()
    if only:
        seeds = [seed for seed in seeds if seed.id in set(only)]
    directory.mkdir(parents=True, exist_ok=True)
    todo = []
    for seed in seeds:
        target = result_path(seed, directory, pass_number)
        if target.exists() and not force:
            continue
        todo.append(seed)
    if limit:
        todo = todo[:limit]
    if not todo:
        print("nothing to do: all requested apps already researched")
        return 0
    print(f"researching {len(todo)} apps (concurrency={concurrency}, pass={pass_number})")
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(
                research_app,
                seed,
                exa,
                llm,
                pass_number,
                (feedback_by_id or {}).get(seed.id, ""),
            ): seed
            for seed in todo
        }
        done = 0
        for future in as_completed(futures):
            seed = futures[future]
            try:
                research = future.result()
            except Exception as exc:
                failures.append(f"{seed.app}: {exc}")
                with _print_lock:
                    print(f"FAIL {seed.app}: {str(exc)[:200]}")
                continue
            target = result_path(seed, directory, pass_number)
            target.write_text(research.model_dump_json(indent=1) + "\n")
            done += 1
            with _print_lock:
                print(f"[{done}/{len(todo)}] {seed.app} -> {research.verdict} ({research.access})")
    if failures:
        print(f"{len(failures)} failures")
        return 1
    return 0
