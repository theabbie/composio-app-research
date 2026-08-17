import analysisRaw from '../data/analysis.json'
import appsRaw from '../data/apps.json'
import type { Analysis, AppResult } from '../types'

const ACCESS = new Set([
  'self_serve_free',
  'self_serve_trial',
  'paid_plan_required',
  'admin_approval',
  'partner_gated',
  'contact_sales',
  'no_public_program',
  'unknown',
])
const VERDICTS = new Set(['buildable_now', 'buildable_with_work', 'gated', 'no_api', 'unknown'])
const BREADTH = new Set(['broad', 'moderate', 'narrow', 'none', 'unknown'])

export function validateApp(row: unknown): AppResult {
  const r = row as AppResult
  const problems: string[] = []
  if (typeof r.app_id !== 'number') problems.push('app_id')
  if (typeof r.app !== 'string' || !r.app) problems.push('app')
  if (typeof r.category !== 'string' || !r.category) problems.push('category')
  if (!ACCESS.has(r.access)) problems.push(`access=${String(r.access)}`)
  if (!VERDICTS.has(r.verdict)) problems.push(`verdict=${String(r.verdict)}`)
  if (!BREADTH.has(r.api_breadth)) problems.push(`api_breadth=${String(r.api_breadth)}`)
  if (!Array.isArray(r.evidence) || r.evidence.length === 0) problems.push('evidence')
  if (problems.length) {
    throw new Error(`invalid app row ${JSON.stringify(row).slice(0, 80)}: ${problems.join(', ')}`)
  }
  return r
}

export function loadApps(): AppResult[] {
  if (!Array.isArray(appsRaw)) throw new Error('apps.json must be an array')
  return appsRaw.map(validateApp)
}

export function loadAnalysis(): Analysis {
  const analysis = analysisRaw as Analysis
  if (typeof analysis.total_apps !== 'number' || analysis.total_apps === 0) {
    throw new Error('analysis.json missing total_apps')
  }
  return analysis
}

export const apps: AppResult[] = loadApps()
export const analysis: Analysis = loadAnalysis()
