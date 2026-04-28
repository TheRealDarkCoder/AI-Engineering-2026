import ast
import json
import os
import re
from agents import create_agents
from tools import run_financial_projection, estimate_market_size


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_tool_content(content):
    """Robustly parse a tool result into a dict.

    AG2 stores tool outputs as str(dict) (single quotes), not JSON, so we try
    json first, then ast.literal_eval, then a regex-extracted substring.
    """
    if content is None:
        return None
    if isinstance(content, dict):
        return content
    if not isinstance(content, str) or not content.strip():
        return None
    for parser in (json.loads, ast.literal_eval):
        try:
            return parser(content)
        except Exception:
            pass
    match = re.search(r"\{[^{}]+\}", content, re.DOTALL)
    if match:
        for parser in (json.loads, ast.literal_eval):
            try:
                return parser(match.group(0))
            except Exception:
                pass
    return None


def _all_assistant_texts(chat_result, agent_name: str) -> list:
    texts = []
    for msg in chat_result.chat_history:
        if not isinstance(msg, dict):
            continue
        if msg.get("tool_calls"):
            continue
        if msg.get("role") == "tool":
            continue
        if msg.get("name") and msg.get("name") != agent_name:
            continue
        content = msg.get("content")
        if content and isinstance(content, str) and content.strip():
            texts.append(content.strip())
    return texts


def _last_assistant_text(chat_result, agent_name: str) -> str:
    texts = _all_assistant_texts(chat_result, agent_name)
    return texts[-1] if texts else ""


def _strip_marker(text: str, marker: str = "END_CRUNCH") -> str:
    return text.replace(marker, "").strip()


def _extract_verdict_block(text: str) -> str:
    match = re.search(r"=== SHARK TANK VERDICT ===.*?={20,}", text, re.DOTALL)
    if match:
        return match.group(0).strip()
    start = text.find("=== SHARK TANK VERDICT ===")
    if start != -1:
        return text[start:].strip()
    return text.strip()


def _collect_tool_results(chat_result) -> dict:
    results = {"financial": None, "market": None, "raw": []}
    for msg in chat_result.chat_history:
        if not isinstance(msg, dict):
            continue
        candidates = []
        if msg.get("role") == "tool":
            candidates.append({"name": msg.get("name", ""), "content": msg.get("content", "")})
        for tr in msg.get("tool_responses") or []:
            candidates.append({"name": tr.get("name", ""), "content": tr.get("content", "")})
        for c in candidates:
            results["raw"].append(c)
            parsed = _parse_tool_content(c["content"])
            if parsed and isinstance(parsed, dict):
                if "monthly_revenue_usd" in parsed:
                    results["financial"] = parsed
                elif "total_addressable_market_usd" in parsed:
                    results["market"] = parsed
    return results


def _collect_tool_events(chat_result) -> list:
    """Pair each tool call request with its result."""
    call_map = {}
    result_map = {}
    for msg in chat_result.chat_history:
        if not isinstance(msg, dict):
            continue
        for tc in msg.get("tool_calls") or []:
            cid = tc.get("id", "")
            fn = tc.get("function", {})
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except Exception:
                args = {}
            call_map[cid] = {"name": fn.get("name", "unknown"), "args": args}
        if msg.get("role") == "tool":
            cid = msg.get("tool_call_id", "")
            result_map[cid] = _parse_tool_content(msg.get("content", ""))
        for tr in msg.get("tool_responses") or []:
            cid = tr.get("tool_call_id", tr.get("id", ""))
            result_map[cid] = _parse_tool_content(tr.get("content", ""))
    return [
        {"name": info["name"], "args": info["args"], "result": result_map.get(cid)}
        for cid, info in call_map.items()
    ]


def _format_tool_results(results: dict) -> str:
    if not results["financial"] and not results["market"]:
        return "(no tool results captured)"
    lines = []
    if results["financial"]:
        f = results["financial"]
        lines.append("Financial projection:")
        for k, v in f.items():
            lines.append(f"  - {k}: {v}")
    if results["market"]:
        m = results["market"]
        # Highlight SAM explicitly — it is the decision-relevant market size metric
        sam = m.get("serviceable_addressable_market_usd", "N/A")
        lines.append(f"Market sizing (SAM = ${sam:,} — USE THIS for scoring, not TAM):" if isinstance(sam, (int, float)) else "Market sizing:")
        for k, v in m.items():
            lines.append(f"  - {k}: {v}")
    return "\n".join(lines)


def _fallback_tool_calls(idea: str) -> dict:
    industry_keywords = [
        "fitness", "food", "transport", "education", "health", "finance",
        "retail", "real estate", "travel", "entertainment", "software",
        "gaming", "social", "pet", "fashion", "agriculture", "energy",
    ]
    idea_lower = idea.lower()
    industry = next((k for k in industry_keywords if k in idea_lower), "software")
    return {
        "financial": run_financial_projection(120.0, 20.0, 5000),
        "market": estimate_market_size(industry, "general consumers"),
        "raw": [],
        "fallback": True,
    }


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_shark_tank(idea: str, on_event=None) -> None:
    """Run the full Shark Tank debate pipeline.

    Args:
        idea: One-sentence startup idea from the user.
        on_event: Optional callback called with structured event dicts as each
                  phase completes. Events are also saved to output/ on disk.
    """
    output_dir = os.getenv("OUTPUT_DIR", "./output")

    def emit(event: dict):
        if on_event:
            on_event(event)

    visionary, skeptic, engineer, analyst, user_proxy = create_agents()
    turns = []

    # ── Phase 1: Pitch ────────────────────────────────────────────────────────
    emit({"type": "status", "phase": 1, "label": "Visionary is crafting the pitch…"})

    r = user_proxy.initiate_chat(
        visionary,
        message=(
            f"You are the founder pitching your startup to investors.\n"
            f"The idea: \"{idea}\"\n\n"
            "Deliver a passionate, detailed 3-paragraph pitch right now. Include concrete numbers "
            "(target monthly price, year-one user estimate, customer acquisition cost, industry category)."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    pitch = _last_assistant_text(r, "Visionary")
    emit({"type": "turn", "phase": 1, "speaker": "Visionary", "role": "The Pitch", "text": pitch})
    turns.append({"speaker": "VISIONARY — The Pitch", "text": pitch})

    # ── Phase 2: Market Inquisition ───────────────────────────────────────────
    emit({"type": "status", "phase": 2, "label": "Skeptic is attacking the market…"})

    r = user_proxy.initiate_chat(
        skeptic,
        message=(
            f"A founder just pitched this startup:\n\n{pitch}\n\n"
            "Tear apart the market viability and business model. Be ruthless."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    skeptic_attack = _last_assistant_text(r, "Skeptic")
    emit({"type": "turn", "phase": 2, "speaker": "Skeptic", "role": "Market Attack", "text": skeptic_attack})
    turns.append({"speaker": "SKEPTIC — Market Attack", "text": skeptic_attack})

    emit({"type": "status", "phase": 2, "label": "Visionary is defending the market…"})
    r = user_proxy.initiate_chat(
        visionary,
        message=(
            f"A Skeptic investor just attacked your pitch:\n\n{skeptic_attack}\n\n"
            "Defend your market position. Be confident but honest. Re-state your monthly price, "
            "user target, and CAC if relevant."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    market_defense = _last_assistant_text(r, "Visionary")
    emit({"type": "turn", "phase": 2, "speaker": "Visionary", "role": "Market Defense", "text": market_defense})
    turns.append({"speaker": "VISIONARY — Market Defense", "text": market_defense})

    # Phase 2.5: Skeptic's verdict on the defense
    emit({"type": "status", "phase": 2, "label": "Skeptic is evaluating the defense…"})
    r = user_proxy.initiate_chat(
        skeptic,
        message=(
            f"You raised this market concern:\n{skeptic_attack}\n\n"
            f"The founder defended with:\n{market_defense}\n\n"
            "Is your concern resolved? Give your investor verdict now."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    skeptic_verdict = _last_assistant_text(r, "Skeptic")
    emit({"type": "turn", "phase": 2, "speaker": "Skeptic", "role": "Market Verdict", "text": skeptic_verdict})
    turns.append({"speaker": "SKEPTIC — Market Verdict", "text": skeptic_verdict})

    # ── Phase 3: Tech Inquisition ─────────────────────────────────────────────
    emit({"type": "status", "phase": 3, "label": "Engineer is attacking the tech…"})

    r = user_proxy.initiate_chat(
        engineer,
        message=(
            f"A founder pitched this startup:\n\n{pitch}\n\n"
            "Destroy the technical feasibility. Find the fatal flaw."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    engineer_attack = _last_assistant_text(r, "Engineer")
    emit({"type": "turn", "phase": 3, "speaker": "Engineer", "role": "Tech Attack", "text": engineer_attack})
    turns.append({"speaker": "ENGINEER — Tech Attack", "text": engineer_attack})

    emit({"type": "status", "phase": 3, "label": "Visionary is defending the tech…"})
    r = user_proxy.initiate_chat(
        visionary,
        message=(
            f"An Engineer investor just attacked your tech:\n\n{engineer_attack}\n\n"
            "Defend your technical approach. Show you've thought this through."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    tech_defense = _last_assistant_text(r, "Visionary")
    emit({"type": "turn", "phase": 3, "speaker": "Visionary", "role": "Tech Defense", "text": tech_defense})
    turns.append({"speaker": "VISIONARY — Tech Defense", "text": tech_defense})

    # Phase 3.5: Engineer's verdict on the tech defense
    emit({"type": "status", "phase": 3, "label": "Engineer is evaluating the defense…"})
    r = user_proxy.initiate_chat(
        engineer,
        message=(
            f"You raised this technical concern:\n{engineer_attack}\n\n"
            f"The founder defended with:\n{tech_defense}\n\n"
            "Is your concern resolved? Give your investor verdict now."
        ),
        max_turns=1,
        clear_history=True,
        silent=True,
    )
    engineer_verdict = _last_assistant_text(r, "Engineer")
    emit({"type": "turn", "phase": 3, "speaker": "Engineer", "role": "Tech Verdict", "text": engineer_verdict})
    turns.append({"speaker": "ENGINEER — Tech Verdict", "text": engineer_verdict})

    # ── Phase 4: Number Crunch ────────────────────────────────────────────────
    emit({"type": "status", "phase": 4, "label": "Analyst is running the numbers…"})

    crunch_prompt = (
        f"NUMBER CRUNCH MODE.\n\n"
        f"Startup idea: \"{idea}\"\n\n"
        f"PITCH:\n{pitch}\n\n"
        f"MARKET DEFENSE:\n{market_defense}\n\n"
        f"TECH DEFENSE:\n{tech_defense}\n\n"
        "Follow your STEP 1 → STEP 5 procedure now. Call BOTH tools before writing any text. "
        "End with the line END_CRUNCH on its own."
    )
    r = user_proxy.initiate_chat(
        analyst,
        message=crunch_prompt,
        max_turns=6,
        clear_history=True,
        silent=True,
    )
    crunch_text = _strip_marker(_last_assistant_text(r, "Analyst"))
    tool_results = _collect_tool_results(r)
    tool_events = _collect_tool_events(r)

    if not tool_results["financial"] or not tool_results["market"]:
        tool_results = _fallback_tool_calls(idea)
        crunch_text = (
            (crunch_text + "\n\n" if crunch_text else "")
            + "[Auto-fallback — analyst did not call tools, used industry defaults]\n"
            + _format_tool_results(tool_results)
        )

    # Emit each tool call event (with args + result) for the live UI
    for te in tool_events:
        emit({"type": "tool_call", "name": te["name"], "args": te["args"], "result": te["result"]})

    # If fallback, emit the synthetic tool results
    if not tool_events:
        if tool_results.get("financial"):
            emit({"type": "tool_call", "name": "run_financial_projection",
                  "args": {"note": "fallback defaults"}, "result": tool_results["financial"]})
        if tool_results.get("market"):
            emit({"type": "tool_call", "name": "estimate_market_size",
                  "args": {"note": "fallback defaults"}, "result": tool_results["market"]})

    emit({"type": "turn", "phase": 4, "speaker": "Analyst", "role": "Number Crunch", "text": crunch_text})
    turns.append({"speaker": "ANALYST — Number Crunch", "text": crunch_text})

    # ── Phase 5: Verdict ──────────────────────────────────────────────────────
    emit({"type": "status", "phase": 5, "label": "Analyst is delivering the verdict…"})

    verdict_prompt = (
        "VERDICT MODE.\n\n"
        f"TOOL RESULTS (primary weight):\n{_format_tool_results(tool_results)}\n\n"
        "INVESTOR VERDICTS — these carry decisive weight; apply Step C overrides before scoring:\n"
        f"  Skeptic's verdict on the market defense: {skeptic_verdict}\n"
        f"  Engineer's verdict on the tech defense:  {engineer_verdict}\n\n"
        "DEBATE TRANSCRIPT (use to compute Steps A–B scores):\n\n"
        f"--- PITCH ---\n{pitch}\n\n"
        f"--- SKEPTIC ATTACK ---\n{skeptic_attack}\n\n"
        f"--- VISIONARY MARKET DEFENSE ---\n{market_defense}\n\n"
        f"--- ENGINEER ATTACK ---\n{engineer_attack}\n\n"
        f"--- VISIONARY TECH DEFENSE ---\n{tech_defense}\n\n"
        "Apply Steps A → D in your head, then output ONLY the verdict block. "
        "Stop immediately after the closing =========================="
    )
    r = user_proxy.initiate_chat(
        analyst,
        message=verdict_prompt,
        max_turns=2,
        clear_history=True,
        silent=True,
    )
    verdict_raw = _last_assistant_text(r, "Analyst")
    verdict = _extract_verdict_block(verdict_raw)
    turns.append({"speaker": "ANALYST — Verdict", "text": verdict})

    emit({"type": "verdict", "text": verdict})

    # ── Persist to disk ───────────────────────────────────────────────────────
    os.makedirs(output_dir, exist_ok=True)

    transcript_path = os.path.join(output_dir, "transcript.md")
    with open(transcript_path, "w") as f:
        f.write("# Shark Tank Transcript\n\n")
        for turn in turns:
            f.write(f"## {turn['speaker']}\n\n{turn['text'].strip()}\n\n---\n\n")

    verdict_path = os.path.join(output_dir, "verdict.txt")
    with open(verdict_path, "w") as f:
        f.write(verdict.strip())
