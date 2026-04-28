'use client'

import { motion } from 'framer-motion'
import type { SharkTankState } from '@/lib/useSharkTank'
import StatusPill from './StatusPill'
import PhaseRail from './PhaseRail'
import AgentRoster from './AgentRoster'
import DialogueFeed from './DialogueFeed'

interface Props {
  state: SharkTankState
  children?: React.ReactNode
  compactBarShown?: boolean
}

export default function DebateStage({ state, children, compactBarShown = false }: Props) {
  return (
    <motion.div
      className="h-full flex flex-col"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header bar */}
      <div
        className="flex items-center justify-between px-4 py-3 shrink-0"
        style={{ borderBottom: '1px solid #1e1e1e' }}
      >
        <div className="flex items-center gap-2">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <polygon points="9,1 17,16 1,16" fill="#c9a84c" />
          </svg>
          <span
            className="hidden sm:inline-block text-xs tracking-widest uppercase"
            style={{ color: '#555', fontFamily: 'var(--font-mono)' }}
          >
            Shark Tank
          </span>
        </div>

        <StatusPill label={state.currentStatus} activePhase={state.activePhase} />

        <div className="hidden sm:block w-24" /> {/* spacer for centering */}
      </div>

      {/* Phase progress */}
      <div
        className="px-4 py-3 shrink-0 flex items-center justify-center"
        style={{ borderBottom: '1px solid #1e1e1e' }}
      >
        <PhaseRail activePhase={state.activePhase} />
      </div>

      {/* Agent roster */}
      <div
        className="px-0 py-3 shrink-0"
        style={{ borderBottom: '1px solid #1e1e1e' }}
      >
        <AgentRoster turns={state.turns} activePhase={state.activePhase} />
      </div>

      {/* Idea chip */}
      {state.idea && (
        <div className="px-4 pt-3 shrink-0">
          <p
            className="text-xs px-3 py-1.5 rounded-full inline-block"
            style={{
              background: '#181818',
              border: '1px solid #2a2a2a',
              color: '#666',
              fontFamily: 'var(--font-mono)',
            }}
          >
            💡 {state.idea}
          </p>
        </div>
      )}

      {/* Dialogue feed — takes all remaining space; extra bottom padding when compact bar is present */}
      <DialogueFeed
        turns={state.turns}
        toolCalls={state.toolCalls}
        extraBottomPad={compactBarShown}
      />

      {/* Verdict overlay (rendered as child) */}
      {children}
    </motion.div>
  )
}
