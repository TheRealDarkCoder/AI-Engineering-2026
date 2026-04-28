import json
import os
import queue
import threading

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── SSE helpers ───────────────────────────────────────────────────────────────

def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


def _sse_comment(msg: str = "keepalive") -> str:
    return f": {msg}\n\n"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/run")
def run():
    body = request.get_json(silent=True) or {}
    idea = (body.get("idea") or "").strip()

    if not idea:
        return jsonify({"error": "Missing or empty 'idea' field."}), 400
    if len(idea) > 500:
        return jsonify({"error": "Idea must be under 500 characters."}), 400

    def generate():
        q: queue.Queue = queue.Queue()

        def on_event(event: dict):
            q.put(event)

        def worker():
            try:
                # Import here so the module path resolves correctly when Flask
                # is started from inside the backend/ directory.
                from orchestrator import run_shark_tank
                run_shark_tank(idea, on_event=on_event)
            except Exception as exc:
                q.put({"type": "error", "message": str(exc)})
            finally:
                q.put(None)  # sentinel — stream is done

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        while True:
            try:
                event = q.get(timeout=20)
            except queue.Empty:
                # Keep the connection alive while agents are thinking
                yield _sse_comment("keepalive")
                continue

            if event is None:
                yield _sse({"type": "done"})
                break

            yield _sse(event)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
