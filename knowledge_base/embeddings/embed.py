"""
knowledge_base/embeddings/embed.py — embed and store Manim examples in Supabase

Usage:
    # Store a single example manually
    from knowledge_base.embeddings.embed import store_example
    store_example(
        title="Binary Search",
        description="Binary search on a sorted array with mid pointer animation",
        code="...",
        source_file="binary_search.py",
        concepts="binary search, divide and conquer, mid pointer, sorted array",
        visual_elements="array cells, left right mid pointers, color highlight",
        difficulty="intermediate",
    )

    # Scan and store all .py files from knowledge_base/scenes/ (idempotent)
    from knowledge_base.embeddings.embed import store_all_scenes
    store_all_scenes()
"""

import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

# ── Model singleton ────────────────────────────────────────────────────────────
_MODEL = None


def _get_model():
    """Load sentence-transformer model once, reuse for the process lifetime."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        print("[embed] Loading sentence-transformer model…")
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        print("[embed] Model ready.")
    return _MODEL


# ── Core embedding ─────────────────────────────────────────────────────────────

def embed_text(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.
    Model is loaded once and cached for the process lifetime.
    """
    return _get_model().encode(text, normalize_embeddings=True).tolist()


def build_embedding_text(
    title: str,
    description: str,
    code: str,
    concepts: str = "",
    visual_elements: str = "",
) -> str:
    """
    Construct the compound text that gets embedded for a scene file.

    We combine multiple fields rather than just description because:
    - title      → matches high-level user queries ("binary search")
    - description → matches intent ("search in sorted array")
    - concepts    → matches algorithm vocabulary ("divide and conquer, mid pointer")
    - visual_elements → matches animation vocabulary ("pointer, highlight, swap")

    Code is intentionally excluded — it adds noise (variable names, syntax)
    that hurts semantic similarity more than it helps.
    """
    parts = []

    if title:
        parts.append(title)
    if description:
        parts.append(description)
    if concepts:
        parts.append(concepts)
    if visual_elements:
        parts.append(visual_elements)

    # Fallback: if somehow everything is empty, embed the first 500 chars of code
    if not parts and code:
        parts.append(code[:500])

    return " | ".join(parts)


# ── Docstring parser ───────────────────────────────────────────────────────────

def _parse_docstring_fields(code: str) -> dict[str, str]:
    """
    Extract structured KEY: value pairs from a scene file's header.

    Supports both triple-quoted docstrings and leading # comment blocks.
    Recognised keys: TITLE, CONCEPTS, VISUAL_ELEMENTS, DIFFICULTY

    Example scene header:
        \"\"\"
        TITLE: Binary Search — Logarithmic Narrowing
        CONCEPTS: binary search, divide and conquer, mid pointer, sorted array, search space
        VISUAL_ELEMENTS: array cells, left/right/mid pointers, color highlight, shrinking bounds
        DIFFICULTY: intermediate
        \"\"\"
    """
    recognised = {"TITLE", "CONCEPTS", "VISUAL_ELEMENTS", "DIFFICULTY"}
    fields: dict[str, str] = {}

    for line in code.splitlines():
        # Strip comment markers and whitespace
        stripped = line.strip().lstrip("#").strip()

        # Stop parsing once we hit actual code (class/def/import)
        if stripped.startswith(("class ", "def ",)):
            break

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip().upper()
            val = val.strip()
            if key in recognised and val:
                fields[key] = val

    return fields


def _extract_description(code: str, title: str) -> str:
    """
    Derive a one-line description from a scene file.
    Priority: parsed TITLE + CONCEPTS → first meaningful comment → generic fallback.
    """
    fields = _parse_docstring_fields(code)

    if fields.get("TITLE") and fields.get("CONCEPTS"):
        return f"{fields['TITLE']}. Concepts: {fields['CONCEPTS']}"

    if fields.get("TITLE"):
        return fields["TITLE"]

    if fields.get("CONCEPTS"):
        return f"{title}. Concepts: {fields['CONCEPTS']}"

    # Scan for a meaningful standalone comment
    for line in code.splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("#")
            and not stripped.startswith("#!")
            and not stripped.startswith("# -*-")
        ):
            candidate = stripped.lstrip("#").strip()
            if len(candidate) > 8:
                return candidate

    return f"Manim animation scene: {title}"


# ── Supabase helpers ───────────────────────────────────────────────────────────

def _get_supabase_client():
    """Return a Supabase client or raise a clear error if env vars are missing."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_KEY must be set in your .env file. "
            "Get them from: Supabase dashboard → Project Settings → API."
        )
    from supabase import create_client
    return create_client(url, key)


# ── Public API ─────────────────────────────────────────────────────────────────

def store_example(
    title: str,
    description: str,
    code: str,
    source_file: str = "",
    concepts: str = "",
    visual_elements: str = "",
    difficulty: str = "intermediate",
) -> None:
    """
    Embed and upsert a single Manim code example into Supabase.

    The upsert key is `source_file` — re-running with the same file name
    updates the existing row instead of inserting a duplicate.
    Pass source_file="" to always insert (e.g. for manually added snippets).

    Args:
        title:          Short human-readable name.
        description:    What this scene does — used for display, not embedding.
        code:           Full Manim Python source.
        source_file:    Filename (e.g. "binary_search.py") used as upsert key.
        concepts:       Comma-separated algorithm concepts.
        visual_elements: Comma-separated visual animation elements.
        difficulty:     "beginner" | "intermediate" | "advanced"
    """
    client = _get_supabase_client()

    embedding_text = build_embedding_text(
        title=title,
        description=description,
        code=code,
        concepts=concepts,
        visual_elements=visual_elements,
    )
    embedding = embed_text(embedding_text)

    row = {
        "title":           title,
        "description":     description,
        "code":            code,
        "embedding":       embedding,
        "concepts":        concepts,
        "visual_elements": visual_elements,
        "difficulty":      difficulty,
    }

    if source_file:
        row["source_file"] = source_file
        # Upsert: update existing row if source_file already exists
        client.table("manim_examples").upsert(
            row, on_conflict="source_file"
        ).execute()
        print(f"[embed] Upserted:  {title!r}  ({source_file})")
    else:
        row["source_file"] = None
        client.table("manim_examples").insert(row).execute()
        print(f"[embed] Inserted:  {title!r}  (manual)")


def store_examples_bulk(examples: list[dict]) -> None:
    """
    Store multiple examples. Each dict may contain any keys accepted by
    store_example(). Continues on individual failures.
    """
    success = 0
    for ex in examples:
        try:
            store_example(
                title          = ex.get("title", "Untitled"),
                description    = ex.get("description", ""),
                code           = ex.get("code", ""),
                source_file    = ex.get("source_file", ""),
                concepts       = ex.get("concepts", ""),
                visual_elements= ex.get("visual_elements", ""),
                difficulty     = ex.get("difficulty", "intermediate"),
            )
            success += 1
        except Exception as e:
            print(f"[embed] Failed to store {ex.get('title', '?')!r}: {e}")

    print(f"[embed] Bulk complete: {success}/{len(examples)} stored.")


def store_all_scenes(scenes_dir: str | None = None) -> None:
    """
    Read every .py file in knowledge_base/scenes/, parse its structured
    header, embed it, and upsert into Supabase. Safe to re-run at any time.

    Args:
        scenes_dir: Override the default scenes directory path.
    """
    if scenes_dir is None:
        scenes_dir = pathlib.Path(__file__).parent.parent / "scenes"
    else:
        scenes_dir = pathlib.Path(scenes_dir)

    scene_files = sorted(scenes_dir.glob("*.py"))

    if not scene_files:
        print(f"[embed] No .py files found in {scenes_dir}")
        return

    print(f"[embed] Found {len(scene_files)} scene file(s) in {scenes_dir}")
    success = 0

    for path in scene_files:
        try:
            code   = path.read_text(encoding="utf-8")
            fields = _parse_docstring_fields(code)

            # Use parsed TITLE if present, otherwise derive from filename
            title = fields.get("TITLE") or path.stem.replace("_", " ").title()

            # Build description from parsed fields
            description = _extract_description(code, title)

            store_example(
                title          = title,
                description    = description,
                code           = code,
                source_file    = path.name,
                concepts       = fields.get("CONCEPTS", ""),
                visual_elements= fields.get("VISUAL_ELEMENTS", ""),
                difficulty     = fields.get("DIFFICULTY", "intermediate"),
            )
            success += 1

        except Exception as e:
            import traceback
            print(f"[embed] Error processing {path.name}: {e}")
            traceback.print_exc()

    print(f"\n[embed] Done: {success}/{len(scene_files)} scenes stored successfully.")


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target = pathlib.Path(sys.argv[1])
        if target.is_dir():
            store_all_scenes(str(target))
        elif target.is_file():
            code   = target.read_text(encoding="utf-8")
            fields = _parse_docstring_fields(code)
            title  = fields.get("TITLE") or target.stem.replace("_", " ").title()
            store_example(
                title          = title,
                description    = _extract_description(code, title),
                code           = code,
                source_file    = target.name,
                concepts       = fields.get("CONCEPTS", ""),
                visual_elements= fields.get("VISUAL_ELEMENTS", ""),
                difficulty     = fields.get("DIFFICULTY", "intermediate"),
            )
        else:
            print(f"[embed] Path not found: {target}")
            sys.exit(1)
    else:
        # Default: embed everything in knowledge_base/scenes/
        store_all_scenes()