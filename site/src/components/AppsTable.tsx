import { useMemo, useState } from 'react'

import { ACCESS_LABELS, ACCESS_TONES, AUTH_LABELS, BREADTH_LABELS, VERDICT_LABELS, VERDICT_TONES } from '../lib/labels'
import { categoriesOf, EMPTY_FILTERS, filterApps, type TableFilters } from '../lib/stats'
import type { AppResult } from '../types'
import { Badge } from './Badge'

interface AppsTableProps {
  apps: AppResult[]
}

function EvidenceList({ app }: { app: AppResult }) {
  return (
    <div className="space-y-3 px-5 py-4">
      <p className="text-sm text-zinc-600">{app.one_liner}</p>
      {app.blocker ? (
        <p className="text-sm text-zinc-700">
          <span className="font-medium text-zinc-900">Main blocker:</span> {app.blocker}
        </p>
      ) : null}
      {app.notes ? <p className="text-sm text-zinc-500">{app.notes}</p> : null}
      <ul className="space-y-2">
        {app.evidence.map((item, index) => (
          <li key={index} className="rounded-lg border border-zinc-200 bg-white p-3 text-xs">
            <p className="font-medium text-zinc-800">{item.claim}</p>
            <blockquote className="mt-1 border-l-2 border-zinc-300 pl-2 text-zinc-500">
              “{item.quote}”
            </blockquote>
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="mt-1 inline-block break-all font-mono text-[11px] text-zinc-500 underline decoration-zinc-300 underline-offset-2 hover:text-zinc-900"
            >
              {item.url}
            </a>
          </li>
        ))}
      </ul>
      <p className="text-[11px] text-zinc-400">
        researched {app.researched_at.slice(0, 10)} · pass {app.pass_number} · confidence{' '}
        {app.confidence.toFixed(2)}
      </p>
    </div>
  )
}

const selectClass =
  'rounded-lg border border-zinc-200 bg-white px-2.5 py-1.5 text-xs text-zinc-700 focus:border-zinc-400 focus:outline-none'

export function AppsTable({ apps }: AppsTableProps) {
  const [filters, setFilters] = useState<TableFilters>(EMPTY_FILTERS)
  const [open, setOpen] = useState<number | null>(null)
  const categories = useMemo(() => categoriesOf(apps), [apps])
  const filtered = useMemo(() => filterApps(apps, filters), [apps, filters])

  const set = (patch: Partial<TableFilters>) => setFilters((prev) => ({ ...prev, ...patch }))

  return (
    <section id="matrix" className="mx-auto max-w-6xl scroll-mt-20 px-6 py-14">
      <h2 className="text-2xl font-semibold tracking-tight text-zinc-900">All 100 apps</h2>
      <p className="mt-2 text-sm text-zinc-600">
        Every row cites the docs it stands on — expand a row to see the quoted evidence.
      </p>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <input
          type="search"
          placeholder="Search apps…"
          value={filters.search}
          onChange={(event) => set({ search: event.target.value })}
          className={`${selectClass} w-44`}
          aria-label="Search apps"
        />
        <select value={filters.category} onChange={(e) => set({ category: e.target.value })} className={selectClass} aria-label="Filter by category">
          <option value="all">All categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
        <select value={filters.verdict} onChange={(e) => set({ verdict: e.target.value })} className={selectClass} aria-label="Filter by verdict">
          <option value="all">All verdicts</option>
          {Object.entries(VERDICT_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select value={filters.access} onChange={(e) => set({ access: e.target.value })} className={selectClass} aria-label="Filter by access model">
          <option value="all">All access models</option>
          {Object.entries(ACCESS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select value={filters.auth} onChange={(e) => set({ auth: e.target.value })} className={selectClass} aria-label="Filter by auth method">
          <option value="all">All auth methods</option>
          {Object.entries(AUTH_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <span className="text-xs tabular-nums text-zinc-500">
          {filtered.length} of {apps.length}
        </span>
      </div>

      <div className="mt-4 overflow-hidden rounded-xl border border-zinc-200 bg-zinc-50">
        <ul className="divide-y divide-zinc-200">
          {filtered.map((app) => {
            const expanded = open === app.app_id
            return (
              <li key={app.app_id}>
                <button
                  type="button"
                  onClick={() => setOpen(expanded ? null : app.app_id)}
                  aria-expanded={expanded}
                  className="flex w-full flex-wrap items-center gap-x-4 gap-y-1 px-5 py-3 text-left hover:bg-white focus:bg-white focus:outline-none"
                >
                  <span className="w-8 shrink-0 font-mono text-xs text-zinc-400">
                    {String(app.app_id).padStart(3, '0')}
                  </span>
                  <span className="min-w-36 flex-1 font-medium text-zinc-900">{app.app}</span>
                  <span className="hidden w-44 truncate text-xs text-zinc-500 lg:inline">
                    {app.category}
                  </span>
                  <span className="flex flex-wrap items-center gap-1.5">
                    {app.auth_methods.slice(0, 3).map((method) => (
                      <Badge key={method} label={AUTH_LABELS[method]} tone="muted" />
                    ))}
                    <Badge label={ACCESS_LABELS[app.access]} tone={ACCESS_TONES[app.access]} />
                    <Badge label={BREADTH_LABELS[app.api_breadth]} tone="muted" />
                    {app.official_mcp ? <Badge label="MCP" tone="good" /> : null}
                    <Badge label={VERDICT_LABELS[app.verdict]} tone={VERDICT_TONES[app.verdict]} />
                  </span>
                </button>
                {expanded ? (
                  <div className="border-t border-zinc-200 bg-zinc-50">
                    <EvidenceList app={app} />
                  </div>
                ) : null}
              </li>
            )
          })}
        </ul>
        {filtered.length === 0 ? (
          <p className="px-5 py-8 text-center text-sm text-zinc-500">No apps match the filters.</p>
        ) : null}
      </div>
    </section>
  )
}
