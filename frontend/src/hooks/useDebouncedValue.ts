import { useEffect, useState } from 'react'

/**
 * Delay a value without delaying the input that produced it.
 *
 * The text field stays controlled and updates on every keystroke; only the
 * value that triggers a request is delayed. Debouncing the control itself
 * would make typing feel laggy, which is the wrong thing to optimize.
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs)
    return () => window.clearTimeout(timer)
  }, [value, delayMs])

  return debounced
}