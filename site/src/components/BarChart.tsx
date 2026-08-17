import type { BarDatum } from '../lib/stats'
import { TONE_DOTS } from '../lib/labels'

interface BarChartProps {
  data: BarDatum[]
  total?: number
  title: string
  subtitle?: string
}

export function BarChart({ data, total, title, subtitle }: BarChartProps) {
  const max = Math.max(...data.map((d) => d.value), 1)
  const denominator = total ?? data.reduce((sum, d) => sum + d.value, 0)
  return (
    <figure className="rounded-xl border border-zinc-200 bg-white p-5">
      <figcaption className="mb-4">
        <h3 className="text-sm font-semibold text-zinc-900">{title}</h3>
        {subtitle ? <p className="mt-0.5 text-xs text-zinc-500">{subtitle}</p> : null}
      </figcaption>
      <ul className="space-y-2.5">
        {data.map((d) => (
          <li key={d.label} className="grid grid-cols-[9rem_1fr_3.5rem] items-center gap-3 text-xs">
            <span className="truncate text-zinc-600" title={d.label}>
              {d.label}
            </span>
            <span className="h-4 rounded bg-zinc-100">
              <span
                className={`block h-4 rounded ${TONE_DOTS[d.tone ?? 'muted']}`}
                style={{ width: `${Math.max((d.value / max) * 100, d.value ? 4 : 0)}%` }}
              />
            </span>
            <span className="text-right font-mono text-zinc-500">
              {d.value}
              <span className="text-zinc-400"> · {denominator ? Math.round((d.value / denominator) * 100) : 0}%</span>
            </span>
          </li>
        ))}
      </ul>
    </figure>
  )
}
