"""
agents/prompt_expander.py  —  Stage 1: user prompt → animation scene plan
"""
import json
import re
from pathlib import Path
from agents.llm_client import call_llm

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "expander_system.txt").read_text()
MAX_TRIES = 3




def expand_prompt(user_prompt: str, kb_context: str = ""):
    """
    Call the LLM with the expander system prompt.
    Returns a list of scene dicts (the animation plan).
    Retries up to MAX_TRIES on JSON parse failure.
    """
    user_content = user_prompt
    if kb_context:
        user_content += f"\n\n=== KNOWLEDGE BASE EXAMPLES (reference only) ===\n{kb_context}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]
    content, elapsed = call_llm(
        messages=messages,
        temperature=0.2,
    )

    data=content.lstrip("```json").rstrip("```")


    # OPTIONAL: You can still run _validate_scene() as a safety net,
    # but the schema already guarantees all required fields exist
    # scene_plan = [_validate_scene(scene) for scene in scene_plan]

    return data, elapsed




# def _extract_json(raw: str) -> list[dict]:
#     """Parse the LLM response into a list of scene dicts, handling non-conformant shapes."""
#     text = raw.strip()
#
#     # Strip markdown fences
#     if "```" in text:
#         inner = text.split("```")[1]
#         if inner.startswith("json"):
#             inner = inner[4:]
#         text = inner.strip()
#
#     # Extract array even if there's surrounding prose
#     if not text.startswith("["):
#         match = re.search(r"\[.*\]", text, re.DOTALL)
#         if match:
#             text = match.group(0)
#
#     parsed = json.loads(text)
#
#     if isinstance(parsed, list):
#         return [_validate_scene(s, i + 1) for i, s in enumerate(parsed)]
#
#     # Handle {"scenes": [...]} wrapper
#     if isinstance(parsed, dict) and "scenes" in parsed:
#         scenes = parsed["scenes"]
#         return [_validate_scene(s, i + 1) for i, s in enumerate(scenes)]
#
#     raise ValueError(f"Expected JSON array of scenes, got: {type(parsed)}")


# def _validate_scene(scene: dict, index: int) -> dict:
#     """Fill in any missing fields with safe defaults."""
#     scene.setdefault("scene_number", index)
#     scene.setdefault("type", "main")
#     scene.setdefault("is_intro", scene.get("type") == "intro")
#     scene.setdefault("is_outro", scene.get("type") == "outro")
#     scene.setdefault("title", f"Scene {index}")
#     scene.setdefault("concept", "")
#     scene.setdefault("animation_description", "")
#     scene.setdefault("narration", "")
#     scene.setdefault("code_snippet", "")
#     scene.setdefault("relevant_lines", [])
#     scene.setdefault("variable_trace", [])
#     return scene
