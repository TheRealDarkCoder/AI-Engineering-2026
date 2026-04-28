'use client'

import { motion, AnimatePresence } from 'framer-motion'

interface Props { label: string; activePhase: number }

const PHASE_COLORS: Record<number, string> = {
  1: '#34d399', 2: '#f87171', 3: '#60a5fa', 4: '#a78bfa', 5: '#c9a84c',
}

export default function StatusPill({ label, activePhase }: Props) {
  const color = PHASE_COLORS[activePhase] ?? '#555'

  return (
    <div className="flex items-center justify-center">
      <div
        className="flex items-center gap-2 px-4 py-1.5 rounded-full"
        style={{ background: '#111', border: '1px solid #1e1e1e' }}
      >
        {/* Spinning orb */}
        <motion.div
          className="rounded-full"
          style={{ width: 6, height: 6, background: color, flexShrink: 0 }}
          animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Status label with cross-fade */}
        <div className="relative overflow-hidden" style={{ height: '1.2em' }}>
          <AnimatePresence mode="wait">
            <motion.span
              key={label}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="text-xs absolute inset-0 flex items-center whitespace-nowrap"
              style={{ color: '#888', fontFamily: 'var(--font-mono)' }}
            >
              {label || 'Initialising…'}
            </motion.span>
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
