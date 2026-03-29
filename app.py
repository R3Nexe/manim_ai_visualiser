"""
app.py — Streamlit UI for Manim AI Visualiser
"""
import os
import sys
import threading
from pathlib import Path
from streamlit_ace import st_ace
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Manim AI Visualiser",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
defaults = {
    "messages": [],           # [{role, content}]
    "video_path": None,       # str path to latest .mp4
    "current_code": "",       # generated Manim script content
    "script_path": None,      # path to the script file on disk
    "session_dir": None,      # session output dir
    "pipeline_running": False,
    "pipeline_error": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Sidebar — Settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Settings")

    provider = st.selectbox(
        "Provider",
        ["local", "openai", "anthropic", "gemini"],
        index=0,
        help="LLM provider to use for generation",
    )

    model_defaults = {
        "local":     "",
        "openai":    "gpt-4o",
        "anthropic": "claude-sonnet-4-6",
        "gemini":    "gemini-2.5-pro-preview",
    }
    model = st.text_input(
        "Model",
        value=model_defaults.get(provider, ""),
        placeholder="Leave blank for provider default",
    )

    st.divider()

    if provider == "openai":
        openai_key = st.text_input("OpenAI API Key", type="password",
                                   value=os.getenv("OPENAI_API_KEY", ""))
    elif provider == "anthropic":
        anthropic_key = st.text_input("Anthropic API Key", type="password",
                                      value=os.getenv("ANTHROPIC_API_KEY", ""))
    elif provider == "gemini":
        gemini_key = st.text_input("Gemini API Key", type="password",
                                   value=os.getenv("GEMINI_API_KEY", ""))
    elif provider == "local":
        local_url = st.text_input(
            "LM Studio / Ollama URL",
            value=os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:1234/v1/chat/completions"),
        )

    st.divider()

    quality = st.radio(
        "Render Quality",
        options=["Low (fast)", "Medium", "High"],
        index=0,
        help="Low =  (480p), Medium =  (720p), High =  (1080p)",
    )
    quality_flag = {
        "Low (fast)": "-ql",
        "Medium":     "-qm",
        "High":       "-qh",
    }[quality]





# ---------------------------------------------------------------------------
# Helper — push API keys into env before running pipeline
# ---------------------------------------------------------------------------
def _apply_env_settings():
    os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model
    elif "LLM_MODEL" in os.environ:
        del os.environ["LLM_MODEL"]

    if provider == "openai" and openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    elif provider == "anthropic" and anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    elif provider == "gemini" and gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    elif provider == "local" and local_url:
        os.environ["LOCAL_LLM_URL"] = local_url


# ---------------------------------------------------------------------------
# Helper — run pipeline (blocking, called inside st.spinner)
# ---------------------------------------------------------------------------
def _run_pipeline(prompt: str) -> tuple[str, str, str]:
    """
    Returns (video_path, script_content, script_path_str).
    Raises on failure.
    """
    _apply_env_settings()
    from pipeline.executor import run, OUTPUTS, RAW_DIR

    video_path = run(prompt, quality_flag=quality_flag, provider=provider,
                     model=model or None)
    if not video_path:
        raise RuntimeError("Pipeline returned no video. Check logs for details.")

    # Locate the script that was used: outputs/<session_id>/animation.py
    # The session id is embedded in the video filename: final_<session_id>.mp4
    video_stem = Path(video_path).stem          # e.g. final_1711700000_abc123
    session_id = video_stem.replace("final_", "", 1)
    session_dir = OUTPUTS / session_id
    script_path = session_dir / "animation.py"

    code = script_path.read_text() if script_path.exists() else ""
    return video_path, code, str(script_path)


# ---------------------------------------------------------------------------
# Helper — re-render existing (possibly edited) script
# ---------------------------------------------------------------------------
def _rerender(script_path: str, code: str) -> tuple[str, str]:
    """Write edited code to disk and re-render. Returns (new_video_path, stderr)."""
    _apply_env_settings()
    from pipeline.executor import _render, VIDEO_DIR
    import time, uuid

    p = Path(script_path)
    p.write_text(code)

    session_dir = p.parent
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    video_path, stderr = _render(p, session_dir, quality_flag)
    if video_path is None:
        return "", stderr

    final_path = VIDEO_DIR / f"final_rerender_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
    video_path.rename(final_path)
    return str(final_path), ""


# ---------------------------------------------------------------------------
# Layout — video panel (70%) + chat panel (30%), or full-width chat
# ---------------------------------------------------------------------------
has_video = bool(st.session_state.video_path)

if has_video:
    col_main, col_chat = st.columns([8, 2], gap="xsmall")

else:
    col_main = None
    col_chat = st.container(height="content")

# ── Video / Code panel ──────────────────────────────────────────────────────
if has_video and col_main is not None:
    with col_main:
        tab_video, tab_code = st.tabs(["Video", "Script Editor"])

        with tab_video:
            st.video(st.session_state.video_path)
            st.caption("## Video Generated",text_alignment="center")

        with tab_code:
            edited_code=st_ace(value=st.session_state.current_code,language="python",theme="tomorrow_night")

            rerender_col, status_col = st.columns([2, 5])
            with rerender_col:
                rerender_btn = st.button("Re-render", type="primary",
                                         use_container_width=True)
            with status_col:
                rerender_status = st.empty()

            if rerender_btn:
                if not st.session_state.script_path:
                    rerender_status.error("No script path found.")
                else:
                    with st.spinner("Re-rendering..."):
                        new_path, stderr = _rerender(
                            st.session_state.script_path, edited_code
                        )
                    if new_path:
                        st.session_state.video_path = new_path
                        st.session_state.current_code = edited_code
                        rerender_status.success("Re-render complete!")
                        st.rerun()
                    else:
                        rerender_status.error("Render failed.")
                        with st.expander("Stderr"):
                            st.code(stderr)

# ── Chat panel ──────────────────────────────────────────────────────────────
with col_chat:
    st.subheader("Chat" if not has_video else "Chat")

    # Render chat history
    chat_container = st.container(height="stretch" if has_video else 560)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if st.session_state.pipeline_error:
            with st.chat_message("assistant"):
                st.error(st.session_state.pipeline_error)

    # Chat input
    prompt_input = st.chat_input("Describe a concept to visualise…",
                                 disabled=st.session_state.pipeline_running)

    if prompt_input:
        st.session_state.pipeline_error = None
        st.session_state.messages.append({"role": "user", "content": prompt_input})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt_input)

        with chat_container:
            with st.chat_message("assistant"):
                status_placeholder = st.empty()
                status_placeholder.markdown("Generating animation…")

        st.session_state.pipeline_running = True
        try:
            with st.spinner("Generating Manim Script (this may take a few minutes)…"):
                video_path, code, script_path = _run_pipeline(prompt_input)

            st.session_state.video_path   = video_path
            st.session_state.current_code = code
            st.session_state.script_path  = script_path

            reply = f"Done! Rendered to `{Path(video_path).name}`."
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as exc:
            err = str(exc)
            st.session_state.pipeline_error = err
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Pipeline failed: {err}"}
            )
        finally:
            st.session_state.pipeline_running = False

        st.rerun()
