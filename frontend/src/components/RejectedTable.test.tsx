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
    render(<RejectedTable jobs={[untitled]} pending={false} />)

    expect(screen.getByText('No title')).toBeInTheDocument()
  })

  it('shows every rejection reason, not just the first', () => {
    render(<RejectedTable jobs={[untitled]} pending={false} />)

    expect(screen.getByText('TITLE')).toBeInTheDocument()
    expect(screen.getByText('STAFFING')).toBeInTheDocument()
  })

  it('explains an empty rejected tab rather than showing a blank table', () => {
    render(<RejectedTable jobs={[]} pending={false} />)

    expect(screen.getByText(/Every posting in this feed was approved/)).toBeInTheDocument()
  })
})