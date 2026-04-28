'use client'

import { useReducer, useRef, useCallback } from 'react'
import type { SSEEvent, Turn, ToolCallEvent } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:5000'

export type AppPhase = 'idle' | 'running' | 'done'

export interface SharkTankState {
  appPhase: AppPhase
  idea: string
  currentStatus: string
  activePhase: number
  turns: Turn[]
  toolCalls: ToolCallEvent[]
  verdict: string | null
  error: string | null
}

type Action =
  | { type: 'START'; idea: string }
  | { type: 'EVENT'; event: SSEEvent }
  | { type: 'RESET' }

const initial: SharkTankState = {
  appPhase: 'idle',
  idea: '',
  currentStatus: '',
  activePhase: 0,
  turns: [],
  toolCalls: [],
  verdict: null,
  error: null,
}

function reducer(state: SharkTankState, action: Action): SharkTankState {
  switch (action.type) {
    case 'START':
      return { ...initial, appPhase: 'running', idea: action.idea }
    case 'EVENT': {
      const ev = action.event
      switch (ev.type) {
        case 'status':
          return { ...state, currentStatus: ev.label, activePhase: ev.phase }
        case 'turn':
          return { ...state, turns: [...state.turns, ev] }
        case 'tool_call':
          return { ...state, toolCalls: [...state.toolCalls, ev] }
        case 'verdict':
          return { ...state, verdict: ev.text }
        case 'done':
          return { ...state, appPhase: 'done' }
        case 'error':
          return { ...state, error: ev.message, appPhase: 'done' }
        default:
          return state
      }
    }
    case 'RESET':
      return initial
    default:
      return state
  }
}

export function useSharkTank() {
  const [state, dispatch] = useReducer(reducer, initial)
  const abortRef = useRef<AbortController | null>(null)

  const submit = useCallback(async (idea: string) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    dispatch({ type: 'START', idea })

    try {
      const response = await fetch(`${API_URL}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea }),
        signal: controller.signal,
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({ error: response.statusText }))
        dispatch({ type: 'EVENT', event: { type: 'error', message: err.error ?? 'Request failed' } })
        return
      }

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() ?? ''
        for (const frame of frames) {
          const dataLine = frame.split('\n').find(l => l.startsWith('data: '))
          if (!dataLine) continue
          try {
            const event = JSON.parse(dataLine.slice(6)) as SSEEvent
            dispatch({ type: 'EVENT', event })
          } catch {
            // skip malformed frames
          }
        }
      }
    } catch (err: unknown) {
      if ((err as { name?: string }).name !== 'AbortError') {
        dispatch({ type: 'EVENT', event: { type: 'error', message: (err as Error).message ?? 'Unknown error' } })
      }
    }
  }, [])

  const reset = useCallback(() => {
    abortRef.current?.abort()
    dispatch({ type: 'RESET' })
  }, [])

  return { state, submit, reset }
}
