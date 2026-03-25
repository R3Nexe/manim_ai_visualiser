"""
knowledge_base/embeddings/embed.py — embed and store Manim examples in Supabase

Usage:
    from knowledge_base.embeddings.embed import store_example, embed_text

    store_example(
        title="Bubble sort swap",
        description="Animate swapping two adjacent array elements using label moves",
        code="self.play(label_i.animate.move_to(...), ...)"
    )

    # Scan and store all .py files from knowledge_base/scenes/
    store_all_scenes()
"""
import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def embed_text(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.
    Model is loaded once and cached for the process lifetime.
    """
    return _get_model().encode(text).tolist()


def store_example(title: str, description: str, code: str) -> None:
    """
    Embed and upsert a Manim code example into Supabase.

    Args:
        title:       Short name, e.g. "Bubble sort swap animation"
        description: What this code does — used for semantic retrieval matching
        code:        The Manim Python snippet
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    from supabase import create_client

    client    = create_client(url, key)
    embedding = embed_text(description)

    client.table("manim_examples").insert({
        "title":     title,
        "description": description,
        "code":      code,
        "embedding": embedding,
    }).execute()

    print(f"[embed] Stored: {title!r}")


def store_examples_bulk(examples: list[dict]) -> None:
    """
    Bulk insert multiple examples.
    Each dict must have keys: title, description, code.
    """
    for ex in examples:
        store_example(ex["title"], ex["description"], ex["code"])


def store_all_scenes(scenes_dir: str | None = None) -> None:
    """
    Read every .py file in knowledge_base/scenes/, derive a title and
    description from the filename and file contents, then embed and store
    each one in Supabase.

    Args:
        scenes_dir: Path to the scenes directory. Defaults to
                    <repo_root>/knowledge_base/scenes/ relative to this file.
    """
    if scenes_dir is None:
        scenes_dir = pathlib.Path(__file__).parent.parent / "scenes"
    else:
        scenes_dir = pathlib.Path(scenes_dir)

    scene_files = sorted(scenes_dir.glob("*.py"))
    if not scene_files:
        print(f"[embed] No .py files found in {scenes_dir}")
        return

    for path in scene_files:
        code = path.read_text(encoding="utf-8")

        # Derive a human-readable title from the filename, e.g.
        # "binary_search.py" → "Binary Search"
        title = path.stem.replace("_", " ").title()

        # Build a short description: extract the first comment line that
        # starts with "# ---" (section header), otherwise fall back to a
        # generic description built from the title.
        description = _extract_description(code, title)

        store_example(title=title, description=description, code=code)


def _extract_description(code: str, title: str) -> str:
    """
    Heuristically derive a one-line description from scene source code.

    Strategy (in priority order):
    1. First non-empty line that starts with '#' and is not a shebang
    2. The title of the Text() object on the intro title line
    3. Generic fallback: "Manim animation scene: <title>"
    """
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            candidate = stripped.lstrip("#").strip()
            if candidate and len(candidate) > 4:
                return candidate

    # Fallback
    return f"Manim animation scene: {title}"
