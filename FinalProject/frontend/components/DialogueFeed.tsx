'use client'

import { useEffect, useRef } from 'react'
import type { Turn, ToolCallEvent } from '@/lib/types'
import MessageBubble from './MessageBubble'
import ToolCallCard from './ToolCallCard'

interface Props {
  turns: Turn[]
  toolCalls: ToolCallEvent[]
  extraBottomPad?: boolean
}

export default function DialogueFeed({ turns, toolCalls, extraBottomPad = false }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [turns.length, toolCalls.length])

  // Interleave tool calls after the Phase 4 crunch turn
  const crunchTurnIndex = turns.findIndex(t => t.phase === 4 && t.role === 'Number Crunch')

  return (
    <div className={`flex-1 overflow-y-auto px-4 py-4 ${extraBottomPad ? 'pb-20' : ''}`}>
      <div className="flex flex-col gap-4">
        {turns.map((turn, i) => (
          <div key={i}>
            <MessageBubble turn={turn} index={i} />
            {/* Show tool call card just before the Number Crunch turn */}
            {i === crunchTurnIndex - 1 && toolCalls.length > 0 && (
              <div className="mt-4 -mx-4">
                <ToolCallCard toolCalls={toolCalls} />
              </div>
            )}
          </div>
        ))}

        {/* Show tool calls if the crunch turn hasn't arrived yet */}
        {crunchTurnIndex === -1 && toolCalls.length > 0 && (
          <div className="-mx-4">
            <ToolCallCard toolCalls={toolCalls} />
          </div>
        )}
      </div>
      <div ref={bottomRef} />
    </div>
  )
}
