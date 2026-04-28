export type AgentName = 'Visionary' | 'Skeptic' | 'Engineer' | 'Analyst'

export interface StatusEvent {
  type: 'status'
  phase: number
  label: string
}

export interface Turn {
  type: 'turn'
  phase: number
  speaker: AgentName
  role: string
  text: string
}

export interface ToolCallEvent {
  type: 'tool_call'
  name: string
  args: Record<string, unknown>
  result: Record<string, unknown> | null
}

export interface VerdictEvent {
  type: 'verdict'
  text: string
}

export interface DoneEvent { type: 'done' }
export interface ErrorEvent { type: 'error'; message: string }

export type SSEEvent =
  | StatusEvent
  | Turn
  | ToolCallEvent
  | VerdictEvent
  | DoneEvent
  | ErrorEvent

export interface ParsedVerdict {
  decision: string
  offer: string
  rationale: string
  marketRisk: string
  techRisk: string
  financials: string
  raw: string
}

export function parseVerdict(text: string): ParsedVerdict {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)
  const get = (prefix: string) => {
    const line = lines.find(l => l.startsWith(prefix))
    return line ? line.slice(prefix.length).trim() : ''
  }
  return {
    decision: get('Decision:'),
    offer: get('Offer:'),
    rationale: get('Rationale:'),
    marketRisk: get('Key Market Risk:'),
    techRisk: get('Key Tech Risk:'),
    financials: get('Financials:'),
    raw: text,
  }
}

export const AGENT_COLORS: Record<AgentName, string> = {
  Visionary: '#34d399',
  Skeptic:   '#f87171',
  Engineer:  '#60a5fa',
  Analyst:   '#a78bfa',
}

export const AGENT_ROLES: Record<AgentName, string> = {
  Visionary: 'The Founder',
  Skeptic:   'Investor — Markets',
  Engineer:  'Investor — Tech',
  Analyst:   'Orchestrator',
}

export const PHASE_LABELS: Record<number, string> = {
  1: 'Pitch',
  2: 'Market',
  3: 'Tech',
  4: 'Numbers',
  5: 'Verdict',
}
