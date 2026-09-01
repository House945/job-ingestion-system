import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SegmentedControl } from './SegmentedControl'

const segments = [
  { id: 'approved', label: 'Approved', count: 10 },
  { id: 'rejected', label: 'Rejected', count: 10 },
]

describe('SegmentedControl', () => {
  it('switches on click', async () => {
    const onSelect = vi.fn()
    render(<SegmentedControl segments={segments} selected="approved" onSelect={onSelect} />)

    await userEvent.click(screen.getByRole('button', { name: /Rejected/ }))

    expect(onSelect).toHaveBeenCalledWith('rejected')
  })

  it('switches with the keyboard', async () => {
    const onSelect = vi.fn()
    render(<SegmentedControl segments={segments} selected="approved" onSelect={onSelect} />)

    await userEvent.tab()
    await userEvent.tab()
    await userEvent.keyboard('{Enter}')

    expect(onSelect).toHaveBeenCalledWith('rejected')
  })

  it('marks the current segment as pressed', () => {
    render(<SegmentedControl segments={segments} selected="approved" onSelect={() => undefined} />)

    expect(screen.getByRole('button', { name: /Approved/ })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
  })
})