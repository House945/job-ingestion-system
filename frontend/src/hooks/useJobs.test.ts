import { act, renderHook } from '@testing-library/react'
import { useMemo } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { fetchJobs } from '../api/client'
import type { JobQuery } from '../types/api'
import { useDebouncedValue } from './useDebouncedValue'
import { useJobs } from './useJobs'

vi.mock('../api/client', () => ({
  fetchJobs: vi.fn(() => Promise.resolve([])),
}))

const BASE: JobQuery = { search: '', country: '', sortBy: '', order: 'desc' }

/**
 * The wiring from App: a debounced search term feeding useJobs.
 *
 * The query object arrives with a new identity on every keystroke, exactly as
 * it does from App's state. The memo has to depend on the fields rather than
 * the object, or the effect refires before the debounce has moved.
 */
function useSearchedJobs(query: JobQuery) {
  const debouncedSearch = useDebouncedValue(query.search, 180)
  const effectiveQuery = useMemo(
    () => ({
      search: debouncedSearch,
      country: query.country,
      sortBy: query.sortBy,
      order: query.order,
    }),
    [debouncedSearch, query.country, query.sortBy, query.order],
  )

  return useJobs(effectiveQuery)
}

describe('useJobs', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('sends one request for a burst of keystrokes, not one per keystroke', async () => {
    const { rerender } = renderHook((query: JobQuery) => useSearchedJobs(query), {
      initialProps: BASE,
    })

    await act(async () => {
      await vi.advanceTimersByTimeAsync(200)
    })
    vi.mocked(fetchJobs).mockClear()

    for (const search of ['e', 'en', 'eng', 'engi']) {
      rerender({ ...BASE, search })
    }

    expect(fetchJobs).not.toHaveBeenCalled()

    await act(async () => {
      await vi.advanceTimersByTimeAsync(200)
    })

    expect(fetchJobs).toHaveBeenCalledTimes(1)
    expect(vi.mocked(fetchJobs).mock.calls[0][0].search).toBe('engi')
  })
})
