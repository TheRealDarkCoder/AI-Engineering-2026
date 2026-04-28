# Shark Tank — Frontend

**Final Project · AI Engineering · University of Oulu 2026**
Source: [github.com/TheRealDarkCoder/AI-Engineering-2026](https://github.com/TheRealDarkCoder/AI-Engineering-2026)

Next.js 16 SPA that streams the multi-agent debate live from the Flask backend and renders it with Framer Motion animations.

## Setup

```bash
npm install
```

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

```bash
npm run dev   # http://localhost:3000
```

The backend must be running first. See the root `README.md` for full setup instructions.

## Key components

| Component | Purpose |
|---|---|
| `useSharkTank` | POST SSE streaming hook — state machine (`idle → running → done`) |
| `IdeaInput` | Landing screen with preset ideas |
| `DebateStage` | Main debate view: phase rail, agent roster, dialogue feed |
| `MessageBubble` | Word-by-word animated message reveal; "Verdict" role pills are accent-coloured |
| `ToolCallCard` | Animated number counters for financial and market tool results |
| `VerdictScreen` | Full-screen overlay (collapse to sticky bar to review the transcript) |
