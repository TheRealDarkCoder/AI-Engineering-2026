# Assignment 3: Multi-Agent Painter & Critic

## How to Run

**Requirements:** Python 3.11+, internet access to the provided API proxy.

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install ag2[openai] Pillow python-dotenv

# Configure environment
cp .env.example .env
# Edit .env to set PROXY_URL, MODEL, SUBJECT, etc.

# Run
python painter_critic.py
```

Output images are saved to `output/round_01.png` … `output/round_10.png`.
The full conversation log is saved to `output/conversation_log.txt`.

---

## Drawing Subject

**"A sunset over the ocean with a sailboat silhouette"**

A scene composed from scratch on a blank canvas: sky gradient from deep blue at the top to warm orange at the horizon, a sun near the horizon, a dark ocean below, and a sailboat silhouette with hull, mast, and sail.

---

## Design Decisions

### Agent Architecture

Two `AssistantAgent` instances — **Painter** and **Critic** — each paired with a `UserProxyAgent` for conversation management:

- **Painter + Executor**: `Executor.initiate_chat(painter, ...)` starts each painting turn. The Painter emits tool calls; the Executor executes them automatically via AG2's built-in tool dispatch. The conversation terminates cleanly when the Painter replies with `DONE`.
- **Critic + CriticProxy**: After each painting turn, `CriticProxy.initiate_chat(critic, ...)` sends the rendered canvas as a base64-encoded `image_url` message. The Critic evaluates it visually and returns feedback in a single turn (`max_turns=1`).

This is the standard AG2 two-agent pattern. The outer `for round_num in range(...)` iterates rounds only; all turn management inside each round is handled by `initiate_chat`.

### Design Pattern

**Sequential two-agent chat per round** (not a GroupChat). Chosen because:
- The Painter and Critic have strictly alternating, non-overlapping roles with no need for dynamic speaker selection.
- Simpler to reason about and debug than a GroupChat with a custom speaker function.
- `clear_history=True` on every `initiate_chat` avoids accumulating stale or dangling tool call messages across rounds (see Improvements section).

### Painter Tools

Four drawing tools registered with AG2's `register_function`:

| Tool | Purpose |
|------|---------|
| `draw_rectangle(x, y, width, height, r, g, b)` | Backgrounds, sky bands, ocean regions, boat hull |
| `draw_ellipse(x, y, width, height, r, g, b)` | Sun, reflections, clouds |
| `draw_polygon(points, r, g, b)` | Triangular sails, irregular shapes |
| `draw_line(x1, y1, x2, y2, r, g, b, width)` | Mast, horizon line, fine details |

### Multimodal Messaging

Both agents receive the canvas as an OpenAI-format `image_url` message containing a `data:image/png;base64,...` URI. This uses the model's vision capability so both the Painter and Critic base their decisions on the actual visual output rather than text descriptions.

---

## Improvements Beyond Requirements

### 1. Painter also receives the canvas image (not just the Critic)

**Requirement:** Only the Critic was required to receive the image.  
**What we do:** The Painter also receives the current canvas as a multimodal `image_url` at the start of every turn.  
**Justification:** Without seeing the canvas, the Painter has no spatial awareness of what has already been drawn and where, causing it to draw blindly and produce incoherent compositions. Giving it the image each round aligns with the prompt's own hint: *"Don't make the Painter guess where to put pixels."*

### 2. Drawing history log passed to the Painter

**What we do:** Every tool call result (e.g. `OK: rectangle (75,120) size 50x15 color (20,10,5)`) is accumulated in a `drawing_history` list and injected into the Painter's message each round.  
**Justification:** The model has no persistent memory across `initiate_chat` calls (history is cleared each round to avoid API errors). Without the log, when the Critic asks the Painter to move or modify an element, the Painter redraws it at slightly shifted coordinates without removing the original, leaving ghost duplicates on the canvas. The log gives the Painter the exact coordinates of every existing element so it can cover the old version with the background color before redrawing.

### 3. Clean termination with `is_termination_msg`

**What we do:** The Executor is configured with `is_termination_msg=lambda msg: "DONE" in msg.get("content", "")`.  
**Justification:** Without this, after the Painter sends `DONE`, the Executor auto-replies with an empty message (its default behaviour with `human_input_mode="NEVER"`). The Painter then receives the empty message, assumes the conversation is still active, and replies `DONE` again. This ping-pong repeats until `max_turns` is exhausted, wasting API calls and time every round.

### 4. `clear_history=True` on every Painter turn

**What we do:** `clear_history=True` is set on every `executor.initiate_chat(...)` call, not only round 1.  
**Justification:** If a round ends while the Painter still has an unexecuted tool call in its last message (e.g. `max_turns` is hit mid-call), that dangling tool call is left in the AG2 conversation history. In the next round with `clear_history=False`, the API receives a message sequence containing a tool call with no corresponding result and returns a `400 Bad Request`. Clearing history each round prevents this entirely; context is preserved through the explicit drawing log and canvas image instead.

---

## Observations on Painter Output

**What went well:**
- The Painter reliably builds a recognizable scene structure from a blank canvas, establishing sky, ocean, and horizon in the first round.
- The sailboat silhouette (hull rectangle + triangular polygon for the sail + mast line) appears consistently across models and improves in detail across rounds.
- The Critic's feedback is concise and actionable; the Painter does apply it in subsequent rounds (e.g. enlarging the sun, darkening the hull, adding wave highlights).
- The drawing history log successfully prevents ghost duplicates — when the Critic requests repositioning an element, the Painter covers the old area before redrawing.

**What went wrong / limitations:**
- The color palette is coarse — the model tends to pick round numbers (255, 128, 64) rather than subtle intermediate values, so the image looks blocky.
- The Painter occasionally redraws large background regions when refining details, which can overwrite previously added elements.
- Later rounds (6–10) show diminishing returns — the model reaches a local "good enough" state and makes incremental rather than bold changes.
- A 200×200 canvas leaves little room for fine detail; the result is more of a pixel-art impression than a realistic painting.
