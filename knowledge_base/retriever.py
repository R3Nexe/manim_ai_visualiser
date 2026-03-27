"""
knowledge_base/retriever.py — retrieve relevant Manim examples from Supabase
                               with a local cosine-similarity fallback.

Usage:
    from knowledge_base.retriever import retrieve_examples

    # Returns a formatted string ready to inject into an LLM prompt.
    # Falls back to local file scan if Supabase is unavailable.
    context = retrieve_examples("binary search sorted array")
    context = retrieve_examples("bubble sort swap animation", top_k=2)
    context = retrieve_examples("graph BFS", threshold=0.35)
"""

import os
import pathlib
import traceback
from dotenv import load_dotenv

load_dotenv()

# Default similarity threshold.
# Scores below this are considered noise and excluded from the prompt.
# Tune by running: SELECT title, 1-(embedding<=>query) FROM manim_examples ORDER BY 2 DESC
DEFAULT_THRESHOLD: float = 0.30
DEFAULT_TOP_K: int = 3


# ── Public API ─────────────────────────────────────────────────────────────────

def retrieve_examples(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_THRESHOLD,
) -> str:
    """
    Find the most relevant Manim code examples for a user query.

    Strategy:
        1. Try Supabase (pgvector cosine search) — fast, works at scale.
        2. If Supabase is unconfigured or errors, fall back to local cosine
           similarity scan across knowledge_base/scenes/*.py files.
        3. If nothing passes the threshold, return "" so the LLM generates
           code from scratch rather than using an irrelevant example.

    Args:
        query:     Natural-language description of what the user wants animated.
        top_k:     Maximum number of examples to return.
        threshold: Minimum cosine similarity score (0–1) to include a result.

    Returns:
        A formatted string ready to prepend to an LLM system prompt,
        or "" if no relevant examples were found.
    """
    if not query or not query.strip():
        return ""

    # ── Try Supabase first ────────────────────────────────────────────────────
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        result = _retrieve_from_supabase(query, top_k, threshold)
        if result is not None:          # None means "Supabase failed, try local"
            return result
        print("[retriever] Supabase failed — falling back to local scan.")
    else:
        print("[retriever] Supabase not configured — using local scan.")

    # ── Local fallback ────────────────────────────────────────────────────────
    return _retrieve_local(query, top_k, threshold)


# ── Supabase retrieval ─────────────────────────────────────────────────────────

def _retrieve_from_supabase(
    query: str,
    top_k: int,
    threshold: float,
) -> str | None:
    """
    Query Supabase via the match_manim_examples RPC.

    Returns:
        Formatted string on success (may be "" if nothing passes threshold).
        None if Supabase raised an exception (triggers local fallback).
    """
    try:
        from supabase import create_client
        from knowledge_base.embeddings.embed import embed_text

        client    = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        embedding = embed_text(query)

        response = client.rpc(
            "match_manim_examples",
            {
                "query_embedding": embedding,
                "match_count":     top_k,
                "match_threshold": threshold,
            },
        ).execute()

        rows = response.data or []

        if not rows:
            print(
                f"[retriever] Supabase: no results above threshold "
                f"{threshold} for query: {query!r}"
            )
            return ""

        print(f"[retriever] Supabase: {len(rows)} result(s) for {query!r}")
        return _format_results(rows, source="supabase")

    except Exception as e:
        print(f"[retriever] Supabase error: {e}")
        traceback.print_exc()
        return None          # signal caller to use local fallback


# ── Local fallback retrieval ───────────────────────────────────────────────────

def _retrieve_local(
    query: str,
    top_k: int,
    threshold: float,
) -> str:
    """
    Pure in-process fallback — no Supabase required.

    Embeds the query and all scene files, scores them with cosine similarity,
    and returns the top results that pass the threshold.

    Slower than Supabase (O(n) embeddings on every call) but works instantly
    during development with zero infrastructure setup.
    """
    try:
        import numpy as np
        from knowledge_base.embeddings.embed import (
            embed_text,
            build_embedding_text,
            _extract_description,
            _parse_docstring_fields,
        )

        scenes_dir = pathlib.Path(__file__).parent / "scenes"
        files      = sorted(scenes_dir.glob("*.py"))

        if not files:
            print(f"[retriever/local] No .py files found in {scenes_dir}")
            return ""

        print(f"[retriever/local] Scoring {len(files)} scene file(s) for {query!r}")

        query_vec = np.array(embed_text(query), dtype=np.float32)
        scored: list[tuple[float, dict]] = []

        for path in files:
            try:
                code   = path.read_text(encoding="utf-8")
                fields = _parse_docstring_fields(code)
                title  = fields.get("TITLE") or path.stem.replace("_", " ").title()
                desc   = _extract_description(code, title)

                doc_text = build_embedding_text(
                    title          = title,
                    description    = desc,
                    code           = code,
                    concepts       = fields.get("CONCEPTS", ""),
                    visual_elements= fields.get("VISUAL_ELEMENTS", ""),
                )
                doc_vec = np.array(embed_text(doc_text), dtype=np.float32)

                # Cosine similarity (vectors are already L2-normalised by embed_text)
                sim = float(np.dot(query_vec, doc_vec))

                scored.append((sim, {
                    "title":       title,
                    "description": desc,
                    "code":        code,
                    "similarity":  sim,
                    "source_file": path.name,
                }))

            except Exception as e:
                print(f"[retriever/local] Error reading {path.name}: {e}")

        # Sort descending by similarity, apply threshold, take top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        passing = [row for sim, row in scored if sim >= threshold][:top_k]

        if not passing:
            print(
                f"[retriever/local] No results above threshold "
                f"{threshold}. Best was {scored[0][0]:.3f} ({scored[0][1]['title']!r})"
                if scored else "[retriever/local] No scene files scored."
            )
            return ""

        print(f"[retriever/local] {len(passing)} result(s) passed threshold.")
        return _format_results(passing, source="local")

    except Exception as e:
        print(f"[retriever/local] Fatal error: {e}")
        traceback.print_exc()
        return ""


# ── Output formatter ───────────────────────────────────────────────────────────

def _format_results(rows: list[dict], source: str = "") -> str:
    """
    Format retrieved examples into a string suitable for LLM prompt injection.

    Structure per example:
        # Example: <title>
        # Source: <source_file>   (if present)
        # Similarity: <score>
        # Concepts: <description>
        <code>

    Examples are separated by a clear delimiter so the LLM can distinguish
    where one example ends and the next begins.
    """
    parts = []

    for row in rows:
        sim         = row.get("similarity", 0.0)
        title       = row.get("title", "Unknown")
        description = row.get("description", "")
        code        = row.get("code", "").strip()
        source_file = row.get("source_file", "")

        print(
            f"[retriever/{source}] ✓ {title!r}  "
            f"similarity={sim:.3f}"
            + (f"  file={source_file}" if source_file else "")
        )

        header_lines = [f"# Example: {title}"]
        if source_file:
            header_lines.append(f"# Source: {source_file}")
        header_lines.append(f"# Similarity: {sim:.3f}")
        if description:
            header_lines.append(f"# Concepts: {description}")

        parts.append("\n".join(header_lines) + "\n\n" + code)

    return "\n\n# " + "─" * 60 + "\n\n".join(parts)


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    query     = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "binary search"
    top_k     = int(os.getenv("RETRIEVER_TOP_K",    str(DEFAULT_TOP_K)))
    threshold = float(os.getenv("RETRIEVER_THRESHOLD", str(DEFAULT_THRESHOLD)))

    print(f"\nQuery:     {query!r}")
    print(f"Top-k:     {top_k}")
    print(f"Threshold: {threshold}")
    print("─" * 60)

    result = retrieve_examples(query, top_k=top_k, threshold=threshold)

    if result:
        print("\n── Retrieved context ──────────────────────────────────────")
        print(result)
    else:
        print("\n[retriever] No relevant examples found.")