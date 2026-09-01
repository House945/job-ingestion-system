export type SalaryUnit = 'annual' | 'hourly' | 'unknown'

export interface Salary {
  amount: number
  currency: string
  unit: SalaryUnit
}

export interface Job {
  source_index: number
  title: string
  company: string
  description: string
  city: string | null
  region: string | null
  country: string
  country_label: string
  is_remote: boolean
  employment_type: string
  salary: Salary | null
  comparable_annual_usd: number | null
  posting_date: string | null
  warnings: string[]
}

export interface RejectionReason {
  code: string
  message: string
}

export interface RejectedJob {
  source_index: number
  title: string | null
  company: string | null
  country_label: string | null
  salary_text: string | null
  reasons: RejectionReason[]
  warnings: string[]
}

export interface CountryOption {
  value: string
  label: string
}

export type SortField = 'salary' | 'posting_date'
export type SortOrder = 'asc' | 'desc'

export interface JobQuery {
  search: string
  country: string
  sortBy: SortField | ''
  order: SortOrder
}