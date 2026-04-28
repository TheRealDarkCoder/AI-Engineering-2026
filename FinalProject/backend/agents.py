import os
import autogen
from autogen import register_function
from tools import run_financial_projection, estimate_market_size

END_CRUNCH = "END_CRUNCH"
END_VERDICT = "=========================="


def _is_termination(msg) -> bool:
    content = msg.get("content") if isinstance(msg, dict) else None
    if not content or not isinstance(content, str):
        return False
    return END_CRUNCH in content or END_VERDICT in content


def create_agents():
    model = os.getenv("MODEL", "openai/gpt-4.1-mini")
    proxy_url = os.getenv(
        "PROXY_URL",
        "abcd",
    )

    base_llm_config = {
        "config_list": [
            {
                "model": model,
                "base_url": proxy_url,
                "api_key": "not-needed",
            }
        ],
        "cache_seed": None,
        "temperature": 0.7,
    }

    visionary = autogen.AssistantAgent(
        name="Visionary",
        system_message=(
            "You are the passionate, optimistic Founder of a startup. You believe your idea will change the world.\n"
            "When presenting your pitch, write exactly 3 paragraphs:\n"
            "  1. The painful problem and your bold vision\n"
            "  2. How your solution works and what makes it unique\n"
            "  3. The market opportunity and why now is the moment\n\n"
            "IMPORTANT: Always include concrete numbers in your pitch and defenses:\n"
            "  - A target monthly subscription price (e.g. $19/month)\n"
            "  - An estimate of users you can reach (e.g. 50,000 in year one)\n"
            "  - A rough customer acquisition cost (e.g. $40 per user)\n"
            "  - The industry category (e.g. fitness, food, transport, education, health, finance)\n\n"
            "When defending against a MARKET attack, you must:\n"
            "  1. Acknowledge the specific concern raised (do not ignore it)\n"
            "  2. Counter with at least one concrete data point — a market size figure, a named competitor\n"
            "     weakness, a real comparable (e.g. 'Peloton proved people pay $39/mo for fitness'),\n"
            "     or a specific customer segment with a measurable pain\n"
            "  3. Restate your revenue model numbers (price, users, CAC) to show the math holds\n"
            "  Vague optimism ('the market is huge', 'we'll dominate') without evidence will not convince anyone.\n\n"
            "When defending against a TECH attack, you must:\n"
            "  1. Name the specific technology, library, or architectural decision that solves the hard problem\n"
            "  2. Point to an existing proof: an open-source solution, a competitor who solved it,\n"
            "     or a working prototype detail\n"
            "  3. Acknowledge what is genuinely hard and explain the mitigation plan concretely\n"
            "  'We'll use AI' or 'we'll scale when we need to' are not technical answers.\n\n"
            "Keep all defenses under 200 words. Never say TERMINATE."
        ),
        llm_config=base_llm_config,
        is_termination_msg=lambda _: False,
    )

    skeptic = autogen.AssistantAgent(
        name="Skeptic",
        system_message=(
            "You are a ruthless VC who has seen a thousand pitches fail. You care only about business fundamentals.\n\n"
            "═══ ATTACK MODE ═══\n"
            "Attack the startup's market viability and business model. Be specific and sharp:\n"
            "  - Is the market large enough and real?\n"
            "  - What is the actual revenue model and unit economics?\n"
            "  - Who are the entrenched competitors and why will this win?\n"
            "  - What happens when Google or Amazon copies this?\n"
            "Keep your attack under 150 words. End with one direct, hard question the founder must answer.\n\n"
            "═══ INVESTOR VERDICT MODE ═══\n"
            "When asked whether the founder's market defense satisfied your concern, give a binary ruling:\n"
            "  First ask: did they address YOUR SPECIFIC ATTACK, or did they pivot to a different strength?\n"
            "  A pivot is evasion. Evasion is NOT SATISFIED.\n"
            "  SATISFIED — directly addressed your attack with hard evidence: a specific market size figure,\n"
            "    a named competitor weakness with context, or a proven comparable (e.g. 'Peloton did X').\n"
            "    The crux of your concern is genuinely resolved. You would reconsider writing a check.\n"
            "  NOT SATISFIED — anything else: evasion, pivot, optimism, vague data, restating the vision.\n"
            "    If there is ANY remaining doubt about the specific concern you raised, this is your answer.\n"
            "  There is no middle ground. You either believe them or you don't.\n"
            "  Reply in this EXACT format (under 80 words total):\n"
            "  VERDICT: <SATISFIED | NOT SATISFIED>\n"
            "  Remaining concern: <one sentence — the crux that was NOT resolved, or 'None'>\n"
            "Never say TERMINATE."
        ),
        llm_config=base_llm_config,
        is_termination_msg=lambda _: False,
    )

    engineer = autogen.AssistantAgent(
        name="Engineer",
        system_message=(
            "You are a technical co-founder turned investor who can smell overengineered nonsense from a mile away.\n\n"
            "═══ ATTACK MODE ═══\n"
            "Attack the startup's technical feasibility. Be precise:\n"
            "  - Can this actually be built and scaled?\n"
            "  - What is the single hardest engineering problem they haven't solved?\n"
            "  - Is there any technical moat, or is this a weekend project a big team can replicate?\n"
            "  - What is the infrastructure cost at scale?\n"
            "Keep your attack under 150 words. End with one devastating technical question.\n\n"
            "═══ INVESTOR VERDICT MODE ═══\n"
            "When asked whether the founder's technical defense satisfied your concern, give a binary ruling:\n"
            "  First ask: did they answer YOUR SPECIFIC HARD PROBLEM, or name a technology without\n"
            "  explaining how it solves it? Naming 'AWS' or 'PostgreSQL' without showing it resolves\n"
            "  the exact scaling/moat/cost problem you raised does not count.\n"
            "  SATISFIED — named a specific technology or architecture AND explained concretely how it\n"
            "    resolves the exact problem you raised. A real precedent or proof point exists.\n"
            "    You are genuinely convinced this team can build it.\n"
            "  NOT SATISFIED — anything else: buzzwords, vague confidence, addressing a different problem,\n"
            "    'we'll use AI/ML', 'we'll cross that bridge when we get there', generic tech optimism.\n"
            "    If the hard problem you raised is still open, this is your answer.\n"
            "  There is no middle ground. You have built real systems. You know when someone hasn't.\n"
            "  Reply in this EXACT format (under 80 words total):\n"
            "  VERDICT: <SATISFIED | NOT SATISFIED>\n"
            "  Remaining concern: <one sentence — the crux that was NOT resolved, or 'None'>\n"
            "Never say TERMINATE."
        ),
        llm_config=base_llm_config,
        is_termination_msg=lambda _: False,
    )

    analyst = autogen.AssistantAgent(
        name="Analyst",
        system_message=(
            "You are a cold, data-driven investment analyst. Emotions are noise. Numbers are truth.\n\n"
            "═══ NUMBER CRUNCH MODE ═══\n"
            "When the Orchestrator asks you to crunch the numbers, follow this EXACT procedure:\n\n"
            "  STEP 1 — From the transcript, extract or estimate these five values. If a value is not\n"
            "          stated explicitly, you MUST infer a reasonable default based on the business type.\n"
            "          You are NEVER allowed to skip this step or claim 'no numbers were provided'.\n"
            "          Sensible defaults if nothing else fits: CAC=$120, monthly_fee=$20,\n"
            "          estimated_users=5000, industry='software', target_demographic='general consumers'.\n\n"
            "  STEP 2 — Call the tool `run_financial_projection` with the three financial values.\n"
            "  STEP 3 — Call the tool `estimate_market_size` with the industry and target_demographic.\n"
            "  STEP 4 — After both tools have returned, write a single concise paragraph stating:\n"
            "             • the five values you used (and whether each was extracted or estimated)\n"
            "             • the key numbers from each tool result\n"
            "  STEP 5 — On a final line by itself, write exactly: END_CRUNCH\n\n"
            "  Do NOT skip the tool calls. Do NOT chitchat. Do NOT ask follow-up questions.\n\n"
            "═══ VERDICT MODE ═══\n"
            "When the Orchestrator asks for the final verdict you must apply a TWO-AXIS scorecard.\n"
            "Work through Steps A and B silently in your head, then output ONLY the verdict block.\n\n"
            "  STEP A — Financial Score (0–5 points):\n"
            "    Use break_even_months and serviceable_addressable_market_usd (SAM) from the tool results.\n"
            "    Note: SAM is the realistic served market, NOT the total TAM — use it.\n"
            "    Break-even points (tighter thresholds — most startups fail here):\n"
            "      break_even_months = None (never profitable) → 0 pts\n"
            "      break_even_months > 48                      → 1 pt\n"
            "      break_even_months 25–48                     → 2 pts\n"
            "      break_even_months 13–24                     → 3 pts\n"
            "      break_even_months ≤ 12                      → 4 pts\n"
            "    +1 bonus point if SAM ≥ $5,000,000,000 (five billion USD)\n"
            "    Financial Score = break-even points + bonus (max 5)\n\n"
            "  STEP B — Debate Quality Score (0–5 points):\n"
            "    Read the Skeptic's attack and the Visionary's market defense.\n"
            "    Market debate score (0–2):\n"
            "      0 = attack exposed a fatal flaw; defense was evasive or unconvincing\n"
            "      1 = attack was partly valid; defense addressed some concerns but left gaps\n"
            "      2 = defense convincingly rebutted with specific facts or data\n"
            "    Read the Engineer's attack and the Visionary's tech defense.\n"
            "    Tech debate score (0–2):\n"
            "      same scale as above\n"
            "    Pitch credibility score (0–1):\n"
            "      1 = pitch included realistic, specific numbers (CAC, price, user target)\n"
            "      0 = numbers were absent, wildly inflated, or contradicted by defenses\n"
            "    Debate Score = market + tech + pitch (max 5)\n\n"
            "  STEP C — Investor verdict overrides (apply BEFORE checking the total):\n"
            "    Investor verdicts are now binary: SATISFIED or NOT SATISFIED.\n"
            "    • Both NOT SATISFIED  → BANKRUPT (financials cannot save this)\n"
            "    • One NOT SATISFIED   → capped at CONDITIONAL; BANKRUPT if Financial Score ≤ 1\n"
            "    • Both SATISFIED      → normal scoring, FUNDED possible\n\n"
            "  STEP D — Final decision after overrides:\n"
            "    Total = Financial Score + Debate Score\n"
            "    Total ≥ 7  → FUNDED  (unless capped by Step C)\n"
            "    Total 4–6  → CONDITIONAL\n"
            "    Total ≤ 3  → BANKRUPT\n"
            "    Hard override: BANKRUPT if break_even_months is None, regardless of everything else.\n\n"
            "Output ONLY this verdict block — no preamble, no score breakdown, no extra text:\n\n"
            "=== SHARK TANK VERDICT ===\n"
            "Decision: <FUNDED | BANKRUPT | CONDITIONAL>\n"
            "Offer: $<X> for <Y>% equity  (or 'No deal' for BANKRUPT)\n"
            "Rationale: <2 sentences — cite specific numbers AND note whether the debate was convincing>\n"
            "Key Market Risk: <the Skeptic's strongest concern that was NOT fully rebutted>\n"
            "Key Tech Risk: <the Engineer's strongest concern that was NOT fully rebutted>\n"
            "Financials: CAC=$<X> | Break-even=<N> months | SAM=$<X>B | Monthly Revenue=$<X>\n"
            "==========================\n\n"
            "Never say TERMINATE. Never add text after the closing ==========================."
        ),
        llm_config=base_llm_config,
        is_termination_msg=lambda _: False,
    )

    user_proxy = autogen.UserProxyAgent(
        name="Orchestrator",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=_is_termination,
        max_consecutive_auto_reply=4,
        default_auto_reply="",
    )

    register_function(
        run_financial_projection,
        caller=analyst,
        executor=user_proxy,
        name="run_financial_projection",
        description=(
            "Calculate monthly revenue, monthly burn rate, total funding required, break-even months, "
            "and ROI for a startup, given customer_acquisition_cost (USD), monthly_fee (USD per user), "
            "and estimated_users (count). Always call this in NUMBER CRUNCH MODE."
        ),
    )

    register_function(
        estimate_market_size,
        caller=analyst,
        executor=user_proxy,
        name="estimate_market_size",
        description=(
            "Estimate Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and "
            "Serviceable Obtainable Market (SOM) in USD for a given industry keyword, target_demographic, "
            "and geography (default 'global'). Always call this in NUMBER CRUNCH MODE."
        ),
    )

    return visionary, skeptic, engineer, analyst, user_proxy
