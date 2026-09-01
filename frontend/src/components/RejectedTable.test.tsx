import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { RejectedTable } from './RejectedTable'
import type { RejectedJob } from '../types/api'

const untitled: RejectedJob = {
  source_index: 19,
  title: null,
  company: 'OpsFlex',
  country_label: 'Remote / unspecified',
  salary_text: '40 USD/hr',
  reasons: [
    { code: 'TITLE', message: 'title is missing or empty' },
    { code: 'STAFFING', message: 'posting is from a staffing firm' },
  ],
  warnings: [],
}

describe('RejectedTable', () => {
  it('renders a posting that has no title', () => {
    render(<RejectedTable jobs={[untitled]} pending={false} error={null} />)

    expect(screen.getByText('No title')).toBeInTheDocument()
  })

  it('shows every rejection reason, not just the first', () => {
    render(<RejectedTable jobs={[untitled]} pending={false} error={null} />)

    expect(screen.getByText('TITLE')).toBeInTheDocument()
    expect(screen.getByText('STAFFING')).toBeInTheDocument()
  })

  it('explains an empty rejected tab rather than showing a blank table', () => {
    render(<RejectedTable jobs={[]} pending={false} error={null} />)

    expect(screen.getByText(/Every posting in this feed was approved/)).toBeInTheDocument()
  })

  it('reports a failure instead of claiming everything was approved', () => {
    render(<RejectedTable jobs={[]} pending={false} error="Request failed: 500" />)

    expect(screen.queryByText(/Every posting in this feed was approved/)).toBeNull()
    expect(screen.getByText(/could not be loaded/)).toBeInTheDocument()
  })
  it('does not claim anything while the request is still in flight', () => {
    render(<RejectedTable jobs={[]} pending={true} error={null} />)

    expect(screen.queryByText(/Every posting in this feed was approved/)).toBeNull()
  })
})