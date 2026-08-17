# composio-app-research

An autonomous research agent that profiles 100 popular apps the way an
integrations team would: how each app authenticates, whether a developer can
self-serve credentials or hits a gate, what the public API surface looks like,
whether an official MCP server exists, and whether the app could become an
agent-callable toolkit today — every claim backed by a cited docs URL.

The full write-up (findings, patterns, the agent itself, and the verification
story) is the deployed case-study page: **<live URL goes here after deploy>**.

## Repository layout

```
agent/        research pipeline (Python 3.11+, uv-managed)
data/         seed research set + agent output (JSON, committed)
tests/        pytest suite for the pipeline
site/         case-study page (Vite + React + TypeScript + Tailwind)
```

## Prerequisites

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and npm
- The [`exa`](https://exa.ai) CLI on PATH for web search/fetch
  (`exa search "<query>"`, `exa fetch <url>`)
- An OpenAI-compatible LLM endpoint for structured extraction

## Setup

```bash
uv venv --python 3.11 .venv
uv pip install -e ".[dev]"
cp .env.example .env   # fill in your LLM endpoint
cd site && npm install
```

## Environment variables

See `.env.example`. The pipeline needs an OpenAI-compatible chat-completions
endpoint (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`). On this machine the key
is read from the macOS keychain when `LLM_API_KEY` is unset; everywhere else,
set the env vars. No secrets are ever committed.

## Running the research agent

```bash
# 1. (re)build the seed list of 100 apps  -> data/apps.json
.venv/bin/python -m agent seed

# 2. research all apps (resumable; cached web fetches) -> data/research/*.json
.venv/bin/python -m agent research

# 3. automated verification: re-fetch every evidence URL and check the
#    quoted claim is actually on the page                    -> data/verification/
.venv/bin/python -m agent verify

# 4. repair pass: re-research apps the verifier flagged, feeding it the
#    verifier's objections                                    -> pass 2 results
.venv/bin/python -m agent repair

# 5. score the human-checked sample, pass 1 vs pass 2 accuracy
.venv/bin/python -m agent sample-check

# 6. pattern analysis -> site/public/data/*.json
.venv/bin/python -m agent analyze
```

Every stage is resumable and safe to re-run; web traffic is cached under
`data/cache/` (gitignored), so iteration costs no new network calls.

## The case-study page

```bash
cd site
npm run dev        # local dev server
npm run test       # vitest unit tests
npm run typecheck  # strict tsc
npm run build      # dist/index.html — one self-contained page
```

## Testing and quality gates

```bash
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check agent tests
.venv/bin/python -m mypy agent
```

## Deployment

The site builds to a single static HTML file and deploys to Vercel as a static
asset:

```bash
cd site && npm run build && vercel deploy dist --prod --yes
```

## Notes and known constraints

- `composioassignment.md` (the original brief) is not committed; the parsed
  research set in `data/apps.json` is the canonical seed.
- "Gated" findings are successes, not failures: where an app requires a paid
  plan, admin approval, or partnership, the agent reports that with evidence.
