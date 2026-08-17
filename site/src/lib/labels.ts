import type { AccessModel, ApiBreadth, AuthMethod, Verdict } from '../types'

export const AUTH_LABELS: Record<AuthMethod, string> = {
  oauth2: 'OAuth 2.0',
  api_key: 'API key',
  basic: 'Basic auth',
  bearer_token: 'Bearer token',
  session_cookie: 'Session cookie',
  none_public: 'None (public)',
  other: 'Other',
  unknown: 'Unknown',
}

export const ACCESS_LABELS: Record<AccessModel, string> = {
  self_serve_free: 'Self-serve (free)',
  self_serve_trial: 'Self-serve (trial)',
  paid_plan_required: 'Paid plan required',
  admin_approval: 'Admin approval',
  partner_gated: 'Partner-gated',
  contact_sales: 'Contact sales',
  no_public_program: 'No public program',
  unknown: 'Unknown',
}

export const VERDICT_LABELS: Record<Verdict, string> = {
  buildable_now: 'Buildable now',
  buildable_with_work: 'Buildable with work',
  gated: 'Gated',
  no_api: 'No API',
  unknown: 'Unknown',
}

export const BREADTH_LABELS: Record<ApiBreadth, string> = {
  broad: 'Broad',
  moderate: 'Moderate',
  narrow: 'Narrow',
  none: 'None',
  unknown: 'Unknown',
}

export type Tone = 'good' | 'warn' | 'bad' | 'muted'

export const VERDICT_TONES: Record<Verdict, Tone> = {
  buildable_now: 'good',
  buildable_with_work: 'warn',
  gated: 'bad',
  no_api: 'bad',
  unknown: 'muted',
}

export const ACCESS_TONES: Record<AccessModel, Tone> = {
  self_serve_free: 'good',
  self_serve_trial: 'good',
  paid_plan_required: 'warn',
  admin_approval: 'warn',
  partner_gated: 'bad',
  contact_sales: 'bad',
  no_public_program: 'bad',
  unknown: 'muted',
}

export const TONE_CLASSES: Record<Tone, string> = {
  good: 'bg-emerald-50 text-emerald-800 border-emerald-200',
  warn: 'bg-amber-50 text-amber-800 border-amber-200',
  bad: 'bg-rose-50 text-rose-800 border-rose-200',
  muted: 'bg-zinc-100 text-zinc-600 border-zinc-200',
}

export const TONE_DOTS: Record<Tone, string> = {
  good: 'bg-emerald-500',
  warn: 'bg-amber-500',
  bad: 'bg-rose-500',
  muted: 'bg-zinc-400',
}
