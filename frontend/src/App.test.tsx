import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import App from './App'
import type { RejectedJob } from './types/api'

const rejected: RejectedJob = {
  source_index: 19,
  title: 'Junior Developer',
  company: 'Staffing Solutions',
  country_label: 'Canada',
  salary_text: '80,000 USD/yr',
  reasons: [{ code: 'STAFFING', message: 'posting is from a staffing firm' }],
  warnings: [],
}

vi.mock('./api/client', () => ({
  fetchJobs: vi.fn(() => Promise.reject(new Error('Request failed: 500'))),
  fetchRejectedJobs: vi.fn(() => Promise.resolve([rejected])),
  fetchCountries: vi.fn(() => Promise.resolve([])),
}))

describe('App', () => {
  it('still shows rejected postings when the approved query has failed', async () => {
    render(<App />)

    expect(await screen.findByText(/could not be loaded/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /Rejected/ }))

    expect(await screen.findByText('Junior Developer')).toBeInTheDocument()
    expect(screen.queryByText(/could not be loaded/)).toBeNull()
  })
})
