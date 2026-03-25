"""
knowledge_base/retriever.py — retrieve relevant Manim examples from Supabase

Usage:
    from knowledge_base.retriever import retrieve_examples
    context = retrieve_examples("bubble sort array animation")
"""
import os
from dotenv import load_dotenv

load_dotenv()


def retrieve_examples(query: str, top_k: int = 3) -> str:
    """
    Find the top_k most relevant Manim code examples for the given query.
    Embeds the query with sentence-transformers, queries Supabase via pgvector.

    Returns a formatted string ready to inject into an LLM prompt.
    Returns empty string if Supabase is not configured or on any error.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return ""

    try:
        from supabase import create_client
        from knowledge_base.embeddings.embed import embed_text

        client    = create_client(url, key)
        embedding = embed_text(query)

        response = client.rpc("match_manim_examples", {
            "query_embedding": embedding,
            "match_count":     top_k,
        }).execute()

        if not response.data:
            return ""

        parts = []
        for row in response.data:
            parts.append(
                f"# Example: {row['title']}\n"
                f"# {row['description']}\n"
                f"{row['code']}"
            )
        return "\n\n---\n\n".join(parts)

    except Exception as e:
        import traceback
        print(f"[retriever] KB retrieval failed: {e}")
        traceback.print_exc()
        return ""
