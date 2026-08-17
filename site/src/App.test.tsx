import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import App from './App'
import { apps } from './lib/data'

describe('App', () => {
  it('renders the headline sections', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/100 apps/i)
    expect(screen.getByRole('heading', { name: /the patterns/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /all 100 apps/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /the agent/i })).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: /how the numbers were verified/i }),
    ).toBeInTheDocument()
  })

  it('renders a row for every app', () => {
    render(<App />)
    for (const app of apps.slice(0, 5)) {
      expect(screen.getByRole('button', { name: new RegExp(app.app) })).toBeInTheDocument()
    }
  })

  it('shows the filter controls', () => {
    render(<App />)
    expect(screen.getByLabelText('Search apps')).toBeInTheDocument()
    expect(screen.getByLabelText('Filter by category')).toBeInTheDocument()
    expect(screen.getByLabelText('Filter by verdict')).toBeInTheDocument()
  })
})
