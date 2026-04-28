'use client'

import type { AgentName, Turn } from '@/lib/types'
import AgentCard from './AgentCard'

const AGENTS: AgentName[] = ['Visionary', 'Skeptic', 'Engineer', 'Analyst']

interface Props {
  turns: Turn[]
  activePhase: number
}

export default function AgentRoster({ turns, activePhase }: Props) {
  const lastTurn = turns[turns.length - 1]
  const activeSpeaker: AgentName | null = lastTurn?.speaker ?? null

  return (
    <div className="flex gap-2 px-4">
      {AGENTS.map(name => (
        <AgentCard
          key={name}
          name={name}
          isActive={activeSpeaker === name}
          isDimmed={activeSpeaker !== null && activeSpeaker !== name}
        />
      ))}
    </div>
  )
}
