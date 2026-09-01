import { useEffect, useState } from 'react'

import { fetchJobs } from '../api/client'
import type { Job, JobQuery } from '../types/api'

interface Loaded {
  query: JobQuery
  jobs: Job[]
  error: string | null
}

interface JobsState {
  jobs: Job[]
  pending: boolean
  error: string | null
}

function sameQuery(a: JobQuery, b: JobQuery): boolean {
  return (
    a.search === b.search &&
    a.country === b.country &&
    a.sortBy === b.sortBy &&
    a.order === b.order
  )
}

/**
 * Fetch approved jobs for a query.
 *
 * Pending is derived, not stored: a request is in flight exactly when the last
 * loaded result belongs to a different query than the current one. That avoids
 * a synchronous state write inside the effect, and it makes the two values
 * impossible to disagree.
 *
 * Previous results stay on screen while a new request is in flight. Clearing
 * them first would flash an empty table on every keystroke, which reads as a
 * bug even when it lasts 150ms.
 */
export function useJobs(query: JobQuery): JobsState {
  const [loaded, setLoaded] = useState<Loaded | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    fetchJobs(query, controller.signal)
      .then((jobs) => setLoaded({ query, jobs, error: null }))
      .catch((cause: unknown) => {
        if (controller.signal.aborted) return
        setLoaded({
          query,
          jobs: [],
          error: cause instanceof Error ? cause.message : 'Request failed',
        })
      })

    return () => controller.abort()
  }, [query])

  return {
    jobs: loaded?.jobs ?? [],
    pending: loaded === null || !sameQuery(loaded.query, query),
    error: loaded?.error ?? null,
  }
}