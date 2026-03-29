"""
pipeline/executor.py — full pipeline: user prompt → rendered video

Usage:
    python -m pipeline.executor "explain bubble sort"
    python pipeline/executor.py "explain binary search"
"""
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

# Ensure project root is on sys.path when run directly (python pipeline/executor.py)
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

ROOT      = Path(__file__).parent.parent
OUTPUTS   = ROOT / "outputs"
RAW_DIR   = OUTPUTS / "raw_responses"
VIDEO_DIR = OUTPUTS / "video"

MAX_RENDER_TRIES = 3
USE_KB = os.getenv("USE_KNOWLEDGE_BASE", "false").lower() == "true"


def run(user_prompt: str, quality_flag: str = "-ql",
        provider: str | None = None, model: str | None = None) -> str:
    """
    Execute the full pipeline for a given user prompt.

    Stages:
        0. KB Retrieval    — fetch relevant Manim examples (optional)
        1. Prompt Expander — user text → scene plan (list of scene dicts)
        2. Manim Coder     — scene plan → single Manim Python script
        3. Manim Render    — script → .mp4 via manim CLI (self-healing)
        4. Move            — copy final render to outputs/video/

    Args:
        provider: Override LLM_PROVIDER env var (local | openai | anthropic | gemini)
        model:    Override LLM_MODEL env var (e.g. gpt-4o, claude-sonnet-4-6)

    Returns the path to the final .mp4, or an empty string on failure.
    """
    if provider:
        os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model

    active_provider = os.getenv("LLM_PROVIDER", "local")
    active_model    = os.getenv("LLM_MODEL", "(provider default)")

    session_id  = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    session_dir = OUTPUTS / session_id

    for d in (session_dir, RAW_DIR, VIDEO_DIR):
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"[pipeline] Session:  {session_id}")
    print(f"[pipeline] Prompt:   {user_prompt}")
    print(f"[pipeline] Provider: {active_provider}  Model: {active_model}")
    print(f"{'='*60}")

    # ------------------------------------------------------------------
    # Stage 0 — KB Retrieval (optional)
    # ------------------------------------------------------------------
    kb_context = ""
    if USE_KB:
        print("\n[pipeline] Stage 0 — KB Retrieval")
        try:
            from knowledge_base.retriever import retrieve_examples
            kb_context = retrieve_examples(user_prompt)
            print(f"[pipeline] KB context: {len(kb_context)} chars")
        except Exception as e:
            print(f"[pipeline] KB retrieval failed (non-fatal): {e}")

    # ------------------------------------------------------------------
    # Stage 1 — Prompt Expander
    # ------------------------------------------------------------------
    print("\n[pipeline] Stage 1 — Prompt Expander")
    from agents.prompt_expander import expand_prompt

    try:
        scene_plan, expander_elapsed = expand_prompt(user_prompt, kb_context)
    except Exception as e:
        print(f"[pipeline] Expander failed: {e}")
        return ""

    expander_out = RAW_DIR / f"{session_id}_expander.json"
    expander_out.write_text(json.dumps(scene_plan, indent=2))
    print(f"[pipeline] Scene plan ({len(scene_plan)} scenes) in {expander_elapsed:.1f}s → {expander_out}")

    # ------------------------------------------------------------------
    # Stage 2 — Manim Coder
    # ------------------------------------------------------------------
    print("\n[pipeline] Stage 2 — Manim Coder")
    from agents.manim_coder import generate_manim_script

    try:
        code = generate_manim_script(scene_plan, kb_context)
    except Exception as e:
        print(f"[pipeline] Coder failed: {e}")
        return ""

    if not code:
        print("[pipeline] Coder returned empty script.")
        return ""

    script_path = session_dir / "animation.py"
    script_path.write_text(code)

    coder_out = RAW_DIR / f"{session_id}_coder.py"
    coder_out.write_text(code)
    print(f"[pipeline] Manim script → {script_path}")

    # ------------------------------------------------------------------
    # Stage 3 — Render (with self-healing on runtime failure)
    # ------------------------------------------------------------------
    print("\n[pipeline] Stage 3 — Manim Render")
    from agents.manim_coder import fix_manim_script

    current_code = code
    video_path   = None

    for render_attempt in range(1, MAX_RENDER_TRIES + 1):
        print(f"[pipeline] Render attempt {render_attempt}/{MAX_RENDER_TRIES}")
        video_path, stderr = _render(script_path, session_dir, quality_flag)
        if video_path:
            break

        if render_attempt == MAX_RENDER_TRIES:
            print("[pipeline] Render failed after all attempts.")
            return ""

        print("[pipeline] Render failed — sending stderr to coder for fix")
        current_code = fix_manim_script(scene_plan, current_code, stderr)
        script_path.write_text(current_code)

        fix_out = RAW_DIR / f"{session_id}_coder_fix{render_attempt}.py"
        fix_out.write_text(current_code)
        print(f"[pipeline] Fixed script → {fix_out}")

    # ------------------------------------------------------------------
    # Stage 4 — Move to outputs/video/
    # ------------------------------------------------------------------
    final_path = VIDEO_DIR / f"final_{session_id}.mp4"
    video_path.rename(final_path)
    print(f"\n[pipeline] Done! Final video → {final_path}")
    return str(final_path)


def _render(
    script_path: Path,
    session_dir: Path,
    quality_flag: str = "-ql",
) -> tuple[Path | None, str]:
    media_dir = session_dir / "media"
    cmd = [
        sys.executable, "-m", "manim",
        "render",
        "--media_dir", str(media_dir),
        quality_flag,   # set from settings: -ql / -qm / -qh
        str(script_path),
    ]
    print(f"[render] Running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )

    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"[render] Render failed (exit {result.returncode}).")
        print(f"[render] STDERR:\n{result.stderr}")
        return None, result.stderr

    # Manim writes to: media/videos/<script_stem>/<quality>/<ClassName>.mp4
    candidates = list(media_dir.rglob("*.mp4"))
    if candidates:
        return candidates[0], ""

    msg = "[render] Could not locate output .mp4 in media directory."
    print(msg)
    return None, msg


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manim AI Visualiser pipeline")
    parser.add_argument("prompt", nargs="*", help="Description of the concept to visualise")
    parser.add_argument("--provider", choices=["local", "openai", "anthropic", "gemini"],
                        default=None, help="LLM provider (overrides LLM_PROVIDER env var)")
    parser.add_argument("--model", default=None,
                        help="Model name (overrides LLM_MODEL env var and provider default)")
    parser.add_argument("--quality", default="-ql", choices=["-ql", "-qm", "-qh"],
                        help="Render quality: -ql low (default), -qm medium, -qh high")
    args = parser.parse_args()

    prompt = " ".join(args.prompt) if args.prompt else "explain binary search"
    path = run(prompt, quality_flag=args.quality, provider=args.provider, model=args.model)
    if path:
        print(f"\nSuccess: {path}")
    else:
        print("\nPipeline failed. Check logs above.")
        sys.exit(1)
