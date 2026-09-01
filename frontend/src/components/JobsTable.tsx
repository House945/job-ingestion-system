import { ABSENT, formatDate, formatLocation, formatSalary } from '../lib/format'
import type { Job } from '../types/api'

interface Props {
  jobs: Job[]
  pending: boolean
  searchTerm: string
  onClearSearch: () => void
}

export function JobsTable({ jobs, pending, searchTerm, onClearSearch }: Props) {
  if (jobs.length === 0 && !pending) {
    return (
      <div className="table-wrap">
        <div className="empty">
          <p>
            {searchTerm
              ? `No approved postings match “${searchTerm}”.`
              : 'No approved postings to show.'}
          </p>
          {searchTerm && (
            <button type="button" className="button" onClick={onClearSearch}>
              Clear search
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="table-wrap" data-pending={pending}>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Posted</th>
            <th style={{ textAlign: 'right' }}>Compensation</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <JobRow key={job.source_index} job={job} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

function JobRow({ job }: { job: Job }) {
  const salary = formatSalary(job.salary)
  const salaryWarnings = job.warnings.filter(
    (w) => w.includes('salary') || w.includes('currency'),
  )
  const inferred = salaryWarnings.length > 0

  return (
    <tr>
      <td className="cell-title">{job.title}</td>
      <td>{job.company}</td>
      <td className="cell-muted">{formatLocation(job)}</td>
      <td className="cell-muted">{formatDate(job.posting_date)}</td>
      <td className="cell-salary">
        {salary ? (
          <span className={inferred ? 'inferred' : undefined} title={salaryWarnings.join('\n')}>
            {salary.amount}
            <span className="salary-unit">{salary.unit}</span>
          </span>
        ) : (
          <span className="absent">{ABSENT}</span>
        )}
      </td>
    </tr>
  )
}