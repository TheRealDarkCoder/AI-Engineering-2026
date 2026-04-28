'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { parseVerdict } from '@/lib/types'

const DECISION_COLOR: Record<string, string> = {
  FUNDED: '#22c55e',
  BANKRUPT: '#ef4444',
  CONDITIONAL: '#f59e0b',
}

function Confetti() {
  const particles = Array.from({ length: 28 }, (_, i) => {
    const angle = (i / 28) * 360
    const d = 140 + Math.random() * 80
    return {
      x: Math.cos((angle * Math.PI) / 180) * d,
      y: Math.sin((angle * Math.PI) / 180) * d,
      delay: Math.random() * 0.4,
      color: ['#22c55e', '#c9a84c', '#34d399', '#bbf7d0'][i % 4],
    }
  })
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
      {particles.map((p, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{ width: 6, height: 6, background: p.color }}
          initial={{ x: 0, y: 0, opacity: 0, scale: 0 }}
          animate={{ x: p.x, y: p.y, opacity: [0, 1, 1, 0], scale: [0, 1, 0.8, 0] }}
          transition={{ duration: 1.6, delay: p.delay, ease: 'easeOut' }}
        />
      ))}
    </div>
  )
}

interface Props {
  verdictText: string
  open: boolean
  onCollapse: () => void
  onExpand: () => void
  onReset: () => void
}

export default function VerdictScreen({ verdictText, open, onCollapse, onExpand, onReset }: Props) {
  const v = parseVerdict(verdictText)
  const color = DECISION_COLOR[v.decision] ?? '#c9a84c'
  const isFunded = v.decision === 'FUNDED'
  const isBankrupt = v.decision === 'BANKRUPT'

  return (
    <>
      {/* ── Full overlay ─────────────────────────────────────────── */}
      <AnimatePresence>
        {open && (
          <motion.div
            key="verdict-overlay"
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            style={{ backdropFilter: 'blur(12px)', background: 'rgba(8,8,8,0.88)' }}
          >
            {isBankrupt && (
              <motion.div
                className="fixed inset-0 pointer-events-none"
                style={{ background: 'radial-gradient(ellipse at center, transparent 40%, #ef444440 100%)' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: [0, 1, 0.4] }}
                transition={{ duration: 1.2 }}
              />
            )}

            <motion.div
              className="relative w-full max-w-lg rounded-2xl overflow-hidden"
              style={{ background: '#0e0e0e', border: `1px solid ${color}33` }}
              initial={{ scale: 0.85, opacity: 0, y: 20 }}
              animate={isBankrupt
                ? { scale: 1, opacity: 1, y: 0, x: [0, -6, 6, -5, 5, -3, 0] }
                : { scale: 1, opacity: 1, y: 0 }
              }
              exit={{ scale: 0.92, opacity: 0, y: 16 }}
              transition={isBankrupt
                ? { scale: { type: 'spring', stiffness: 300, damping: 20 }, x: { delay: 0.4, duration: 0.5 } }
                : { type: 'spring', stiffness: 280, damping: 22 }
              }
            >
              {isFunded && <Confetti />}

              <div className="h-1 w-full" style={{ background: color }} />

              <div className="p-4 sm:p-8">
                {/* Decision word */}
                <motion.div
                  className="text-center mb-6"
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 320, damping: 12, delay: 0.2 }}
                >
                  <p
                    className="text-4xl sm:text-6xl font-black tracking-wider"
                    style={{ color, fontFamily: 'var(--font-display)', textShadow: `0 0 40px ${color}60` }}
                  >
                    {v.decision || 'VERDICT'}
                  </p>
                  {v.offer && (
                    <motion.p
                      className="mt-2 text-lg font-medium"
                      style={{ color: '#f0f0f0', fontFamily: 'var(--font-display)' }}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 }}
                    >
                      {v.offer}
                    </motion.p>
                  )}
                </motion.div>

                <div className="h-px mb-5" style={{ background: '#1e1e1e' }} />

                <motion.div
                  className="flex flex-col gap-3 text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  {v.rationale && (
                    <div>
                      <p className="text-xs mb-1" style={{ color: '#555' }}>Rationale</p>
                      <p style={{ color: '#ccc' }}>{v.rationale}</p>
                    </div>
                  )}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-1">
                    {v.marketRisk && (
                      <div className="rounded-lg p-3" style={{ background: '#f8717115', border: '1px solid #f8717120' }}>
                        <p className="text-xs mb-1" style={{ color: '#f87171' }}>Market Risk</p>
                        <p className="text-xs" style={{ color: '#ccc' }}>{v.marketRisk}</p>
                      </div>
                    )}
                    {v.techRisk && (
                      <div className="rounded-lg p-3" style={{ background: '#60a5fa15', border: '1px solid #60a5fa20' }}>
                        <p className="text-xs mb-1" style={{ color: '#60a5fa' }}>Tech Risk</p>
                        <p className="text-xs" style={{ color: '#ccc' }}>{v.techRisk}</p>
                      </div>
                    )}
                  </div>
                  {v.financials && (
                    <div
                      className="rounded-lg p-3 text-xs"
                      style={{ background: '#111', border: '1px solid #222', fontFamily: 'var(--font-mono)', color: '#888' }}
                    >
                      {v.financials}
                    </div>
                  )}
                </motion.div>

                <div className="h-px my-6" style={{ background: '#1e1e1e' }} />

                {/* Action buttons */}
                <motion.div
                  className="flex flex-col sm:flex-row gap-2 sm:gap-3"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.9 }}
                >
                  <motion.button
                    onClick={onCollapse}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    className="flex-1 py-3 rounded-xl text-sm font-semibold"
                    style={{
                      background: '#181818',
                      border: `1px solid ${color}44`,
                      color: color,
                      fontFamily: 'var(--font-display)',
                      cursor: 'pointer',
                    }}
                  >
                    ↓ Review Transcript
                  </motion.button>
                  <motion.button
                    onClick={onReset}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    className="flex-1 py-3 rounded-xl text-sm font-semibold"
                    style={{
                      background: '#1a1a1a',
                      border: '1px solid #2a2a2a',
                      color: '#888',
                      fontFamily: 'var(--font-display)',
                      cursor: 'pointer',
                    }}
                  >
                    ↩ New Idea
                  </motion.button>
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Compact sticky bar ────────────────────────────────────── */}
      <AnimatePresence>
        {!open && (
          <motion.div
            key="verdict-bar"
            className="fixed bottom-0 left-0 right-0 z-40 px-4 pb-4"
            initial={{ y: 80, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 80, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 340, damping: 28 }}
          >
            <div
              className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 sm:py-3 rounded-2xl"
              style={{
                background: '#0e0e0e',
                border: `1px solid ${color}44`,
                boxShadow: `0 0 32px ${color}18`,
              }}
            >
              {/* Decision badge */}
              <div
                className="px-3 py-1 rounded-full text-xs font-black tracking-wider shrink-0"
                style={{
                  background: `${color}18`,
                  color,
                  border: `1px solid ${color}44`,
                  fontFamily: 'var(--font-display)',
                }}
              >
                {v.decision}
              </div>

              {/* Offer / financials summary */}
              <div className="flex-1 min-w-0">
                {v.offer && (
                  <p className="text-sm truncate" style={{ color: '#ddd', fontFamily: 'var(--font-display)' }}>
                    {v.offer}
                  </p>
                )}
                {v.financials && (
                  <p className="text-xs truncate" style={{ color: '#555', fontFamily: 'var(--font-mono)' }}>
                    {v.financials}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={onExpand}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold"
                  style={{
                    background: `${color}18`,
                    border: `1px solid ${color}44`,
                    color,
                    fontFamily: 'var(--font-display)',
                    cursor: 'pointer',
                  }}
                >
                  ↑ Verdict
                </button>
                <button
                  onClick={onReset}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold"
                  style={{
                    background: '#1a1a1a',
                    border: '1px solid #2a2a2a',
                    color: '#666',
                    fontFamily: 'var(--font-display)',
                    cursor: 'pointer',
                  }}
                >
                  ↩ New
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
