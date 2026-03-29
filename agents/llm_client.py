"""
LLM client with multi-provider support.
Switch providers via LLM_PROVIDER env var or the --provider CLI flag in executor.py.
"""

import os
import requests
from functools import wraps
from time import time

# Per-provider defaults. Override model with LLM_MODEL env var or --model CLI flag.
PROVIDER_CONFIGS = {
    "local":     {
        "url":   None,  # reads LOCAL_LLM_URL env var
        "model": None,  # reads LLM_MODEL env var (required for local)
    },
    "openai":    {
        "url":   "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o",
    },
    "gemini":    {
        "url":   None,  # uses google-genai SDK, not HTTP directly
        "model": "gemini-3.1-pro-preview",
    },
    "anthropic": {
        "url":   "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-6",
    },
}


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        elapsed = time() - start
        return result, elapsed
    return wrapper


def call_llm(messages, temperature=0.7, response_format=None):
    """
    Universal LLM client. Routes to provider based on LLM_PROVIDER env var.

    Args:
        messages: List of {"role": "...", "content": "..."} dicts
        temperature: Sampling temperature (0.0-1.0)
        response_format: Optional schema for structured output (OpenAI-compatible only)

    Returns:
        (content: str, elapsed_seconds: float)
    """
    provider = os.getenv("LLM_PROVIDER", "local").lower()

    if provider not in PROVIDER_CONFIGS:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. Valid: {list(PROVIDER_CONFIGS)}")

    if provider == "anthropic":
        return _call_anthropic(messages, temperature)
    elif provider == "gemini":
        return _call_gemini(messages, temperature)
    else:
        return _call_openai_compat(messages, temperature, response_format, provider)


def _resolve_model(provider: str) -> str:
    """Return LLM_MODEL env var if set, otherwise the provider default."""
    return os.getenv("LLM_MODEL") or PROVIDER_CONFIGS[provider]["model"] or "unknown-model"


@timed
def _call_openai_compat(messages, temperature, response_format=None, provider="local"):
    cfg = PROVIDER_CONFIGS[provider]

    # local falls back to LOCAL_LLM_URL; cloud providers use their fixed URL
    url = cfg["url"] or os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:1234/v1/chat/completions")

    headers = {"Content-Type": "application/json"}
    if provider == "openai":
        headers["Authorization"] = f"Bearer {os.getenv('OPENAI_API_KEY')}"

    payload = {
        "model": _resolve_model(provider),
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }

    if response_format is not None:
        payload["response_format"] = response_format

    response = requests.post(url, headers=headers, json=payload, timeout=300)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


@timed
def _call_gemini(messages, temperature):
    """
    Google Gemini adapter using the official google-genai SDK.
    Reads GEMINI_API_KEY from the environment automatically.
    """
    from google import genai
    from google.genai import types

    client = genai.Client()  # picks up GEMINI_API_KEY from env

    # Separate system prompt from the conversation
    system_content = ""
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_content = msg["content"]
        elif msg["role"] == "user":
            contents.append(types.Content(role="user", parts=[types.Part(text=msg["content"])]))
        elif msg["role"] == "assistant":
            contents.append(types.Content(role="model", parts=[types.Part(text=msg["content"])]))

    config = types.GenerateContentConfig(temperature=temperature)
    if system_content:
        config.system_instruction = system_content

    response = client.models.generate_content(
        model=_resolve_model("gemini"),
        contents=contents,
        config=config,
    )
    return response.text


@timed
def _call_anthropic(messages, temperature):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01",
    }

    system_content = ""
    user_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_content = msg["content"]
        else:
            user_messages.append(msg)

    payload = {
        "model": _resolve_model("anthropic"),
        "max_tokens": 8192,
        "temperature": temperature,
        "messages": user_messages,
    }

    if system_content:
        payload["system"] = system_content

    response = requests.post(
        PROVIDER_CONFIGS["anthropic"]["url"], headers=headers, json=payload, timeout=300
    )
    response.raise_for_status()

    data = response.json()
    return data["content"][0]["text"]