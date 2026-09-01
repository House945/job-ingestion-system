import { useEffect, useState } from 'react'

import { fetchJobs } from '../api/client'
import type { Job, JobQuery } from '../types/api'

interface JobsState {
  jobs: Job[]
  pending: boolean
  error: string | null
}

/**
 * Fetch approved jobs for a query.
 *
 * Previous results stay on screen while a new request is in flight. Clearing
 * them first would flash an empty table on every keystroke, which reads as a
 * bug even when it lasts 150ms.
 */
export function useJobs(query: JobQuery): JobsState {
  const [jobs, setJobs] = useState<Job[]>([])
  const [pending, setPending] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    setPending(true)

    fetchJobs(query, controller.signal)
      .then((result) => {
        setJobs(result)
        setError(null)
      })
      .catch((cause: unknown) => {
        if (controller.signal.aborted) return
        setError(cause instanceof Error ? cause.message : 'Request failed')
      })
      .finally(() => {
        if (!controller.signal.aborted) setPending(false)
      })

    return () => controller.abort()
  }, [query.search, query.country, query.sortBy, query.order])

  return { jobs, pending, error }
}