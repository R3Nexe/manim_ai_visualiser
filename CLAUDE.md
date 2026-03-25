# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multi-agent pipeline that converts natural language algorithm descriptions into animated Manim visualizations. Input: a text prompt describing a DSA concept. Output: `final.mp4`.

**Primary development target**: local LLMs (LM Studio / Ollama) with a provider abstraction layer that allows later migration to OpenAI, Anthropic, or Gemini without changing agent code.

## Directory Structure

```
manim_ai_visualiser/
├── .env                          # Environment variables (not committed)
├── requirements.txt              # Python dependencies
├── app.py                        # Streamlit UI (stub)
├── config.py                     # Centralized config (stub)
├── agents/
│   ├── llm_client.py             # Unified LLM call entry point
│   ├── prompt_expander.py        # Stage 1: prompt → scene plan
│   ├── manim_coder.py            # Stage 2: scene dict → Manim code
│   └── prompts/
│       ├── expander_system.txt   # System prompt for scene planner
│       └── coder_system.txt      # System prompt for Manim coder (empty stub)
├── pipeline/
│   ├── session.py                # Orchestrator for all 4 stages (stub)
│   ├── executor.py               # Manim render CLI wrapper (stub)
│   └── stitcher.py               # FFmpeg video concat (stub)
├── knowledge_base/
│   ├── retriever.py              # Supabase vector retrieval (stub)
│   └── embeddings/
│       ├── embed.py              # Embedding generation (stub)
│       └── schema.sql            # Supabase vector table schema (stub)
├── ui/
│   └── components.py             # Streamlit component library (stub)
└── outputs/
    ├── <session_id>/             # Per-scene .py files and renders
    ├── raw_responses/            # LLM raw + parsed output logs
    └── video/                    # Final stitched videos
```

## Commands

```bash
# Test the prompt expander agent (accepts optional prompt arg)
python test_expander.py
python test_expander.py "explain merge sort"

# Test the manim coder agent against a boilerplate scene dict
python test_coder.py

# End-to-end integration test (not yet implemented)
python manim_test.py
python manim_test.py "explain binary search"
```

> Note: `test_expander.py`, `test_coder.py`, and `manim_test.py` replace the earlier `tests.py` monolith.

## Environment Setup

`.env` (not committed — copy manually):

```
LOCAL_LLM_URL=http://127.0.0.1:1234/v1/chat/completions   # LM Studio / Ollama
LLM_PROVIDER=local   # local | openai | anthropic | gemini
```

Cloud provider keys (add as needed):
```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

## Pipeline Architecture

Four sequential stages orchestrated by `pipeline/session.py`:

```
User Prompt
  → [1] agents/prompt_expander.py   — LLM call → JSON scene plan (4–6 scene dicts)
  → [2] agents/manim_coder.py       — LLM call per scene → Manim Python code (self-healing, ≤3 retries)
  → [3] pipeline/executor.py        — manim render CLI → per-scene .mp4s              [stub]
  → [4] pipeline/stitcher.py        — FFmpeg concat → outputs/video/final_<id>.mp4    [stub]
```

**Implementation status**:
- ✅ Stage 1 — Prompt Expander: complete (being refactored in `feature/ai`)
- ✅ Stage 2 — Manim Coder: complete (being refactored in `feature/ai`)
- ❌ Stage 3 — Executor: empty stub
- ❌ Stage 4 — Stitcher: empty stub
- ❌ Session orchestrator: empty stub

## The Scene Dict

The central data structure that flows through all pipeline stages. Fields are added incrementally:

| Field | Added by | Notes |
|---|---|---|
| `scene_number` | expander | 1-based index |
| `title` | expander | Short human-readable title |
| `concept` | expander | The specific sub-concept animated |
| `is_intro` / `is_outro` | expander | Layout mode flag |
| `animation_description` | expander | Manim-friendly choreography instructions |
| `narration` | expander | 1–2 sentence viewer takeaway |
| `code_snippet` | expander | Algorithm source code excerpt |
| `relevant_lines` | expander | Line numbers highlighted in code panel |
| `variable_trace` | expander | Variable state per step |
| `code` | coder | Generated Manim Python source |
| `attempts` | coder | Number of self-healing retries used |
| `llm_time` | coder | Seconds spent on LLM call(s) |

## LLM Client (`agents/llm_client.py`)

Single entry point for all LLM calls: `call_llm(messages, temperature) → (content, elapsed_seconds)`.

Provider routing via `LLM_PROVIDER` env var:
- `local` / `openai` / `gemini` → shared OpenAI-compatible HTTP path (`LOCAL_LLM_URL` or provider base URL)
- `anthropic` → separate adapter that extracts the `system` role out of `messages[]` (Anthropic Messages API requires system prompt separately)

All agents import only `call_llm` — they are unaware of the active provider.

## Agent Details

### Stage 1 — Prompt Expander (`agents/prompt_expander.py`)

- Input: plain-text user prompt
- Output: `list[dict]` scene plan
- Temperature: 0.4
- System prompt: `agents/prompts/expander_system.txt`
- Key functions:
  - `expand_prompt(prompt)` → main entry point
  - `_extract_json(raw)` → robust JSON parser (see below)
  - `_validate_scene(scene)` → fills in missing fields with defaults

**LLM JSON Parsing Robustness** — `_extract_json()` handles three non-conformant response shapes:
1. Array wrapped in a markdown fence (` ```json … ``` `)
2. Array wrapped in a JSON object (`{"scenes": [...]}`)
3. A single scene dict instead of an array (wraps it in a list)

### Stage 2 — Manim Coder (`agents/manim_coder.py`)

- Input: single scene dict
- Output: same scene dict with `code`, `attempts`, `llm_time` added
- Temperature: 0.2
- System prompt: `agents/prompts/coder_system.txt` (currently empty stub — inline prompt used)
- `MAX_TRIES = 3`
- Key functions:
  - `generate_scene_code(scene)` → self-healing loop per scene
  - `generate_all_scenes(scene_plan)` → batch entry point
  - `_extract_code(raw)` → strips markdown fences from LLM response
  - `_validate_code(code)` → syntax check via `py_compile` in a temp file
  - `_get_kb_context(scene)` → knowledge base retrieval (disabled)

**Self-healing loop**: on `py_compile` failure, the error traceback is appended to the message history and the LLM is asked to fix its own output. Raises `RuntimeError` after `MAX_TRIES` failed attempts.

## Key Constraints (enforced in system prompts)

**Three-zone canvas layout** — applies to all non-intro/non-outro scenes:
- LEFT (~x = -3.3): visualization (arrays, trees, graphs)
- RIGHT-TOP (~x = 3.3, y = 1.8): code panel
- RIGHT-BOTTOM (~x = 3.3, y = -1.8): variable trace table

**No LaTeX** — use `Text()` only. Hard constraint due to Manim compatibility issues.

**Each scene is independently renderable** — no shared state or imports between scenes.

## Output Layout

```
outputs/
  <session_id>/             ← scene_1.py … scene_N.py + per-scene renders
  raw_responses/
    <id>_expander_raw.txt   ← raw LLM text from expander
    <id>_expander.json      ← parsed scene plan
    <id>_coder.json         ← scene plan with generated code
  video/
    final_<id>.mp4          ← stitched final video
```

## Dependencies (`requirements.txt`)

| Package | Purpose |
|---|---|
| `manim>=0.18.0` | Animation engine |
| `openai>=1.30.0` | LLM client (OpenAI-compatible endpoints) |
| `requests` | Fallback HTTP for local LLM calls |
| `python-dotenv>=1.0.0` | `.env` loading |
| `streamlit>=1.35.0` | UI (inactive) |
| `sentence-transformers>=3.0.0` | Embeddings for knowledge base (inactive) |
| `supabase>=2.4.0` | Vector store (inactive) |
| `ffmpeg-python>=0.2.0` | Video stitching (inactive) |

## Inactive / Scaffolded Features

- **Knowledge base** (`knowledge_base/`): Supabase + sentence-transformers scaffolding exists. Disabled via `USE_KNOWLEDGE_BASE = False` in `manim_coder.py`. Intended to provide few-shot Manim examples as RAG context for the coder.
- **Streamlit UI** (`app.py`, `ui/components.py`): empty stubs.
- **Config module** (`config.py`): empty stub — all config currently via `.env` + `os.getenv`.
- **`coder_system.txt`**: empty — coder currently uses an inline system prompt string.

## Development Notes

- Primary inference target is **local LLMs via LM Studio** (`LLM_PROVIDER=local`). Cloud providers (OpenAI, Anthropic, Gemini) are supported via the `llm_client.py` abstraction and are intended for future quality comparisons or production use.
- The `feature/ai` branch is the active development branch. Agent files (`prompt_expander.py`, `manim_coder.py`) are currently being rewritten there.
- `tests.py` was deleted in the current branch; test files are being split into per-agent scripts (`test_expander.py`, `test_coder.py`, `manim_test.py`).
