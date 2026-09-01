import { useEffect, useState } from 'react'

import { fetchRejectedJobs } from '../api/client'
import type { RejectedJob } from '../types/api'

export function useRejectedJobs(): { jobs: RejectedJob[]; pending: boolean } {
  const [jobs, setJobs] = useState<RejectedJob[]>([])
  const [pending, setPending] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    fetchRejectedJobs(controller.signal)
      .then(setJobs)
      .catch(() => undefined)
      .finally(() => {
        if (!controller.signal.aborted) setPending(false)
      })

    return () => controller.abort()
  }, [])

  return { jobs, pending }
}