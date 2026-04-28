'use client'

import { motion } from 'framer-motion'
import { PHASE_LABELS } from '@/lib/types'

const PHASES = [1, 2, 3, 4, 5]

interface Props { activePhase: number }

export default function PhaseRail({ activePhase }: Props) {
  return (
    <div className="flex items-center gap-0 px-4">
      {PHASES.map((phase, i) => {
        const isDone = phase < activePhase
        const isActive = phase === activePhase
        const isPending = phase > activePhase

        return (
          <div key={phase} className="flex items-center">
            {/* Connector line */}
            {i > 0 && (
              <div
                className="h-px w-8 sm:w-12 transition-all duration-500"
                style={{ background: isDone ? '#c9a84c' : '#2a2a2a' }}
              />
            )}

            {/* Dot + label */}
            <div className="flex flex-col items-center gap-1">
              <div className="relative flex items-center justify-center">
                {/* Pulsing ring on active */}
                {isActive && (
                  <motion.div
                    className="absolute rounded-full"
                    style={{ background: '#c9a84c', width: 20, height: 20 }}
                    animate={{ scale: [1, 1.8, 1], opacity: [0.4, 0, 0.4] }}
                    transition={{ duration: 1.6, repeat: Infinity }}
                  />
                )}
                <motion.div
                  className="rounded-full transition-all duration-300"
                  style={{
                    width: isActive ? 12 : 8,
                    height: isActive ? 12 : 8,
                    background: isDone ? '#c9a84c' : isActive ? '#c9a84c' : '#2a2a2a',
                    border: isPending ? '1px solid #333' : 'none',
                  }}
                />
              </div>
              <span
                className="text-xs hidden sm:block"
                style={{
                  color: isActive ? '#c9a84c' : isDone ? '#888' : '#333',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                {PHASE_LABELS[phase]}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
