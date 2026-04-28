# Shark Tank — AI Startup Interrogator

**Final Project · AI Engineering · University of Oulu 2026**

Hosted: [https://sharktank.zuhayrium.com](https://sharktank.zuhayrium.com)


Source: [github.com/TheRealDarkCoder/AI-Engineering-2026](https://github.com/TheRealDarkCoder/AI-Engineering-2026)

---

A multi-agent system that simulates a Shark Tank–style pitch session. Supply a one-sentence startup idea; four AI agents debate it live, challenge the founder, and deliver a **FUNDED / BANKRUPT / CONDITIONAL** verdict backed by financial projections.

## Agents

| Agent | Role |
|---|---|
| Visionary | Pitches the idea; defends against every attack |
| Skeptic | Attacks market viability, unit economics, and competition |
| Engineer | Attacks technical feasibility, scalability, and moat |
| Analyst | Orchestrates the session, runs financial tools, scores the debate, delivers the verdict |

## Conversation flow

1. **Pitch** — Visionary delivers a 3-paragraph pitch with concrete numbers (CAC, price, user target, industry)
2. **Market Inquisition** — Skeptic attacks → Visionary defends → Skeptic issues a `SATISFIED  / NOT SATISFIED` ruling on the defense
3. **Tech Inquisition** — Engineer attacks → Visionary defends → Engineer issues the same ruling
4. **Number Crunch** — Analyst extracts financial inputs from the debate, calls both tools, summarises the results
5. **Verdict** — Analyst applies a two-axis scorecard and delivers the final decision

## Verdict scoring

The Analyst scores two axes and applies investor-verdict overrides:

**Financial score (0–5):** based on `break_even_months` and SAM (Serviceable Addressable Market). Operating overhead (salaries, infra — 30 % of revenue, min $8 K/mo) is included in the burn model, so break-even is genuinely hard to achieve.

**Debate quality score (0–5):** based on pitch credibility and how effectively each attack was rebutted.

**Investor-verdict overrides (applied first):**
- Both investors `NOT SATISFIED` → capped at CONDITIONAL; BANKRUPT if financials are weak

Final decision: total ≥ 7 → **FUNDED** · 4–6 → **CONDITIONAL** · ≤ 3 or break-even impossible → **BANKRUPT**

## Tools

```python
run_financial_projection(customer_acquisition_cost, monthly_fee, estimated_users)
# → monthly_revenue, monthly_burn_rate (incl. overhead), funding_required, break_even_months, roi

estimate_market_size(industry, target_demographic, geography)
# → TAM, SAM, SOM  (SAM is used for scoring, not TAM)
```

## Stack

- **Backend** — Python, AG2 (`ag2[openai]`), Flask SSE streaming
- **Frontend** — Next.js 16, Tailwind v4, Framer Motion 12
- **LLM** — Any OpenRouter-compatible model (default: `openai/gpt-4.1-mini`)

---

## Installation

### Backend

```bash
cd FinalProject/backend
pip install -r requirements.txt
cp .env.example .env
```

`.env` values:
```
PROXY_URL=...
MODEL=openai/gpt-4.1-mini
PORT=5000
```

### Frontend

```bash
cd FinalProject/frontend
npm install
```

`frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## Running

```bash
# Terminal 1
cd FinalProject/backend && python app.py

# Terminal 2
cd FinalProject/frontend && npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Enter an idea or pick a preset, then watch the debate unfold live. When the verdict arrives, click **↓ Review Transcript** to scroll through the full debate and tool call results.
