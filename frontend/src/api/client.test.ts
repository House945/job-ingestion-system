import { describe, expect, it } from 'vitest'

import { buildJobsPath } from './client'

const base = { search: '', country: '', sortBy: '' as const, order: 'desc' as const }

describe('buildJobsPath', () => {
  it('omits empty parameters', () => {
    expect(buildJobsPath(base)).toBe('/jobs')
  })

  it('trims the search term', () => {
    expect(buildJobsPath({ ...base, search: '  engineer  ' })).toBe('/jobs?search=engineer')
  })

  it('sends order only alongside a sort field', () => {
    expect(buildJobsPath({ ...base, order: 'asc' })).toBe('/jobs')
    expect(buildJobsPath({ ...base, sortBy: 'salary', order: 'asc' })).toBe(
      '/jobs?sort_by=salary&order=asc',
    )
  })

  it('includes the country filter', () => {
    expect(buildJobsPath({ ...base, country: 'canada' })).toBe('/jobs?country=canada')
  })
})