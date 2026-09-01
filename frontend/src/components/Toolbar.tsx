import type { CountryOption, JobQuery, SortField, SortOrder } from '../types/api'

interface Props {
  query: JobQuery
  countries: CountryOption[]
  onChange: (next: JobQuery) => void
}

export function Toolbar({ query, countries, onChange }: Props) {
  const toggleOrder = () => {
    const order: SortOrder = query.order === 'desc' ? 'asc' : 'desc'
    onChange({ ...query, order })
  }

  return (
    <div className="toolbar">
      <input
        className="field search"
        type="search"
        value={query.search}
        placeholder="Search titles"
        aria-label="Search titles"
        onChange={(event) => onChange({ ...query, search: event.target.value })}
      />

      <select
        className="field"
        value={query.country}
        aria-label="Filter by country"
        onChange={(event) => onChange({ ...query, country: event.target.value })}
      >
        <option value="">All countries</option>
        {countries.map((country) => (
          <option key={country.value} value={country.value}>
            {country.label}
          </option>
        ))}
      </select>

      <select
        className="field"
        value={query.sortBy}
        aria-label="Sort by"
        onChange={(event) =>
          onChange({ ...query, sortBy: event.target.value as SortField | '' })
        }
      >
        <option value="">Feed order</option>
        <option value="salary">Salary</option>
        <option value="posting_date">Posting date</option>
      </select>

      <button
        type="button"
        className="field direction"
        disabled={!query.sortBy}
        aria-label={query.order === 'desc' ? 'Sort ascending' : 'Sort descending'}
        onPointerDown={toggleOrder}
      >
        {query.order === 'desc' ? '↓' : '↑'}
      </button>
    </div>
  )
}