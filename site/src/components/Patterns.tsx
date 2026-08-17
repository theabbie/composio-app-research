import { ACCESS_LABELS, ACCESS_TONES, AUTH_LABELS, VERDICT_LABELS, VERDICT_TONES } from '../lib/labels'
import { distributionToBars, pct } from '../lib/stats'
import type { Analysis } from '../types'
import { BarChart } from './BarChart'

interface PatternsProps {
  analysis: Analysis
}

export function Patterns({ analysis }: PatternsProps) {
  const authBars = distributionToBars(analysis.auth_distribution, AUTH_LABELS)
  const verdictBars = distributionToBars(analysis.verdict_distribution, VERDICT_LABELS, VERDICT_TONES)
  const accessBars = distributionToBars(analysis.access_distribution, ACCESS_LABELS, ACCESS_TONES)
  const blockerBars = distributionToBars(analysis.blocker_taxonomy, {})
  const categories = Object.entries(analysis.by_category).sort(
    (a, b) => b[1].self_serve_rate - a[1].self_serve_rate,
  )

  return (
    <section id="patterns" className="mx-auto max-w-6xl scroll-mt-20 px-6 py-14">
      <h2 className="text-2xl font-semibold tracking-tight text-zinc-900">The patterns</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-zinc-200 bg-white p-5 md:col-span-2">
          <h3 className="text-sm font-semibold text-zinc-900">Headlines</h3>
          <ul className="mt-3 space-y-3 text-sm leading-relaxed text-zinc-700">
            <li className="flex gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-zinc-900" />
              <span>
                <strong className="font-medium text-zinc-900">API keys and OAuth 2.0 dominate.</strong>{' '}
                Between them they cover the overwhelming majority of apps; OAuth appears wherever a
                marketplace or multi-tenant story exists, API keys wherever the API came first.
              </span>
            </li>
            <li className="flex gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-zinc-900" />
              <span>
                <strong className="font-medium text-zinc-900">
                  {pct(Math.round(analysis.self_serve_rate * analysis.total_apps), analysis.total_apps)}{' '}
                  of the 100 are self-serve.
                </strong>{' '}
                A developer can get credentials today for most of this list; gates concentrate in
                finance, enterprise CRM, and ads platforms.
              </span>
            </li>
            <li className="flex gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-zinc-900" />
              <span>
                <strong className="font-medium text-zinc-900">
                  The most common blocker is not auth — it is access.
                </strong>{' '}
                Partner programs, sales gates, and paid-plan requirements outnumber missing APIs.
                Where an API exists, it is usually REST and usually broad.
              </span>
            </li>
            <li className="flex gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-zinc-900" />
              <span>
                <strong className="font-medium text-zinc-900">
                  {analysis.official_mcp_apps.length} apps already ship an official MCP server.
                </strong>{' '}
                These are the zero-build wins: wrap, don&apos;t rebuild.
              </span>
            </li>
          </ul>
        </div>
        <BarChart data={verdictBars} title="Buildability verdicts" subtitle="Could this be an agent toolkit today?" />
        <BarChart data={authBars} title="Auth methods" subtitle="An app can support several" />
        <BarChart data={accessBars} title="How a developer gets credentials" />
        <BarChart data={blockerBars} title="What blocks the rest" subtitle="Main blocker, bucketed" />
      </div>

      <div className="mt-4 overflow-x-auto rounded-xl border border-zinc-200 bg-white">
        <table className="w-full min-w-[42rem] text-left text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-xs uppercase tracking-wide text-zinc-500">
              <th className="px-5 py-3 font-medium">Category</th>
              <th className="px-5 py-3 font-medium">Apps</th>
              <th className="px-5 py-3 font-medium">Self-serve</th>
              <th className="px-5 py-3 font-medium">Gated</th>
              <th className="px-5 py-3 font-medium">Buildable now</th>
            </tr>
          </thead>
          <tbody>
            {categories.map(([category, stats]) => (
              <tr key={category} className="border-b border-zinc-100 last:border-0">
                <td className="px-5 py-2.5 font-medium text-zinc-800">{category}</td>
                <td className="px-5 py-2.5 tabular-nums text-zinc-600">{stats.apps}</td>
                <td className="px-5 py-2.5 tabular-nums text-emerald-700">
                  {stats.self_serve} <span className="text-zinc-400">({pct(stats.self_serve, stats.apps)})</span>
                </td>
                <td className="px-5 py-2.5 tabular-nums text-rose-700">{stats.gated}</td>
                <td className="px-5 py-2.5 tabular-nums text-zinc-700">
                  {stats.buildable_now}{' '}
                  <span className="text-zinc-400">({pct(stats.buildable_now, stats.apps)})</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
