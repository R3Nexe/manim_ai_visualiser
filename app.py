"""
app.py — Streamlit UI for Manim AI Visualiser
"""
import os
import sys
import threading
import datetime
from pathlib import Path
from streamlit_ace import st_ace
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Manim AI Visualiser",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main Background Gradient (Dark Navy to Charcoal) */
    .stApp {
        background: linear-gradient(135deg, #0b132b 0%, #36454F 100%) !important;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(11, 19, 43, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Global Text Color Adjustment */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label {
        color: #f0f4f8 !important;
    }

    /* Divider Lines */
    hr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Chat Messages Glassmorphism */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
    "pipeline_logs": "",      # captured stdout from last pipeline run
    "search_history": [],     # list of dicts: [{"date": str, "prompt": str}]
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Sidebar — Settings & History
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

    st.divider()

    # --- History Option ---
    st.subheader("Search History")
    if not st.session_state.search_history:
        st.markdown("*(No Search History)*")
    else:
        for item in reversed(st.session_state.search_history):  # Show newest first
            st.caption(f"**{item['date']}**")
            st.text(f"{item['prompt'][:50]}{'...' if len(item['prompt']) > 50 else ''}")

        if st.button("Clear History", use_container_width=True):
            st.session_state.search_history = []
            st.rerun()

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


# Helper — run pipeline (blocking, called inside st.spinner)
# ---------------------------------------------------------------------------
def _run_pipeline(prompt: str) -> tuple[str, str, str]:
    """
    Returns (video_path, script_content, script_path_str).
    Captures all pipeline stdout into st.session_state.pipeline_logs.
    Raises on failure.
    """
    import io
    from contextlib import redirect_stdout, redirect_stderr

    _apply_env_settings()
    from pipeline.executor import run, OUTPUTS, RAW_DIR

    log_buffer = io.StringIO()
    try:
        with redirect_stdout(log_buffer), redirect_stderr(log_buffer):
            video_path = run(prompt, quality_flag=quality_flag, provider=provider,
                             model=model or None)
    except Exception as exc:
        st.session_state.pipeline_logs = log_buffer.getvalue()
        raise RuntimeError(str(exc))
    finally:
        # Always persist whatever was captured so far
        st.session_state.pipeline_logs = log_buffer.getvalue()

    if not video_path:
        raise RuntimeError("Pipeline returned no video.")

    video_stem = Path(video_path).stem
    session_id = video_stem.replace("final_", "", 1)
    session_dir = OUTPUTS / session_id
    script_path = session_dir / "animation.py"

    code = script_path.read_text() if script_path.exists() else ""
    return video_path, code, str(script_path)

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

# Layout — video panel (70%) + chat panel (30%), or full-width chat
# ---------------------------------------------------------------------------
has_video = bool(st.session_state.video_path)

if has_video:
    col_main, col_chat = st.columns([8, 2], gap="small")
else:
    col_main = None
    col_chat = st.container(height="content")

# ── Video / Code panel ──────────────────────────────────────────────────────
if has_video and col_main is not None:
    with col_main:
        tab_video, tab_code = st.tabs(["Video", "Script Editor"])

        with tab_video:
            st.video(st.session_state.video_path)
            st.caption("## Video Generated", text_alignment="center")

            # --- Download Video Option ---
            try:
                with open(st.session_state.video_path, "rb") as vid_file:
                    st.download_button(
                        label="⬇️ Download Video",
                        data=vid_file.read(),
                        file_name=Path(st.session_state.video_path).name,
                        mime="video/mp4",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error loading video for download: {e}")

        with tab_code:
            edited_code = st_ace(value=st.session_state.current_code, language="python", theme="tomorrow_night")

            rerender_col, status_col = st.columns([2, 5])
            with rerender_col:
                rerender_btn = st.button("Re-render", type="primary", use_container_width=True)
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
                if st.session_state.pipeline_logs:
                    with st.expander("Pipeline logs"):
                        st.code(st.session_state.pipeline_logs, language="text")

    # Chat input
    prompt_input = st.chat_input("Describe a concept to visualise…",
                                 disabled=st.session_state.pipeline_running)

    if prompt_input:
        # Update search history with timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        st.session_state.search_history.append({"date": current_time, "prompt": prompt_input})

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