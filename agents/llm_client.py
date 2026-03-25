"""
Modified llm_client.py to support structured output via response_format
"""

import os
import requests
from functools import wraps
from time import time

# Existing decorator stays the same
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        elapsed = time() - start
        return result, elapsed
    return wrapper


# MODIFIED: Add response_format parameter
def call_llm(messages, temperature=0.7, response_format=None):
    """
    Universal LLM client. Routes to provider based on LLM_PROVIDER env var.

    Args:
        messages: List of {"role": "...", "content": "..."} dicts
        temperature: Sampling temperature (0.0-1.0)
        response_format: Optional schema for structured output (OpenAI-compatible only)
                        Pass the entire schema dict from scene_plan_schema.py

    Returns:
        (content: str, elapsed_seconds: float)
    """
    provider = os.getenv("LLM_PROVIDER", "local").lower()

    if provider == "anthropic":
        return _call_anthropic(messages, temperature)
    elif provider in ["local", "openai", "gemini"]:
        return _call_openai_compat(messages, temperature, response_format)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


@timed
def _call_openai_compat(messages, temperature, response_format=None):
    """
    MODIFIED: Now accepts response_format parameter
    """
    url = os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:1234/v1/chat/completions")
    headers = {"Content-Type": "application/json"}

    # Add API key for OpenAI/Gemini
    provider = os.getenv("LLM_PROVIDER", "local").lower()
    if provider == "openai":
        headers["Authorization"] = f"Bearer {os.getenv('OPENAI_API_KEY')}"
    elif provider == "gemini":
        headers["Authorization"] = f"Bearer {os.getenv('GEMINI_API_KEY')}"

    payload = {
        "model": os.getenv("LLM_MODEL", "LOCAL_LLM_MODEL"),
        "messages": messages,
        "temperature": temperature,
        "stream": False
    }

    # MODIFIED: Add response_format if provided
    if response_format is not None:
        payload["response_format"] = response_format

    response = requests.post(url, headers=headers, json=payload, timeout=300)
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content


@timed
def _call_anthropic(messages, temperature):
    """
    Anthropic-specific adapter (unchanged - doesn't support response_format)
    """
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01"
    }

    # Extract system message
    system_content = ""
    user_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_content = msg["content"]
        else:
            user_messages.append(msg)

    payload = {
        "model": os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022"),
        "max_tokens": 8192,
        "temperature": temperature,
        "messages": user_messages
    }

    if system_content:
        payload["system"] = system_content

    response = requests.post(url, headers=headers, json=payload, timeout=300)
    response.raise_for_status()

    data = response.json()
    content = data["content"][0]["text"]
    return content