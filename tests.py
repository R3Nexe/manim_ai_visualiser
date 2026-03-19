"""
Run from project root:
    python tests.py              # runs all tests
    python tests.py expander     # runs only prompt expander test
    python tests.py coder        # runs only manim coder test
"""
import sys

DIVIDER = "=" * 60
SUBDIV  = "-" * 40

TEST_PROMPT = "explain binary search"


def _header(title: str):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def _scene_block(scene: dict):
    print(f"\n  Scene {scene['scene_number']}: {scene['title']}")
    print(f"  {SUBDIV}")
    print(f"\n  Concept\n  {scene['concept']}")
    print(f"\n  Animation\n  {scene['animation_description']}")
    print(f"\n  Narration\n  {scene['narration']}")
    print()


# ── Test 1: Prompt Expander ───────────────────────────────────────────────────

def test_prompt_expander():
    _header(f"TEST: Prompt Expander  |  prompt: \"{TEST_PROMPT}\"")
    from agents.prompt_expander import get_scene_plan_json

    plan = get_scene_plan_json(TEST_PROMPT)

    if not plan:
        print("  [FAIL] No scenes returned.\n")
        return None

    print(f"  [PASS] {len(plan)} scene(s) returned.")
    for scene in plan:
        _scene_block(scene)

    print(DIVIDER + "\n")
    return plan


# ── Test 2: Manim Coder ───────────────────────────────────────────────────────

def test_manim_coder(plan=None):
    _header("TEST: Manim Coder")

    try:
        from agents.manim_coder import generate_manim_code
    except ImportError:
        print("  [SKIP] agents.manim_coder not implemented yet.\n")
        print(DIVIDER + "\n")
        return

    if plan is None:
        print("  [SKIP] No scene plan provided — run expander first.\n")
        print(DIVIDER + "\n")
        return

    for scene in plan:
        print(f"\n  Generating code for Scene {scene['scene_number']}: {scene['title']} ...")
        code = generate_manim_code(scene)
        if code:
            print(f"  [PASS] Code generated ({len(code)} chars)")
            print(f"\n{code}\n")
        else:
            print("  [FAIL] No code returned.")

    print(DIVIDER + "\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if target in ("all", "expander"):
        plan = test_prompt_expander()
    else:
        plan = None

    if target in ("all", "coder"):
        test_manim_coder(plan)
