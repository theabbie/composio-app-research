import { formatCost, formatTokens } from '../lib/stats'
import type { Analysis } from '../types'

const STAGES = [
  {
    name: 'seed',
    detail: 'Parses the assignment into a typed research set (100 apps, 10 categories).',
  },
  {
    name: 'research',
    detail:
      'Per app: three targeted Exa searches (auth docs, credential access, MCP/API surface), fetches the top official docs pages, then an LLM extracts a schema-validated JSON profile. Every field must cite a verbatim quote from a fetched page.',
  },
  {
    name: 'verify',
    detail:
      'Re-fetches every evidence URL and checks the quoted claim is really on the page, plus deterministic consistency rules (e.g. “buildable now” cannot coexist with a partner gate).',
  },
  {
    name: 'repair',
    detail:
      'Apps the verifier flags get researched again as a second pass, with the verifier’s objections fed back into the prompt. Pass 1 is kept for the accuracy comparison.',
  },
  {
    name: 'sample-check',
    detail:
      'A stratified human-checked sample scores field-level accuracy for both passes — the honest before/after.',
  },
  {
    name: 'analyze',
    detail:
      'Deterministic aggregation (no LLM): distributions, per-category rates, blocker taxonomy, easy-win and outreach lists that power this page.',
  },
]

export function AgentSection({ analysis }: { analysis: Analysis }) {
  const usage = analysis.llm_usage
  return (
    <section id="agent" className="border-y border-zinc-200 bg-white">
      <div className="mx-auto max-w-6xl scroll-mt-20 px-6 py-14">
        <h2 className="text-2xl font-semibold tracking-tight text-zinc-900">The agent</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-600">
          No app was researched by hand. A resumable Python pipeline
          (<code className="rounded bg-zinc-100 px-1 font-mono text-xs">agent/</code> in the repo)
          does the searching, reading, and structured extraction; every web response is cached to
          disk so runs are reproducible, and every LLM call is usage-logged.
        </p>
        <ol className="mt-8 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {STAGES.map((stage, index) => (
            <li key={stage.name} className="rounded-xl border border-zinc-200 bg-zinc-50 p-5">
              <p className="font-mono text-xs text-zinc-400">{String(index + 1).padStart(2, '0')}</p>
              <h3 className="mt-1 font-mono text-sm font-semibold text-zinc-900">
                agent {stage.name}
              </h3>
              <p className="mt-2 text-xs leading-relaxed text-zinc-600">{stage.detail}</p>
            </li>
          ))}
        </ol>
        <div className="mt-6 flex flex-wrap items-center gap-x-8 gap-y-2 rounded-xl border border-zinc-200 bg-zinc-50 px-5 py-4 text-xs text-zinc-600">
          <span>
            <strong className="font-semibold text-zinc-900">{usage.calls}</strong> LLM calls
          </span>
          <span>
            <strong className="font-semibold text-zinc-900">{formatTokens(usage.prompt_tokens)}</strong>{' '}
            input tokens
          </span>
          <span>
            <strong className="font-semibold text-zinc-900">{formatTokens(usage.completion_tokens)}</strong>{' '}
            output tokens
          </span>
          <span>
            total LLM cost{' '}
            <strong className="font-semibold text-zinc-900">{formatCost(usage.cost_usd)}</strong>
          </span>
        </div>
        <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-5">
          <h3 className="text-sm font-semibold text-amber-900">Where a human was still needed</h3>
          <ul className="mt-2 list-disc space-y-1.5 pl-5 text-xs leading-relaxed text-amber-900/90">
            <li>
              Designing the extraction schema and the verifier’s consistency rules — the agent
              fills the schema, it does not get to redefine it.
            </li>
            <li>
              Hand-checking the stratified accuracy sample against primary docs (the numbers in the
              verification section below).
            </li>
            <li>
              Adjudicating the genuinely ambiguous cases the agent surfaced as low-confidence, and
              sanity-reading surprising claims (e.g. official MCP servers) before publishing.
            </li>
          </ul>
        </div>
      </div>
    </section>
  )
}
