import json
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

# from knowledge_base.retriever import retrieve, format_for_expander
import dotenv
load_dotenv()

LM_STUDIO_URL = os.getenv("LOCAL_LLM_URL")

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "expander_system.txt").read_text()

def get_scene_plan_json(user_prompt):
    # hits=retrieve(user_prompt)
    # rag_context=format_for_expander(hits)
    # if rag_context:
    #     user_prompt=f"{rag_context}\n\nUSER TOPIC:\n\n{user_prompt}"
    payload = {
        "model": "google/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": f"{SYSTEM_PROMPT}"},
            {"role": "user", "content": f"{user_prompt}"},
        ],
        "temperature": 0.4,
    }
    response = requests.post(LM_STUDIO_URL, json=payload,timeout=120)
    content = response.json()["choices"][0]["message"]["content"]
    return extract_json(content)
def extract_json(raw):
    if "```" in raw:
        content = raw.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        raw = content.strip()

    scene_plan = json.loads(raw)

    return [_validate_scene(s, i) for i, s in enumerate(scene_plan)]

def _validate_scene(scene: dict, index: int) -> dict:
    defaults = {
        "scene_number":          index + 1,
        "title":                 f"Scene {index + 1}",
        "concept":               "",
        "animation_description": "",
        "narration":             "",
    }
    return {**defaults, **scene}