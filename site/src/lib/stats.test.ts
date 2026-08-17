import { describe, expect, it } from 'vitest'

import type { AppResult } from '../types'
import {
  categoriesOf,
  distributionToBars,
  EMPTY_FILTERS,
  filterApps,
  formatCost,
  formatTokens,
  headlineStats,
  isSelfServe,
  pct,
} from './stats'
import type { Analysis } from '../types'

export function makeApp(overrides: Partial<AppResult> = {}): AppResult {
  return {
    app_id: 1,
    app: 'Pipedrive',
    category: 'CRM and Sales',
    one_liner: 'Sales CRM',
    auth_methods: ['oauth2', 'api_key'],
    access: 'self_serve_free',
    api_styles: ['rest'],
    api_breadth: 'broad',
    official_mcp: false,
    verdict: 'buildable_now',
    blocker: null,
    confidence: 0.9,
    evidence: [{ claim: 'c', url: 'https://x.com', quote: 'q' }],
    notes: '',
    pass_number: 1,
    researched_at: '2026-08-17T00:00:00+00:00',
    ...overrides,
  }
}

function makeAnalysis(overrides: Partial<Analysis> = {}): Analysis {
  return {
    total_apps: 100,
    auth_distribution: { oauth2: 60, api_key: 70 },
    access_distribution: { self_serve_free: 70, partner_gated: 10 },
    verdict_distribution: { buildable_now: 60, gated: 20 },
    api_breadth_distribution: { broad: 50 },
    api_style_distribution: { rest: 90 },
    by_category: {},
    self_serve_rate: 0.7,
    gated_rate: 0.2,
    buildable_now_rate: 0.6,
    official_mcp_apps: ['Slack'],
    easy_wins: ['Slack'],
    needs_outreach: [],
    blocker_taxonomy: { 'paid plan required': 8 },
    top_blockers_raw: {},
    verification: {},
    llm_usage: { calls: 10, prompt_tokens: 1000, completion_tokens: 500, cost_usd: 1.5 },
    ...overrides,
  }
}

describe('isSelfServe', () => {
  it('treats free and trial as self-serve', () => {
    expect(isSelfServe('self_serve_free')).toBe(true)
    expect(isSelfServe('self_serve_trial')).toBe(true)
    expect(isSelfServe('partner_gated')).toBe(false)
    expect(isSelfServe('unknown')).toBe(false)
  })
})

describe('filterApps', () => {
  const apps = [
    makeApp({ app_id: 1, app: 'Pipedrive', category: 'CRM and Sales', one_liner: 'Sales CRM' }),
    makeApp({
      app_id: 2,
      app: 'Slack',
      category: 'Communications and Messaging',
      verdict: 'gated',
      access: 'partner_gated',
      auth_methods: ['bearer_token'],
      one_liner: 'Team messaging',
    }),
    makeApp({
      app_id: 3,
      app: 'Stripe',
      category: 'Finance and Fintech',
      auth_methods: ['api_key'],
      one_liner: 'Payments infrastructure',
    }),
  ]

  it('filters by category', () => {
    const result = filterApps(apps, { ...EMPTY_FILTERS, category: 'Finance and Fintech' })
    expect(result.map((a) => a.app)).toEqual(['Stripe'])
  })

  it('filters by verdict and access', () => {
    expect(filterApps(apps, { ...EMPTY_FILTERS, verdict: 'gated' }).map((a) => a.app)).toEqual(['Slack'])
    expect(filterApps(apps, { ...EMPTY_FILTERS, access: 'partner_gated' })).toHaveLength(1)
  })

  it('filters by auth method membership', () => {
    const result = filterApps(apps, { ...EMPTY_FILTERS, auth: 'oauth2' })
    expect(result.map((a) => a.app)).toEqual(['Pipedrive'])
  })

  it('searches name and one-liner case-insensitively', () => {
    expect(filterApps(apps, { ...EMPTY_FILTERS, search: 'sales crm' })).toHaveLength(1)
    expect(filterApps(apps, { ...EMPTY_FILTERS, search: 'SLACK' })).toHaveLength(1)
    expect(filterApps(apps, { ...EMPTY_FILTERS, search: 'zzz' })).toHaveLength(0)
  })
})

describe('categoriesOf', () => {
  it('returns sorted unique categories', () => {
    const apps = [makeApp({ category: 'B' }), makeApp({ category: 'A' }), makeApp({ category: 'B' })]
    expect(categoriesOf(apps)).toEqual(['A', 'B'])
  })
})

describe('distributionToBars', () => {
  it('maps keys through labels with fallback', () => {
    const bars = distributionToBars({ oauth2: 3, mystery: 1 }, { oauth2: 'OAuth 2.0' })
    expect(bars).toEqual([
      { label: 'OAuth 2.0', value: 3, tone: 'muted' },
      { label: 'mystery', value: 1, tone: 'muted' },
    ])
  })
})

describe('pct', () => {
  it('formats percentages and guards division by zero', () => {
    expect(pct(1, 3)).toBe('33%')
    expect(pct(0, 0)).toBe('0%')
  })
})

describe('headlineStats', () => {
  it('derives counts from rates and totals', () => {
    const stats = headlineStats(makeAnalysis())
    const byLabel = Object.fromEntries(stats.map((s) => [s.label, s.value]))
    expect(byLabel['apps researched']).toBe('100')
    expect(byLabel['self-serve credentials']).toBe('70%')
    expect(byLabel['buildable today']).toBe('60%')
    expect(byLabel['official MCP servers']).toBe('1')
  })
})

describe('formatting helpers', () => {
  it('formats cost and tokens', () => {
    expect(formatCost(1.5)).toBe('$1.50')
    expect(formatTokens(500)).toBe('500')
    expect(formatTokens(2500)).toBe('2.5k')
    expect(formatTokens(2_500_000)).toBe('2.5M')
  })
})
