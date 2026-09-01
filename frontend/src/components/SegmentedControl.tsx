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
 * Selection commits on pointer-down rather than click, so the indicator starts
 * moving the instant the control is pressed.
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
    <div className="segmented" role="tablist" ref={container}>
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
          role="tab"
          data-segment={segment.id}
          aria-selected={segment.id === selected}
          className="segment"
          onPointerDown={() => onSelect(segment.id)}
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