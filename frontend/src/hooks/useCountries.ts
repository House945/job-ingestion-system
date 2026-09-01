import { useEffect, useState } from 'react'

import { fetchCountries } from '../api/client'
import type { CountryOption } from '../types/api'

export function useCountries(): CountryOption[] {
  const [countries, setCountries] = useState<CountryOption[]>([])

  useEffect(() => {
    const controller = new AbortController()
    fetchCountries(controller.signal)
      .then(setCountries)
      .catch(() => undefined)
    return () => controller.abort()
  }, [])

  return countries
}