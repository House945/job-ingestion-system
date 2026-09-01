import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { JobsTable } from './JobsTable'
import type { Job } from '../types/api'

function job(overrides: Partial<Job> = {}): Job {
  return {
    source_index: 0,
    title: 'Backend Engineer',
    company: 'NextGen Systems',
    description: 'Build APIs.',
    city: 'Austin',
    region: 'TX',
    country: 'united_states',
    country_label: 'United States',
    is_remote: false,
    employment_type: 'full_time',
    salary: { amount: 145000, currency: 'USD', unit: 'annual' },
    comparable_annual_usd: 145000,
    posting_date: '2023-10-03',
    warnings: [],
    ...overrides,
  }
}

const noop = () => undefined

describe('JobsTable', () => {
  it('renders a row per posting', () => {
    render(
      <JobsTable
        jobs={[job(), job({ source_index: 1, title: 'Data Scientist' })]}
        pending={false}
        searchTerm=""
        onClearSearch={noop}
      />,
    )

    expect(screen.getByText('Backend Engineer')).toBeInTheDocument()
    expect(screen.getByText('Data Scientist')).toBeInTheDocument()
  })

  it('keeps an hourly rate visibly hourly', () => {
    render(
      <JobsTable
        jobs={[job({ salary: { amount: 62.5, currency: 'USD', unit: 'hourly' } })]}
        pending={false}
        searchTerm=""
        onClearSearch={noop}
      />,
    )

    expect(screen.getByText('$62.50')).toBeInTheDocument()
    expect(screen.getByText('/hr')).toBeInTheDocument()
  })

  it('shows a dash instead of an empty cell when the date is missing', () => {
    render(
      <JobsTable
        jobs={[job({ posting_date: null })]}
        pending={false}
        searchTerm=""
        onClearSearch={noop}
      />,
    )

    expect(screen.getAllByText('—').length).toBeGreaterThan(0)
  })

  it('shows a dash when there is no salary at all', () => {
    render(
      <JobsTable
        jobs={[job({ salary: null })]}
        pending={false}
        searchTerm=""
        onClearSearch={noop}
      />,
    )

    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('names the search term in the empty state and offers a way out', async () => {
    const onClearSearch = vi.fn()
    render(
      <JobsTable jobs={[]} pending={false} searchTerm="plumber" onClearSearch={onClearSearch} />,
    )

    expect(screen.getByText(/plumber/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Clear search' })).toBeInTheDocument()
  })

  it('does not offer to clear a search that was never entered', () => {
    render(<JobsTable jobs={[]} pending={false} searchTerm="" onClearSearch={noop} />)

    expect(screen.queryByRole('button', { name: 'Clear search' })).toBeNull()
  })
})