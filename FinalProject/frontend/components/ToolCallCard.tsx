'use client'

import { useEffect } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import type { ToolCallEvent } from '@/lib/types'

function formatNum(v: number): string {
  if (v >= 1_000_000_000) return `$${(v / 1_000_000_000).toFixed(1)}B`
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${v.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
  return `$${v.toFixed(2)}`
}

function AnimatedStat({ label, value, suffix = '' }: { label: string; value: number | null; suffix?: string }) {
  const mv = useMotionValue(0)
  const display = useTransform(mv, v => {
    if (value === null) return 'N/A'
    return formatNum(v) + suffix
  })

  useEffect(() => {
    if (value === null) return
    const ctrl = animate(mv, value, { duration: 1.6, ease: 'easeOut' })
    return () => ctrl.stop()
  }, [value, mv])

  return (
    <div className="flex justify-between items-baseline py-1.5 border-b" style={{ borderColor: '#1e1e1e' }}>
      <span className="text-xs" style={{ color: '#555', fontFamily: 'var(--font-mono)' }}>{label}</span>
      <motion.span className="text-sm font-medium" style={{ color: '#f0f0f0', fontFamily: 'var(--font-mono)' }}>
        {display}
      </motion.span>
    </div>
  )
}

function Panel({
  title,
  color,
  stats,
}: {
  title: string
  color: string
  stats: { label: string; value: number | null; suffix?: string }[]
}) {
  return (
    <div
      className="flex-1 rounded-xl p-4 min-w-0"
      style={{ background: '#111', border: `1px solid ${color}33` }}
    >
      <p
        className="text-xs mb-3 font-medium"
        style={{ color, fontFamily: 'var(--font-mono)' }}
      >
        {title}
      </p>
      <div>
        {stats.map(s => (
          <AnimatedStat key={s.label} {...s} />
        ))}
      </div>
    </div>
  )
}

interface Props { toolCalls: ToolCallEvent[] }

export default function ToolCallCard({ toolCalls }: Props) {
  const fin = toolCalls.find(t => t.name === 'run_financial_projection')?.result as Record<string, number> | undefined
  const mkt = toolCalls.find(t => t.name === 'estimate_market_size')?.result as Record<string, number> | undefined

  if (!fin && !mkt) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -12, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 22 }}
      className="mx-4 my-2"
    >
      <div
        className="rounded-xl p-1 mb-2"
        style={{ background: 'linear-gradient(135deg, #a78bfa22, #c9a84c22)', border: '1px solid #2a2a2a' }}
      >
        <p
          className="text-xs text-center py-1"
          style={{ color: '#555', fontFamily: 'var(--font-mono)' }}
        >
          ⬡ Analyst called {toolCalls.length} tool{toolCalls.length !== 1 ? 's' : ''}
        </p>
      </div>
      <div className="flex flex-col sm:flex-row gap-3">
        {fin && (
          <Panel
            title="run_financial_projection(...)"
            color="#a78bfa"
            stats={[
              { label: 'Monthly Revenue', value: fin.monthly_revenue_usd ?? null },
              { label: 'Monthly Burn', value: fin.monthly_burn_rate_usd ?? null },
              { label: 'Funding Required', value: fin.funding_required_usd ?? null },
              { label: 'Break-even', value: fin.break_even_months ?? null, suffix: ' mo' },
              { label: 'ROI at Break-even', value: fin.roi_at_break_even ?? null, suffix: '×' },
            ]}
          />
        )}
        {mkt && (
          <Panel
            title="estimate_market_size(...)"
            color="#c9a84c"
            stats={[
              { label: 'TAM', value: mkt.total_addressable_market_usd ?? null },
              { label: 'SAM', value: mkt.serviceable_addressable_market_usd ?? null },
              { label: 'SOM', value: mkt.serviceable_obtainable_market_usd ?? null },
            ]}
          />
        )}
      </div>
    </motion.div>
  )
}
