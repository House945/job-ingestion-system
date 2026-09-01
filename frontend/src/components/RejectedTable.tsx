import { ABSENT } from '../lib/format'
import type { RejectedJob } from '../types/api'

interface Props {
  jobs: RejectedJob[]
  pending: boolean
}

/**
 * Rejected postings need their own columns.
 *
 * A rejected posting may have no title, no location and no parseable salary,
 * so it cannot share a row shape with an approved one. What it always has is
 * reasons, which is why they get the widest column.
 */
export function RejectedTable({ jobs, pending }: Props) {
  if (pending) {
    return <div className="table-wrap"><p className="message">Loading…</p></div>
  }

  if (jobs.length === 0) {
    return (
      <div className="table-wrap">
        <div className="empty">
          <p>Every posting in this feed was approved.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Compensation</th>
            <th>Why it was rejected</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.source_index}>
              <td className="cell-title">
                {job.title ?? <span className="absent">No title</span>}
              </td>
              <td>{job.company ?? <span className="absent">{ABSENT}</span>}</td>
              <td className="cell-muted">
                {job.country_label ?? <span className="absent">{ABSENT}</span>}
              </td>
              <td className="cell-muted">
                {job.salary_text ?? <span className="absent">{ABSENT}</span>}
              </td>
              <td>
                <div className="chips">
                  {job.reasons.map((reason) => (
                    <span key={reason.code} className="chip" title={reason.message}>
                      {reason.code}
                    </span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}