import type { CountryOption, Job, JobQuery, RejectedJob } from '../types/api'

/**
 * Requests go to /api, which the dev server proxies to the backend.
 * The frontend never holds a backend address.
 */
const BASE = '/api'

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${BASE}${path}`, { signal })

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return (await response.json()) as T
}

export function buildJobsPath(query: JobQuery): string {
  const params = new URLSearchParams()

  if (query.search.trim()) params.set('search', query.search.trim())
  if (query.country) params.set('country', query.country)
  if (query.sortBy) {
    params.set('sort_by', query.sortBy)
    params.set('order', query.order)
  }

  const suffix = params.toString()
  return suffix ? `/jobs?${suffix}` : '/jobs'
}

export function fetchJobs(query: JobQuery, signal?: AbortSignal): Promise<Job[]> {
  return get<Job[]>(buildJobsPath(query), signal)
}

export function fetchRejectedJobs(signal?: AbortSignal): Promise<RejectedJob[]> {
  return get<RejectedJob[]>('/jobs/rejected', signal)
}

export function fetchCountries(signal?: AbortSignal): Promise<CountryOption[]> {
  return get<CountryOption[]>('/countries', signal)
}