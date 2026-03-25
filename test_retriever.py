"""
Diagnostic script for knowledge base retrieval.
Run: python test_retriever.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_KEY: {'set' if key else 'MISSING'}")

# --- Step 1: Can we connect and read the table directly? ---
print("\n--- Step 1: Direct table read ---")
try:
    from supabase import create_client
    client = create_client(url, key)
    resp = client.table("manim_examples").select("id, title, description").execute()
    print(f"Rows in manim_examples: {len(resp.data)}")
    for row in resp.data:
        print(f"  id={row['id']}  title={row['title']!r}  desc={row['description'][:60]!r}")
except Exception as e:
    import traceback
    print(f"FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# --- Step 2: Generate an embedding ---
print("\n--- Step 2: Embed query ---")
try:
    from knowledge_base.embeddings.embed import embed_text
    embedding = embed_text("binary search algorithm array")
    print(f"Embedding dim: {len(embedding)}  first 5 values: {embedding[:5]}")
except Exception as e:
    import traceback
    print(f"FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# --- Step 3: Call the RPC function ---
print("\n--- Step 3: RPC match_manim_examples ---")
try:
    resp = client.rpc("match_manim_examples", {
        "query_embedding": embedding,
        "match_count": 3,
    }).execute()
    print(f"RPC returned {len(resp.data)} rows")
    for row in resp.data:
        print(f"  title={row['title']!r}  similarity={row.get('similarity', 'N/A'):.4f}")
except Exception as e:
    import traceback
    print(f"FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nAll checks passed.")
