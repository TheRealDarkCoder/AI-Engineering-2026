"""
Multi-Agent Painter & Critic using AG2 framework.
Subject: A sunset over the ocean with a sailboat.
"""

import base64
import os
from io import BytesIO

from dotenv import load_dotenv
from PIL import Image, ImageDraw
from autogen import AssistantAgent, UserProxyAgent, register_function

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
PROXY_URL = os.environ["PROXY_URL"]
MODEL     = os.environ["MODEL"]
CANVAS_SIZE = int(os.getenv("CANVAS_SIZE", 200))
NUM_ROUNDS  = int(os.getenv("NUM_ROUNDS", 10))
OUTPUT_DIR  = os.getenv("OUTPUT_DIR", "output")
SUBJECT     = os.environ["SUBJECT"]

os.makedirs(OUTPUT_DIR, exist_ok=True)

llm_config = {
    "config_list": [
        {
            "model": MODEL,
            "api_key": "not-needed",
            "base_url": PROXY_URL,
        }
    ],
    "temperature": 0.3,
}

# ── Canvas state ───────────────────────────────────────────────────────────────
canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), color=(0, 0, 0))


def _save_canvas(round_num: int) -> str:
    path = os.path.join(OUTPUT_DIR, f"round_{round_num:02d}.png")
    canvas.save(path)
    return path


def _canvas_as_base64() -> str:
    buf = BytesIO()
    canvas.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ── Drawing tools ──────────────────────────────────────────────────────────────

def draw_rectangle(x: int, y: int, width: int, height: int, r: int, g: int, b: int) -> str:
    """Fill a rectangle region on the 200x200 canvas with an RGB color. Use large rectangles for backgrounds and broad areas."""
    draw = ImageDraw.Draw(canvas)
    x2 = min(x + width - 1, CANVAS_SIZE - 1)
    y2 = min(y + height - 1, CANVAS_SIZE - 1)
    draw.rectangle([max(0, x), max(0, y), x2, y2], fill=(r, g, b))
    return f"OK: rectangle ({x},{y}) size {width}x{height} color ({r},{g},{b})"


def draw_ellipse(x: int, y: int, width: int, height: int, r: int, g: int, b: int) -> str:
    """Draw a filled ellipse on the canvas. Bounding box: top-left (x,y), size width x height. Good for sun, waves, clouds."""
    draw = ImageDraw.Draw(canvas)
    x2 = min(x + width - 1, CANVAS_SIZE - 1)
    y2 = min(y + height - 1, CANVAS_SIZE - 1)
    draw.ellipse([max(0, x), max(0, y), x2, y2], fill=(r, g, b))
    return f"OK: ellipse ({x},{y}) size {width}x{height} color ({r},{g},{b})"


def draw_polygon(points: list[list[int]], r: int, g: int, b: int) -> str:
    """Draw a filled polygon. points is a list of [x,y] pairs, e.g. [[10,50],[50,20],[90,50]]. Great for sails and triangular shapes."""
    draw = ImageDraw.Draw(canvas)
    pts = [(max(0, min(p[0], CANVAS_SIZE - 1)), max(0, min(p[1], CANVAS_SIZE - 1))) for p in points]
    draw.polygon(pts, fill=(r, g, b))
    return f"OK: polygon {len(pts)} vertices color ({r},{g},{b})"


def draw_line(x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, width: int = 2) -> str:
    """Draw a straight line from (x1,y1) to (x2,y2). Useful for masts, horizon lines, and details."""
    draw = ImageDraw.Draw(canvas)
    draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=max(1, width))
    return f"OK: line ({x1},{y1})->({x2},{y2}) width={width} color ({r},{g},{b})"


# ── Agents ─────────────────────────────────────────────────────────────────────

painter_system = f"""You are a Painter agent. Your goal is to iteratively paint "{SUBJECT}" on a {CANVAS_SIZE}x{CANVAS_SIZE} pixel canvas.

Canvas coordinates: (0,0) is top-left, ({CANVAS_SIZE-1},{CANVAS_SIZE-1}) is bottom-right.

Available tools:
- draw_rectangle(x, y, width, height, r, g, b)
- draw_ellipse(x, y, width, height, r, g, b)
- draw_polygon(points, r, g, b)  — points is a list of [x, y] pairs
- draw_line(x1, y1, x2, y2, r, g, b, width)

Each turn you will receive the current canvas as an image and a log of every drawing call made so far. Use the log to know the exact position and size of existing elements. If the Critic asks you to change or move an element, first cover the old element by drawing over it with the surrounding background color, then draw the updated version at the new position. When you are done with your turn, reply with: DONE"""

critic_system = f"""You are a Critic agent. Your role is to evaluate a digital painting of "{SUBJECT}" and provide constructive feedback to help the Painter improve it.

Each turn you will receive the current painting as an image. Look at it carefully and provide clear, actionable feedback: note what is working well and describe what could be improved or added in the next round. Keep your feedback concise and focused on the visual result. End your response with: FEEDBACK COMPLETE"""

# Painter + Executor pair
painter = AssistantAgent(
    name="Painter",
    system_message=painter_system,
    llm_config=llm_config,
)

executor = UserProxyAgent(
    name="Executor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=30,
    code_execution_config=False,
    is_termination_msg=lambda msg: isinstance(msg.get("content"), str) and "DONE" in msg["content"],
)

# Critic + its own proxy
critic = AssistantAgent(
    name="Critic",
    system_message=critic_system,
    llm_config=llm_config,
)

critic_proxy = UserProxyAgent(
    name="CriticProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    code_execution_config=False,
)

# Register tools with painter (for LLM) and executor (for execution)
for fn, desc in [
    (draw_rectangle, "Fill a rectangle on the canvas"),
    (draw_ellipse, "Draw a filled ellipse on the canvas"),
    (draw_polygon, "Draw a filled polygon on the canvas"),
    (draw_line, "Draw a line on the canvas"),
]:
    register_function(
        fn,
        caller=painter,
        executor=executor,
        description=desc,
    )


# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    print(f"Multi-Agent Painter & Critic")
    print(f"Subject: {SUBJECT}")
    print(f"Rounds: {NUM_ROUNDS}\n")

    conversation_log = []
    critic_feedback = ""
    drawing_history: list[str] = []

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n{'='*50}")
        print(f"ROUND {round_num}/{NUM_ROUNDS}")
        print('='*50)

        # ── Painter turn ──────────────────────────────────────────────────
        img_b64_painter = _canvas_as_base64()
        history_section = (
            "Drawing calls made so far:\n" + "\n".join(drawing_history)
            if drawing_history
            else "No drawing calls made yet."
        )
        if round_num == 1:
            paint_text = (
                f"Round {round_num}: Here is the current canvas. Begin painting \"{SUBJECT}\".\n\n"
                f"{history_section}\n\n"
                "Make several drawing calls to build the scene, then reply with: DONE"
            )
        else:
            paint_text = (
                f"Round {round_num}: Here is the current canvas.\n\n"
                f"{history_section}\n\n"
                f"Critic feedback from last round:\n{critic_feedback}\n\n"
                "Apply the feedback and make further improvements, then reply with: DONE"
            )
        paint_msg = {
            "content": [
                {"type": "text", "text": paint_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64_painter}"}},
            ]
        }

        print(f"\n[Painter] Starting round {round_num}...")
        paint_result = executor.initiate_chat(
            painter,
            message=paint_msg,
            max_turns=60,
            clear_history=True,
            summary_method="last_msg",
        )
        painter_summary = paint_result.summary or ""

        # Accumulate drawing operations so the Painter can reference them next round
        for msg in paint_result.chat_history:
            if msg.get("role") == "tool":
                content = msg.get("content", "")
                if isinstance(content, str) and content.startswith("OK:"):
                    drawing_history.append(content)

        conversation_log.append(f"\n{'='*60}\nPAINTER ROUND {round_num}\n{'='*60}")
        for msg in paint_result.chat_history:
            role = msg.get("role", "?")
            content = msg.get("content") or ""
            if isinstance(content, str) and "CANVAS_BASE64_PNG:" in content:
                content = "[canvas image data omitted]"
            conversation_log.append(f"[{role}]: {content[:300]}")

        # Save canvas
        saved = _save_canvas(round_num)
        print(f"[Round {round_num}] Saved: {saved}")

        # ── Critic turn ───────────────────────────────────────────────────
        print(f"[Critic] Evaluating round {round_num}...")
        img_b64 = _canvas_as_base64()
        critic_msg = {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Round {round_num} painting is complete. "
                        f"Please evaluate the image and provide specific feedback for the Painter.\n"
                        f"Subject being painted: {SUBJECT}"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                },
            ]
        }

        critic_result = critic_proxy.initiate_chat(
            critic,
            message=critic_msg,
            max_turns=1,
            clear_history=True,
            summary_method="last_msg",
        )
        critic_feedback = critic_result.summary or ""

        conversation_log.append(f"\n{'='*60}\nCRITIC ROUND {round_num}\n{'='*60}")
        for msg in critic_result.chat_history:
            role = msg.get("role", "?")
            content = msg.get("content") or ""
            if isinstance(content, list):
                content = " ".join(
                    part.get("text", "[image]") if isinstance(part, dict) else str(part)
                    for part in content
                )
            conversation_log.append(f"[{role}]: {content[:500]}")

        print(f"[Critic] Feedback: {critic_feedback[:150]}...")

    # Save conversation log
    log_path = os.path.join(OUTPUT_DIR, "conversation_log.txt")
    with open(log_path, "w") as f:
        f.write("\n".join(conversation_log))
    print(f"\nConversation log saved to {log_path}")
    print(f"Images saved in: {OUTPUT_DIR}/")
    print("Done!")


if __name__ == "__main__":
    main()
