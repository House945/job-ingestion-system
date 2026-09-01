import type { Job, Salary } from '../types/api'

/** Shown wherever a value is genuinely absent. Never an empty cell. */
export const ABSENT = '—'

const UNIT_SUFFIX: Record<string, string> = {
  annual: '/yr',
  hourly: '/hr',
}

export interface FormattedSalary {
  amount: string
  unit: string
}

/**
 * Format a salary without ever implying the wrong unit.
 *
 * An hourly rate and an annual salary sit in the same column, so the unit is
 * part of the value, not a detail. Hourly rates keep two decimals because
 * cents matter at that magnitude; annual figures never show them.
 */
export function formatSalary(salary: Salary | null): FormattedSalary | null {
  if (!salary) return null

  const fractionDigits = salary.unit === 'hourly' ? 2 : 0
  const amount = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: salary.currency,
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(salary.amount)

  return { amount, unit: UNIT_SUFFIX[salary.unit] ?? '' }
}

export function formatDate(value: string | null): string {
  if (!value) return ABSENT

  const parsed = new Date(`${value}T00:00:00`)
  if (Number.isNaN(parsed.getTime())) return ABSENT

  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(parsed)
}

export function formatLocation(job: Job): string {
  const parts = [job.city, job.region].filter(Boolean)
  const place = parts.join(', ')

  if (place && job.is_remote) return `${place} · Remote`
  if (place) return place
  if (job.is_remote) return 'Remote'

  return job.country_label
}