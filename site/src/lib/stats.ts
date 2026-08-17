import type { AccessModel, Analysis, AppResult, Verdict } from '../types'

export interface TableFilters {
  category: string
  verdict: string
  access: string
  auth: string
  search: string
}

export const EMPTY_FILTERS: TableFilters = {
  category: 'all',
  verdict: 'all',
  access: 'all',
  auth: 'all',
  search: '',
}

export function isSelfServe(access: AccessModel): boolean {
  return access === 'self_serve_free' || access === 'self_serve_trial'
}

export function filterApps(apps: AppResult[], filters: TableFilters): AppResult[] {
  const query = filters.search.trim().toLowerCase()
  return apps.filter((app) => {
    if (filters.category !== 'all' && app.category !== filters.category) return false
    if (filters.verdict !== 'all' && app.verdict !== filters.verdict) return false
    if (filters.access !== 'all' && app.access !== filters.access) return false
    if (filters.auth !== 'all' && !app.auth_methods.some((m) => m === filters.auth)) return false
    if (
      query &&
      !app.app.toLowerCase().includes(query) &&
      !app.one_liner.toLowerCase().includes(query)
    ) {
      return false
    }
    return true
  })
}

export function categoriesOf(apps: AppResult[]): string[] {
  return [...new Set(apps.map((a) => a.category))].sort()
}

export interface BarDatum {
  label: string
  value: number
  tone?: 'good' | 'warn' | 'bad' | 'muted'
}

export function distributionToBars(
  distribution: Record<string, number>,
  labels: Record<string, string>,
  tones?: Record<string, 'good' | 'warn' | 'bad' | 'muted'>,
): BarDatum[] {
  return Object.entries(distribution).map(([key, value]) => ({
    label: labels[key] ?? key,
    value,
    tone: tones?.[key] ?? 'muted',
  }))
}

export function pct(part: number, whole: number): string {
  if (!whole) return '0%'
  return `${Math.round((part / whole) * 100)}%`
}

export function verdictOf(apps: AppResult[], verdict: Verdict): AppResult[] {
  return apps.filter((a) => a.verdict === verdict)
}

export function headlineStats(analysis: Analysis): { label: string; value: string }[] {
  return [
    { label: 'apps researched', value: String(analysis.total_apps) },
    { label: 'self-serve credentials', value: pct(Math.round(analysis.self_serve_rate * analysis.total_apps), analysis.total_apps) },
    { label: 'buildable today', value: pct(Math.round(analysis.buildable_now_rate * analysis.total_apps), analysis.total_apps) },
    { label: 'gated in some form', value: pct(Math.round(analysis.gated_rate * analysis.total_apps), analysis.total_apps) },
    { label: 'official MCP servers', value: String(analysis.official_mcp_apps.length) },
  ]
}

export function formatCost(usd: number): string {
  return `$${usd.toFixed(2)}`
}

export function formatTokens(count: number): string {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}k`
  return String(count)
}
