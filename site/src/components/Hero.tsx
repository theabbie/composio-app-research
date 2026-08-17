import type { Analysis } from '../types'
import { headlineStats } from '../lib/stats'

export function Hero({ analysis }: { analysis: Analysis }) {
  return (
    <header className="border-b border-zinc-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-14">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
          Composio take-home · AI Product Ops
        </p>
        <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight text-zinc-900">
          100 apps, researched by an agent: which ones can become agent toolkits today?
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-zinc-600">
          An autonomous pipeline researched every app below — auth model, self-serve vs gated
          access, API surface, official MCP presence, and a buildability verdict, each backed by a
          cited docs quote. This page is the findings, the patterns, the agent, and the proof that
          the numbers can be trusted.
        </p>
        <dl className="mt-10 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-zinc-200 bg-zinc-200 sm:grid-cols-5">
          {headlineStats(analysis).map((stat) => (
            <div key={stat.label} className="bg-white px-5 py-4">
              <dt className="text-[11px] font-medium uppercase tracking-wide text-zinc-500">
                {stat.label}
              </dt>
              <dd className="mt-1 text-2xl font-semibold tabular-nums text-zinc-900">
                {stat.value}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </header>
  )
}
