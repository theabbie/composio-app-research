import { pct } from '../lib/stats'
import type { Analysis } from '../types'

const FIELD_LABELS: Record<string, string> = {
  one_liner: 'One-liner',
  auth_methods: 'Auth methods',
  access: 'Self-serve vs gated',
  api_surface: 'API surface',
  verdict: 'Verdict',
  all_fields_correct: 'Whole row correct',
}

export function Verification({ analysis }: { analysis: Analysis }) {
  const verification = analysis.verification
  const human = verification.human_sample
  const rows = verification.human_sample_rows ?? []

  return (
    <section id="verification" className="mx-auto max-w-6xl scroll-mt-20 px-6 py-14">
      <h2 className="text-2xl font-semibold tracking-tight text-zinc-900">
        How the numbers were verified
      </h2>
      <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-600">
        Accuracy mattered more than coverage, so the pipeline verifies itself two ways: an
        automated loop re-fetches every cited URL and checks the quoted claim is literally on the
        page, and a human hand-checked a stratified sample against primary docs. First-pass answers
        were kept so the improvement is measurable, not vibes.
      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {(['pass1', 'pass2'] as const).map((pass) => {
          const stats = verification[pass]
          if (!stats) return null
          return (
            <div key={pass} className="rounded-xl border border-zinc-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-zinc-900">
                Automated verification · {pass === 'pass1' ? 'pass 1 (initial)' : 'pass 2 (after repair)'}
              </h3>
              <dl className="mt-3 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-xs text-zinc-500">rows with zero evidence errors</dt>
                  <dd className="mt-0.5 text-xl font-semibold tabular-nums text-zinc-900">
                    {stats.clean}/{stats.apps}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-zinc-500">evidence quotes found verbatim on cited page</dt>
                  <dd className="mt-0.5 text-xl font-semibold tabular-nums text-zinc-900">
                    {pct(stats.quotes_found, stats.quotes_checked)}
                  </dd>
                </div>
              </dl>
            </div>
          )
        })}
      </div>

      {human ? (
        <div className="mt-4 overflow-x-auto rounded-xl border border-zinc-200 bg-white">
          <table className="w-full min-w-[36rem] text-left text-sm">
            <thead>
              <tr className="border-b border-zinc-200 text-xs uppercase tracking-wide text-zinc-500">
                <th className="px-5 py-3 font-medium">Human-checked sample (n={human.sample_size})</th>
                <th className="px-5 py-3 font-medium">Pass 1 accuracy</th>
                <th className="px-5 py-3 font-medium">Pass 2 accuracy</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(FIELD_LABELS).map(([key, label]) => (
                <tr key={key} className="border-b border-zinc-100 last:border-0">
                  <td className="px-5 py-2.5 font-medium text-zinc-800">{label}</td>
                  <td className="px-5 py-2.5 tabular-nums text-zinc-700">
                    {pct(Math.round((human.pass1[key] ?? 0) * 100), 100)}
                  </td>
                  <td className="px-5 py-2.5 tabular-nums text-zinc-700">
                    {pct(Math.round((human.pass2[key] ?? 0) * 100), 100)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {rows.some((row) => row.notes) ? (
        <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-5">
          <h3 className="text-sm font-semibold text-rose-900">Honest misses</h3>
          <ul className="mt-2 list-disc space-y-1.5 pl-5 text-xs leading-relaxed text-rose-900/90">
            {rows
              .filter((row) => row.notes)
              .map((row) => (
                <li key={row.app_id}>
                  <strong className="font-medium">{row.app}:</strong> {row.notes}
                </li>
              ))}
          </ul>
        </div>
      ) : null}
    </section>
  )
}
