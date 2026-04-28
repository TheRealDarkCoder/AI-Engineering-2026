'use client'

import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { useSharkTank } from '@/lib/useSharkTank'
import IdeaInput from './IdeaInput'
import DebateStage from './DebateStage'
import VerdictScreen from './VerdictScreen'

export default function SharkTankApp() {
  const { state, submit, reset } = useSharkTank()
  const [verdictOpen, setVerdictOpen] = useState(true)

  const handleReset = () => {
    setVerdictOpen(true)
    reset()
  }

  const showVerdictOverlay = state.appPhase === 'done' && !!state.verdict

  return (
    <div className="relative h-full overflow-hidden">
      <AnimatePresence mode="wait">
        {state.appPhase === 'idle' && (
          <IdeaInput key="input" onSubmit={submit} />
        )}
        {(state.appPhase === 'running' || (state.appPhase === 'done' && !state.verdict)) && (
          <DebateStage key="debate" state={state} />
        )}
        {showVerdictOverlay && (
          <DebateStage key="debate-done" state={state} compactBarShown={!verdictOpen} />
        )}
      </AnimatePresence>

      {showVerdictOverlay && state.verdict && (
        <VerdictScreen
          verdictText={state.verdict}
          open={verdictOpen}
          onCollapse={() => setVerdictOpen(false)}
          onExpand={() => setVerdictOpen(true)}
          onReset={handleReset}
        />
      )}
    </div>
  )
}
