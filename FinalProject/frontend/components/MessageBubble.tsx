'use client'

import { motion } from 'framer-motion'
import type { Turn, AgentName } from '@/lib/types'
import { AGENT_COLORS } from '@/lib/types'

const RIGHT_ALIGNED: AgentName[] = ['Skeptic', 'Engineer']

function WordReveal({ text }: { text: string }) {
  const words = text.split(' ')
  const MAX_ANIMATED = 60

  return (
    <p
      className="text-sm leading-relaxed"
      style={{ color: '#ccc', fontFamily: 'var(--font-mono)' }}
    >
      {words.slice(0, MAX_ANIMATED).map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.012, duration: 0.15 }}
        >
          {word}{' '}
        </motion.span>
      ))}
      {words.length > MAX_ANIMATED && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: MAX_ANIMATED * 0.012 + 0.1 }}
        >
          {words.slice(MAX_ANIMATED).join(' ')}
        </motion.span>
      )}
    </p>
  )
}

interface Props { turn: Turn; index: number }

export default function MessageBubble({ turn, index }: Props) {
  const color = AGENT_COLORS[turn.speaker]
  const isRight = RIGHT_ALIGNED.includes(turn.speaker as never)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 280, damping: 26, delay: 0.05 }}
      className={`flex flex-col max-w-[85%] ${isRight ? 'self-end items-end' : 'self-start items-start'}`}
    >
      {/* Header */}
      <div className={`flex items-center gap-2 mb-1.5 ${isRight ? 'flex-row-reverse' : ''}`}>
        <span
          className="text-xs font-semibold"
          style={{ color, fontFamily: 'var(--font-display)' }}
        >
          {turn.speaker}
        </span>
        <span
          className="text-xs px-2 py-0.5 rounded-full"
          style={
            turn.role.endsWith('Verdict')
              ? { background: `${color}18`, color, border: `1px solid ${color}44`, fontFamily: 'var(--font-display)' }
              : { background: '#1a1a1a', color: '#555', border: '1px solid #222' }
          }
        >
          {turn.role}
        </span>
      </div>

      {/* Bubble */}
      <div
        className="px-4 py-3 rounded-2xl"
        style={{
          background: '#111',
          border: `1px solid ${color}22`,
          borderLeft: isRight ? undefined : `2px solid ${color}`,
          borderRight: isRight ? `2px solid ${color}` : undefined,
          maxWidth: '100%',
        }}
      >
        <WordReveal text={turn.text} />
      </div>
    </motion.div>
  )
}
