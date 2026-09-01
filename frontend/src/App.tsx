import { useMemo, useState } from 'react'

import { JobsTable } from './components/JobsTable'
import { RejectedTable } from './components/RejectedTable'
import { SegmentedControl } from './components/SegmentedControl'
import { Toolbar } from './components/Toolbar'
import { useCountries } from './hooks/useCountries'
import { useDebouncedValue } from './hooks/useDebouncedValue'
import { useJobs } from './hooks/useJobs'
import { useRejectedJobs } from './hooks/useRejectedJobs'
import type { JobQuery } from './types/api'

const EMPTY_QUERY: JobQuery = { search: '', country: '', sortBy: '', order: 'desc' }

export default function App() {
  const [tab, setTab] = useState('approved')
  const [query, setQuery] = useState<JobQuery>(EMPTY_QUERY)

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

  const countries = useCountries()
  const { jobs, pending, error } = useJobs(effectiveQuery)
  const rejected = useRejectedJobs()

  return (
    <div className="page">
      <header className="header">
        <h1 className="title">Job feed</h1>
        <p className="subtitle">
          Postings ingested from the source feed, with the reasons any were held back.
        </p>

        <SegmentedControl
          selected={tab}
          onSelect={setTab}
          segments={[
            { id: 'approved', label: 'Approved', count: jobs.length },
            { id: 'rejected', label: 'Rejected', count: rejected.jobs.length },
          ]}
        />

        {tab === 'approved' && (
          <Toolbar query={query} countries={countries} onChange={setQuery} />
        )}
      </header>

      {error ? (
        <div className="table-wrap">
          <p className="message">
            The feed could not be loaded. Check that the API is running, then reload.
          </p>
        </div>
      ) : tab === 'approved' ? (
        <JobsTable
          jobs={jobs}
          pending={pending}
          searchTerm={debouncedSearch}
          onClearSearch={() => setQuery({ ...query, search: '' })}
        />
      ) : (
        <RejectedTable jobs={rejected.jobs} pending={rejected.pending} error={rejected.error} />
      )}
    </div>
  )
}