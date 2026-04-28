'use client'

import { motion } from 'framer-motion'
import type { AgentName } from '@/lib/types'
import { AGENT_COLORS, AGENT_ROLES } from '@/lib/types'

const AVATARS: Record<AgentName, React.ReactNode> = {
  Visionary: (
    <motion.svg
      width="36" height="36" viewBox="0 0 36 36"
      animate={{ rotate: 360 }}
      transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
    >
      <polygon points="18,4 32,30 4,30" fill="#34d399" opacity="0.9" />
    </motion.svg>
  ),
  Skeptic: (
    <motion.svg
      width="36" height="36" viewBox="0 0 36 36"
      animate={{ scale: [1, 1.12, 1] }}
      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
    >
      <polygon points="18,3 22,14 34,14 24,21 28,33 18,26 8,33 12,21 2,14 14,14" fill="#f87171" opacity="0.9" />
    </motion.svg>
  ),
  Engineer: (
    <motion.svg
      width="36" height="36" viewBox="0 0 36 36"
      animate={{ rotate: -360 }}
      transition={{ duration: 16, repeat: Infinity, ease: 'linear' }}
    >
      <polygon points="18,3 30,10.5 30,25.5 18,33 6,25.5 6,10.5" fill="none" stroke="#60a5fa" strokeWidth="2" />
      <circle cx="18" cy="18" r="4" fill="#60a5fa" />
    </motion.svg>
  ),
  Analyst: (
    <motion.svg width="36" height="36" viewBox="0 0 36 36">
      <motion.circle
        cx="18" cy="18" r="14"
        fill="none" stroke="#a78bfa" strokeWidth="1.5" opacity="0.4"
        animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0.8, 0.4] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
      />
      <circle cx="18" cy="18" r="8" fill="none" stroke="#a78bfa" strokeWidth="2" />
      <circle cx="18" cy="18" r="3" fill="#a78bfa" />
    </motion.svg>
  ),
}

interface Props {
  name: AgentName
  isActive: boolean
  isDimmed: boolean
}

export default function AgentCard({ name, isActive, isDimmed }: Props) {
  const color = AGENT_COLORS[name]
  const role = AGENT_ROLES[name]

  return (
    <motion.div
      animate={{
        scale: isActive ? 1.06 : 1,
        opacity: isDimmed ? 0.3 : 1,
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 24 }}
      className="flex flex-col items-center gap-1 sm:gap-2 px-1 sm:px-4 py-2 sm:py-3 rounded-xl flex-1 min-w-0"
      style={{
        background: isActive ? '#181818' : '#111111',
        border: `1px solid ${isActive ? color : '#1e1e1e'}`,
        boxShadow: isActive ? `0 0 20px ${color}30` : 'none',
      }}
    >
      <div className="w-6 h-6 sm:w-9 sm:h-9 flex items-center justify-center shrink-0 [&>svg]:w-full [&>svg]:h-full">
        {AVATARS[name]}
      </div>
      <div className="text-center min-w-0 w-full">
        <p
          className="font-semibold text-sm truncate"
          style={{ color, fontFamily: 'var(--font-display)' }}
        >
          {name}
        </p>
        <p className="text-[10px] sm:text-xs truncate" style={{ color: '#555' }}>
          {role}
        </p>
      </div>
    </motion.div>
  )
}
