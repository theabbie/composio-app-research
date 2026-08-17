export type AuthMethod =
  | 'oauth2'
  | 'api_key'
  | 'basic'
  | 'bearer_token'
  | 'session_cookie'
  | 'none_public'
  | 'other'
  | 'unknown'

export type AccessModel =
  | 'self_serve_free'
  | 'self_serve_trial'
  | 'paid_plan_required'
  | 'admin_approval'
  | 'partner_gated'
  | 'contact_sales'
  | 'no_public_program'
  | 'unknown'

export type ApiStyle = 'rest' | 'graphql' | 'soap' | 'mixed' | 'none' | 'unknown'

export type ApiBreadth = 'broad' | 'moderate' | 'narrow' | 'none' | 'unknown'

export type Verdict =
  | 'buildable_now'
  | 'buildable_with_work'
  | 'gated'
  | 'no_api'
  | 'unknown'

export interface Evidence {
  claim: string
  url: string
  quote: string
}

export interface AppResult {
  app_id: number
  app: string
  category: string
  one_liner: string
  auth_methods: AuthMethod[]
  access: AccessModel
  api_styles: ApiStyle[]
  api_breadth: ApiBreadth
  official_mcp: boolean
  verdict: Verdict
  blocker: string | null
  confidence: number
  evidence: Evidence[]
  notes: string
  pass_number: number
  researched_at: string
}

export interface CategoryStats {
  apps: number
  self_serve: number
  gated: number
  buildable_now: number
  self_serve_rate: number
  buildable_rate: number
}

export interface VerificationPass {
  apps: number
  clean: number
  quotes_checked: number
  quotes_found: number
}

export interface AccuracySummary {
  [field: string]: number
}

export interface HumanSampleRow {
  app_id: number
  app: string
  fields_correct_pass1: Record<string, boolean>
  fields_correct_pass2: Record<string, boolean>
  notes: string
}

export interface VerificationInfo {
  pass1?: VerificationPass
  pass2?: VerificationPass
  human_sample?: {
    sample_size: number
    pass1: AccuracySummary
    pass2: AccuracySummary
  }
  human_sample_rows?: HumanSampleRow[]
}

export interface OutreachItem {
  app: string
  category: string
  access: string
  blocker: string | null
}

export interface Analysis {
  total_apps: number
  auth_distribution: Record<string, number>
  access_distribution: Record<string, number>
  verdict_distribution: Record<string, number>
  api_breadth_distribution: Record<string, number>
  api_style_distribution: Record<string, number>
  by_category: Record<string, CategoryStats>
  self_serve_rate: number
  gated_rate: number
  buildable_now_rate: number
  official_mcp_apps: string[]
  easy_wins: string[]
  needs_outreach: OutreachItem[]
  blocker_taxonomy: Record<string, number>
  top_blockers_raw: Record<string, number>
  verification: VerificationInfo
  llm_usage: {
    calls: number
    prompt_tokens: number
    completion_tokens: number
    cost_usd: number
    by_purpose?: Record<string, number>
  }
}
