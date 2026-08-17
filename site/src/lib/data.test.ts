import { describe, expect, it } from 'vitest'

import { analysis, apps, validateApp } from './data'

describe('bundled dataset', () => {
  it('contains valid app rows', () => {
    expect(apps.length).toBeGreaterThan(0)
    for (const app of apps) {
      expect(() => validateApp(app)).not.toThrow()
    }
  })

  it('has analysis totals consistent with the apps list', () => {
    expect(analysis.total_apps).toBe(apps.length)
  })

  it('every app has at least one evidence URL', () => {
    for (const app of apps) {
      expect(app.evidence.length).toBeGreaterThan(0)
      for (const item of app.evidence) {
        expect(item.url).toMatch(/^https?:\/\//)
      }
    }
  })

  it('unknown verdicts are rare', () => {
    const unknown = apps.filter((a) => a.verdict === 'unknown').length
    expect(unknown / apps.length).toBeLessThan(0.35)
  })
})

describe('validateApp', () => {
  it('rejects rows with bad enums', () => {
    const [first] = apps
    expect(first).toBeDefined()
    const bad = { ...first!, access: 'free-ish' }
    expect(() => validateApp(bad)).toThrow(/access/)
  })
})
