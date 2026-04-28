"use client";

import { useState } from "react";
import { motion, type Variants } from "framer-motion";

const PRESETS = [
  "An alarm clock that shocks you when you hit snooze",
  "Uber but for pets",
  "A smart fridge that monitors your diet and cyberbullies you",
];

const container: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
  exit: { transition: { staggerChildren: 0.04, staggerDirection: -1 } },
};

const item: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -16 },
};

export default function IdeaInput({
  onSubmit,
}: {
  onSubmit: (idea: string) => void;
}) {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = idea.trim();
    if (!trimmed || loading) return;
    setLoading(true);
    onSubmit(trimmed);
  };

  return (
    <motion.div
      className="h-full flex flex-col items-center justify-center px-6"
      variants={container}
      initial="hidden"
      animate="show"
      exit="exit"
    >
      {/* Logo mark */}
      <motion.div variants={item} className="mb-10">
        <div className="flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <polygon points="14,2 26,24 2,24" fill="#c9a84c" opacity="0.9" />
          </svg>
          <span
            className="text-xs tracking-[0.3em] uppercase text-muted"
            style={{ fontFamily: "var(--font-mono)" }}
          >
            AI Shark Tank
          </span>
        </div>
      </motion.div>

      {/* Headline */}
      <motion.h1
        variants={item}
        className="text-6xl sm:text-7xl font-bold text-center mb-4 leading-none tracking-tight"
        style={{ fontFamily: "var(--font-display)", color: "#c9a84c" }}
      >
        Pitch the Sharks.
      </motion.h1>

      <motion.p
        variants={item}
        className="text-muted text-lg text-center mb-10 max-w-md"
      >
        Enter your startup idea. Our AI investors will tear it apart.
      </motion.p>

      {/* Input form */}
      <motion.form
        variants={item}
        onSubmit={handleSubmit}
        className="w-full max-w-xl flex flex-col gap-4"
      >
        <div className="relative">
          <textarea
            rows={3}
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Tinder, but for finding a tennis partner…"
            className="w-full resize-none rounded-xl px-5 py-4 text-base outline-none transition-all duration-200"
            style={{
              background: "#111111",
              border: "1px solid #1e1e1e",
              color: "#f0f0f0",
              fontFamily: "var(--font-body)",
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = "#c9a84c";
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = "#1e1e1e";
            }}
            disabled={loading}
          />
        </div>

        {/* Preset chips */}
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setIdea(p)}
              className="px-3 py-1.5 rounded-full text-sm transition-all duration-150"
              style={{
                background: "#181818",
                border: "1px solid #2a2a2a",
                color: "#888",
                fontFamily: "var(--font-body)",
                cursor: "pointer",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#c9a84c";
                e.currentTarget.style.color = "#c9a84c";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#2a2a2a";
                e.currentTarget.style.color = "#888";
              }}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Submit */}
        <motion.button
          type="submit"
          disabled={!idea.trim() || loading}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-4 rounded-xl font-bold text-base tracking-wide transition-opacity duration-200"
          style={{
            background: "#c9a84c",
            color: "#080808",
            fontFamily: "var(--font-display)",
            opacity: idea.trim() && !loading ? 1 : 0.4,
            cursor: idea.trim() && !loading ? "pointer" : "default",
          }}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin"
                width="16"
                height="16"
                viewBox="0 0 16 16"
              >
                <circle
                  cx="8"
                  cy="8"
                  r="6"
                  stroke="currentColor"
                  strokeWidth="2"
                  fill="none"
                  opacity="0.3"
                />
                <path
                  d="M8 2a6 6 0 0 1 6 6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  fill="none"
                />
              </svg>
              Entering the tank…
            </span>
          ) : (
            "Enter the Tank →"
          )}
        </motion.button>
      </motion.form>
    </motion.div>
  );
}
