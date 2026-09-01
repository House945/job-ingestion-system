import { useLayoutEffect, useRef, useState } from 'react'

export interface Segment {
  id: string
  label: string
  count: number | null
}

interface Props {
  segments: Segment[]
  selected: string
  onSelect: (id: string) => void
}

/**
 * Two-way switch with a sliding indicator.
 *
 * Deliberately not a `tablist`: the full ARIA tabs pattern expects arrow-key
 * navigation, a roving tabindex and an associated tabpanel, and declaring the
 * roles without them announces behaviour the control does not have. Two
 * buttons with `aria-pressed` describe what this actually is.
 *
 * The action commits on click so keyboard users reach it. Press feedback is
 * immediate regardless, because it lives in CSS `:active` rather than in a
 * pointer handler.
 */
export function SegmentedControl({ segments, selected, onSelect }: Props) {
  const container = useRef<HTMLDivElement>(null)
  const [indicator, setIndicator] = useState({ left: 0, width: 0 })

  useLayoutEffect(() => {
    const node = container.current?.querySelector<HTMLElement>(
      `[data-segment="${selected}"]`,
    )
    if (!node) return
    setIndicator({ left: node.offsetLeft, width: node.offsetWidth })
  }, [selected, segments])

  return (
    <div className="segmented" ref={container}>
      <span
        className="segmented-indicator"
        aria-hidden="true"
        style={{
          width: `${indicator.width}px`,
          transform: `translateX(${indicator.left - 2}px)`,
        }}
      />
      {segments.map((segment) => (
        <button
          key={segment.id}
          type="button"
          data-segment={segment.id}
          aria-pressed={segment.id === selected}
          className="segment"
          onClick={() => onSelect(segment.id)}
        >
          {segment.label}
          {segment.count !== null && (
            <span className="segment-count">{segment.count}</span>
          )}
        </button>
      ))}
    </div>
  )
}