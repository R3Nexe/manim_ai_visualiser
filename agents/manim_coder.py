"""
agents/manim_coder.py  —  Stage 2: scene plan → Manim animation script
"""
import json
import os
import py_compile
import tempfile
from pathlib import Path
from agents.llm_client import call_llm

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "coder_system.txt").read_text()
MAX_TRIES = 3
USE_KNOWLEDGE_BASE = True


def generate_manim_script(scene_plan: str, kb_context: str = "") -> str:
    """
    Given the scene plan from the prompt expander, generate a single Manim Python file
    with one AnimationScene class whose construct() plays all scenes sequentially.
    Uses a self-healing loop on syntax failure (up to MAX_TRIES).
    """

    if USE_KNOWLEDGE_BASE and not kb_context:
        from knowledge_base.retriever import retrieve_examples
        query = " ".join(s[:100] for s in scene_plan)
        kb_context = retrieve_examples(query)
        if kb_context:
            print("[coder] KB context retrieved")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": _scene_plan_to_prompt(scene_plan, kb_context)},
    ]

    for attempt in range(1, MAX_TRIES + 1):
        print(f"[coder] attempt {attempt}/{MAX_TRIES}")
        raw, elapsed = call_llm(messages, temperature=0.2)
        print(f"[coder] LLM call took {elapsed:.1f}s")

        code = _extract_code(raw)
        error = _validate_code(code)

        if error is None:
            print("[coder] syntax OK")
            return code

        print(f"[coder] syntax error on attempt {attempt}: {error}")
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": (
                f"Syntax error:\n\n{error}\n\n"
                "Fix the error and return the complete corrected Python file. "
                "No markdown, no explanation — raw Python only."
            ),
        })

    print(f"[coder] failed after {MAX_TRIES} attempts")
    return


def _scene_plan_to_prompt(scene_plan: list[dict], kb_context: str = "") -> str:
    n = len(scene_plan)
    parts = [
        f"Generate a complete Manim animation script for {n} scene(s).",
        "ONE class: AnimationScene(Scene). construct() plays all scenes sequentially.",
        f"\nSCENE PLAN (JSON):\n{json.dumps(scene_plan, indent=2)}",
    ]
    if kb_context:
        parts.append(f"\n=== REFERENCE EXAMPLES (style guide only) ===\n{kb_context}")
    return "\n".join(parts)


def _extract_code(raw: str) -> str:
    """Strip markdown fences if the model wrapped the code."""
    if "```" in raw:
        content = raw.split("```")[1]
        if content.startswith("python"):
            content = content[6:]
        return content.strip()
    return raw.strip()


def fix_manim_script(scene_plan: list[dict], code: str, stderr: str) -> str:
    """
    Given a Manim script that failed at runtime and its stderr output,
    ask the LLM to fix it. Applies the same self-healing + syntax-check loop.
    Returns the (best-effort) corrected code.
    """
    messages = [
        {"role": "system",    "content": SYSTEM_PROMPT},
        {"role": "user",      "content": _scene_plan_to_prompt(scene_plan)},
        {"role": "assistant", "content": code},
        {
            "role": "user",
            "content": (
                f"The script raised a runtime error:\n\n{stderr}\n\n"
                "Fix the error and return the complete corrected Python file. "
                "No markdown, no explanation — raw Python only."
            ),
        },
    ]

    last_code = code
    for attempt in range(1, MAX_TRIES + 1):
        print(f"[coder:fix] attempt {attempt}/{MAX_TRIES}")
        raw, elapsed = call_llm(messages, temperature=0.2)
        print(f"[coder:fix] LLM call took {elapsed:.1f}s")

        fixed = _extract_code(raw)
        error = _validate_code(fixed)

        if error is None:
            print("[coder:fix] syntax OK")
            return fixed

        last_code = fixed
        print(f"[coder:fix] syntax error on attempt {attempt}: {error}")
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": (
                f"Syntax error:\n\n{error}\n\n"
                "Fix the error and return the complete corrected Python file. "
                "No markdown, no explanation — raw Python only."
            ),
        })

    print(f"[coder:fix] failed after {MAX_TRIES} attempts — returning last generated code")
    return last_code


def _validate_code(code: str) -> str | None:
    """Syntax-check via py_compile. Returns None on success, error string on failure."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        py_compile.compile(tmp_path, doraise=True)
        return None
    except py_compile.PyCompileError as e:
        return str(e)
    finally:
        os.unlink(tmp_path)
