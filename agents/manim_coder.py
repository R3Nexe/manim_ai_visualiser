import os
import re
import subprocess
import tempfile
import requests
from pathlib import Path
from dotenv import load_dotenv

# from knowledge_base.retriever import retrieve, format_for_coder
load_dotenv()

LM_STUDIO_URL = os.getenv("LOCAL_LLM_URL")

# Toggle to enable/disable knowledge-base context injection.
# Flip to True once the knowledge base is integrated.
USE_KNOWLEDGE_BASE = False

MAX_TRIES = 3

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "coder_system.txt").read_text()


# ---------------------------------------------------------------------------
# Knowledge-base context (scaffold — wired up when USE_KNOWLEDGE_BASE = True)
# ---------------------------------------------------------------------------

def _get_kb_context(scene: dict) -> str:
    """Return relevant KB snippets for this scene, or empty string."""
    if not USE_KNOWLEDGE_BASE:
        return ""
    # hits = retrieve(scene.get("concept", "") + " " + scene.get("animation_description", ""))
    # return format_for_coder(hits)
    return ""


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def _call_llm(messages: list[dict]) -> str:
    payload = {
        "model": "google/gpt-oss-20b",
        "messages": messages,
        "temperature": 0.2,
    }
    response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
    return response.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Code extraction & validation
# ---------------------------------------------------------------------------

def _extract_code(raw: str) -> str:
    """Pull the Python block out of a fenced code response."""
    if "```" in raw:
        block = raw.split("```")[1]
        if block.startswith("python"):
            block = block[6:]
        return block.strip()
    return raw.strip()


def _validate_code(code: str) -> tuple[bool, str]:
    """
    Write code to a temp file and do a syntax-only check via `py_compile`.
    Returns (ok, error_message).
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    result = subprocess.run(
        ["python", "-m", "py_compile", tmp_path],
        capture_output=True,
        text=True,
    )
    os.unlink(tmp_path)

    if result.returncode == 0:
        return True, ""
    return False, result.stderr.strip()


# ---------------------------------------------------------------------------
# Per-scene code generation with self-healing loop
# ---------------------------------------------------------------------------

def generate_scene_code(scene: dict) -> dict:
    """
    Generate Manim Python code for a single scene dict.

    Returns the scene dict with an added 'code' key and a 'attempts' log.
    Raises RuntimeError if all attempts fail.
    """
    kb_context = _get_kb_context(scene)

    user_content = (
        f"{kb_context}\n\n" if kb_context else ""
    ) + (
        f"Scene {scene.get('scene_number', '?')}: {scene.get('title', '')}\n\n"
        f"Concept: {scene.get('concept', '')}\n\n"
        f"Animation description: {scene.get('animation_description', '')}\n\n"
        f"Narration: {scene.get('narration', '')}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]

    attempts = []
    last_error = None

    for attempt in range(1, MAX_TRIES + 1):
        raw = _call_llm(messages)
        code = _extract_code(raw)
        ok, error = _validate_code(code)

        attempts.append({"attempt": attempt, "ok": ok, "error": error or None})

        if ok:
            return {**scene, "code": code, "attempts": attempts}

        last_error = error
        # Feed the error back so the model can self-correct
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": (
                f"The code you produced has a syntax error. "
                f"Fix it and return only the corrected Python code.\n\nError:\n{error}"
            ),
        })

    raise RuntimeError(
        f"Scene {scene.get('scene_number')} failed after {MAX_TRIES} attempts. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_all_scenes(scene_plan: list[dict]) -> list[dict]:
    """
    Accepts the list of scene dicts produced by prompt_expander.get_scene_plan_json()
    and returns the same list with 'code' and 'attempts' added to each scene.
    """
    results = []
    for scene in scene_plan:
        result = generate_scene_code(scene)
        results.append(result)
    return results
