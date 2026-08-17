export function Footer() {
  return (
    <footer id="run" className="border-t border-zinc-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-14">
        <h2 className="text-2xl font-semibold tracking-tight text-zinc-900">Run it yourself</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-600">
          The whole pipeline is in the source repository and reproduces this page end to end.
          Web research is cached to disk, LLM calls are usage-logged, and every stage is resumable.
        </p>
        <pre className="mt-6 overflow-x-auto rounded-xl border border-zinc-800 bg-zinc-900 p-5 font-mono text-xs leading-relaxed text-zinc-100">
{`git clone <repo-url> && cd composio-app-research
uv venv --python 3.11 .venv && uv pip install -e ".[dev]"
cp .env.example .env            # point it at any OpenAI-compatible LLM

.venv/bin/python -m agent seed            # 100-app research set
.venv/bin/python -m agent research        # research all 100 (resumable)
.venv/bin/python -m agent verify          # re-fetch evidence, check quotes
.venv/bin/python -m agent repair          # second pass on flagged apps
.venv/bin/python -m agent analyze         # build the data behind this page
cd site && npm install && npm run build   # dist/index.html = this page`}
        </pre>
        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-t border-zinc-200 pt-6 text-xs text-zinc-500">
          <p>
            Built with an agent pipeline (Exa search + schema-validated LLM extraction), verified
            twice, presented as one self-contained HTML page.
          </p>
          <a
            href="https://github.com/theabbie/composio-app-research"
            className="font-medium text-zinc-700 underline decoration-zinc-300 underline-offset-2 hover:text-zinc-900"
          >
            Source repository
          </a>
        </div>
      </div>
    </footer>
  )
}
