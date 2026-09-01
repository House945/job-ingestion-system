import { describe, expect, it } from 'vitest'

import { ABSENT, formatDate, formatSalary } from './format'

describe('formatSalary', () => {
  it('formats an annual salary without decimals', () => {
    const result = formatSalary({ amount: 145000, currency: 'USD', unit: 'annual' })

    expect(result).toEqual({ amount: '$145,000', unit: '/yr' })
  })

  it('formats an hourly rate with cents and an hourly suffix', () => {
    const result = formatSalary({ amount: 62.5, currency: 'USD', unit: 'hourly' })

    expect(result).toEqual({ amount: '$62.50', unit: '/hr' })
  })

  it('never presents an hourly rate as an annual figure', () => {
    const hourly = formatSalary({ amount: 62.5, currency: 'USD', unit: 'hourly' })

    expect(hourly?.unit).not.toBe('/yr')
  })

  it('returns null when there is no salary', () => {
    expect(formatSalary(null)).toBeNull()
  })
})

describe('formatDate', () => {
  it('formats an ISO date', () => {
    expect(formatDate('2023-10-03')).toBe('Oct 3, 2023')
  })

  it('shows a dash when the date is missing', () => {
    expect(formatDate(null)).toBe(ABSENT)
    expect(formatDate('')).toBe(ABSENT)
  })

  it('shows a dash when the date is unparseable', () => {
    expect(formatDate('not-a-date')).toBe(ABSENT)
  })
})