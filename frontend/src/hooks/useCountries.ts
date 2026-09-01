import { useEffect, useState } from 'react'

import { fetchCountries } from '../api/client'
import type { CountryOption } from '../types/api'

export function useCountries(): CountryOption[] {
  const [countries, setCountries] = useState<CountryOption[]>([])

  useEffect(() => {
    const controller = new AbortController()
    fetchCountries(controller.signal)
      .then(setCountries)
      // A failed country list degrades to "All countries", which is a usable
      // state rather than a false statement. Unlike the rejected list, an
      // empty filter dropdown claims nothing that is not true.
      .catch(() => undefined)
    return () => controller.abort()
  }, [])

  return countries
}