import { useEffect, useState } from 'react'

import { fetchRejectedJobs } from '../api/client'
import type { RejectedJob } from '../types/api'

interface RejectedState {
  jobs: RejectedJob[]
  pending: boolean
  error: string | null
}

export function useRejectedJobs(): RejectedState {
  const [state, setState] = useState<RejectedState>({
    jobs: [],
    pending: true,
    error: null,
  })

  useEffect(() => {
    const controller = new AbortController()

    fetchRejectedJobs(controller.signal)
      .then((jobs) => setState({ jobs, pending: false, error: null }))
      .catch((cause: unknown) => {
        // An aborted request is normal operation, not a failure.
        if (controller.signal.aborted) return
        setState({
          jobs: [],
          pending: false,
          error: cause instanceof Error ? cause.message : 'Request failed',
        })
      })

    return () => controller.abort()
  }, [])

  return state
}