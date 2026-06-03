# flake8: noqa: E501
"""
app.py – NeuraFlow AI · Intelligent Multi-LLM Document Agent Platform
Clean default Streamlit UI with intelligent provider routing.
"""

import base64
import hashlib
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from services.agent_executor import AgentExecutor
from services.ai_router import build_providers, get_agent
from services.db_manager import DBManager
from services.memory_manager import MemoryManager
from services.rag_engine import RAGManager
from services.telegram_logger import TelegramLogger
from services.tool_registry import ToolRegistry
from utils.helpers import format_token_usage, task_type_label

load_dotenv(override=True)

# Initialize global services
telegram_logger = TelegramLogger()
rag_manager = RAGManager()
db_manager = DBManager()
memory_manager = MemoryManager()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuraFlow AI",
    page_icon=r"C:\Users\Piyu\Downloads\AI-Doc-Assistant\assets\AI.svg",
    layout="centered",
)


# ── Load Logo ─────────────────────────────────────────────────────────────────
def get_base64_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


logo_b64 = get_base64_image("assets/AI.svg")
logo_img = f'<img src="data:image/svg+xml;base64,{logo_b64}" width="40" />'

# ── Provider Metadata ─────────────────────────────────────────────────────────
PROVIDERS = {
    "Auto Agent": {"icon": "🤖", "model": "Smart Router", "key_env": None},
    "Groq": {"icon": "⚡", "model": "LLaMA 3.1 8B", "key_env": "GROQ_API_KEY"},
    "Gemini": {"icon": "🔵", "model": "Gemini 1.5 Flash", "key_env": "GEMINI_API_KEY"},
    "OpenRouter": {
        "icon": "🌐",
        "model": "LLaMA 3 8B",
        "key_env": "OPENROUTER_API_KEY",
    },
    "Hugging Face": {
        "icon": "🤗",
        "model": "Zephyr 7B",
        "key_env": "HUGGINGFACE_API_KEY",
    },
}

# ── Session State ─────────────────────────────────────────────────────────────
for key, val in {
    "selected_provider": "Auto Agent",
    "last_decision": None,
    "chat_history": [],
    "doc_text": "",
    "file_name": "",
    "last_rag_metrics": {},
    "last_memory_metrics": {},
    "last_search_telemetry": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            {logo_img}
            <h2 style="margin: 0;">NeuraFlow AI</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Intelligent Multi-LLM Document Agent Platform")
    st.divider()

    # Hybrid Approach: Load API keys from st.secrets (Cloud) or .env (Local)
    api_keys: dict = {}
    for name, meta in PROVIDERS.items():
        if meta["key_env"] is None:
            continue

        env_key = meta["key_env"]

        try:
            # Try getting from Streamlit Secrets first
            if env_key in st.secrets:
                api_keys[env_key] = st.secrets[env_key]
            else:
                api_keys[env_key] = os.getenv(env_key, "")
        except Exception:
            # Fallback for local environment if secrets file doesn't exist
            api_keys[env_key] = os.getenv(env_key, "")

    st.markdown("""
## 📝 About

NeuraFlow AI is a production-grade Multi-LLM AI platform that intelligently analyzes documents and routes queries to the most suitable AI model. By leveraging Groq, Gemini, OpenRouter, and Hugging Face, the system delivers fast, accurate, and cost-effective responses through intelligent routing and automatic fallback mechanisms.

### 🚀 Models Integrated

* ⚡ LLaMA 3.1 8B (Groq)
* 🔵 Gemini 1.5 Flash (Google)
* 🌐 LLaMA 3 via OpenRouter
* 🤗 Zephyr 7B (Hugging Face)

### ✨ Key Features

* Multi-LLM Architecture
* Intelligent AI Agent Routing
* Automatic Fallback Handling
* PDF Document Question Answering
* Real-Time Model Selection
* Agent Decision Transparency
* Modern Streamlit UI
* Production-Ready Modular Design

Built to demonstrate modern Generative AI, LLM orchestration, document intelligence, and scalable AI application development.
        """)

    st.divider()
    st.caption("🛡️ Autonomous Fallback & Recovery Engine | By Piyush Ramteke")

# ── Build Providers ───────────────────────────────────────────────────────────
providers = build_providers(api_keys)

# ── Main Page ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
        {logo_img}
        <h1 style="margin: 0;">NeuraFlow AI</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("Upload a PDF and ask questions using intelligent multi-LLM routing.")

# Provider Selector
robot_gif_b64 = get_base64_image("assets/happy-retro-robot.gif")
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
        <img src="data:image/gif;base64,{robot_gif_b64}" width="120" style="border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" />
        <div>
            <h2 style="margin: 0; font-size: 24px; color: #f8fafc;">Piyush Ramteke</h2>
            <p style="margin: 4px 0 0 0; font-size: 15px; color: #94a3b8;">
                Data Scientist & AI Engineer | Building intelligent multi-LLM solutions
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.subheader("Select AI Provider")
selected = st.radio(
    "Provider",
    list(PROVIDERS.keys()),
    index=0,
    horizontal=True,
    label_visibility="collapsed",
    key="selected_provider",
)
mode = "auto" if selected == "Auto Agent" else selected
meta = PROVIDERS[selected]
st.info(f"{meta['icon']} **{selected}** · {meta['model']}")

st.info(f"{meta['icon']} **{selected}** · {meta['model']}")

st.divider()
st.markdown("### 🛠️ Agent Settings")
enable_tools = st.checkbox(
    "☑ Enable Agent Tools (ReAct Mode)",
    value=True,
    help="Allows the AI to use Web Search, Calculator, and Document Search.",
)
show_reasoning = st.checkbox(
    "☑ Show Agent Reasoning",
    value=True,
    help="Streams the Agent's internal Thought and Action process.",
)

st.divider()
st.markdown("### 🔍 Search Settings")
st.radio(
    "Search Provider",
    ["Auto", "Tavily", "DuckDuckGo"],
    index=0,
    key="search_provider",
    help="Auto uses Tavily if API key is available, falling back to DuckDuckGo.",
)

# PDF Upload
st.subheader("📂 Upload Document")
uploaded = st.file_uploader("Upload a PDF", type="pdf")

if not uploaded:
    st.stop()

# Extract text on new upload
if uploaded.name != st.session_state.file_name:
    file_bytes = uploaded.getvalue()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    st.session_state.file_name = uploaded.name
    st.session_state.chat_history = []

    reader = PdfReader(uploaded)
    num_pages = len(reader.pages)

    # Check if already indexed
    if rag_manager.is_indexed(file_hash):
        rag_manager.set_collection(f"doc_{file_hash}")
        text = "".join(p.extract_text() for p in reader.pages if p.extract_text())
        st.session_state.doc_text = text
        st.session_state.index_metrics = {
            "chunks": "Cached",
            "embeddings": "Cached",
            "time": 0.0,
            "pages": num_pages,
            "cache_hit": True,
        }
    else:
        progress_bar = st.progress(0)
        status = st.empty()

        def update_progress(msg, pct):
            status.info(msg)
            progress_bar.progress(pct)

        text = "".join(p.extract_text() for p in reader.pages if p.extract_text())

        metadata = {
            "filename": uploaded.name,
            "pages": num_pages,
            "indexed_at": datetime.now().isoformat(),
            "hash": file_hash,
        }

        metrics = rag_manager.index_document(
            document_text=text,
            doc_hash=file_hash,
            metadata=metadata,
            progress_callback=update_progress,
        )

        st.session_state.doc_text = text
        st.session_state.index_metrics = {
            "chunks": metrics["chunks"],
            "embeddings": metrics["embeddings"],
            "time": metrics["time"],
            "pages": num_pages,
            "cache_hit": False,
        }

        status.empty()
        progress_bar.empty()

        # Log the upload to Telegram and DB
        telegram_logger.log_upload(uploaded.name, uploaded.size, num_pages)
        db_manager.log_document(
            filename=uploaded.name,
            pages=num_pages,
            chunks=metrics["chunks"],
            file_size=uploaded.size,
        )

m = st.session_state.get("index_metrics")
if m:
    cache_badge = "🟢 Cache Hit" if m["cache_hit"] else "🟡 Cache Miss"
    st.success(f"✅ **{uploaded.name}** ready — {m['pages']} pages")

    st.markdown(f"### 📊 Indexing Metrics  `{cache_badge}`")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Pages", m["pages"])
    col2.metric("✂️ Chunks", m["chunks"])
    col3.metric("🧠 Embeddings", m["embeddings"])
    col4.metric(
        "⏱️ Index Time",
        f"{m['time']:.2f}s" if isinstance(m["time"], float) else m["time"],
    )
else:
    st.success(f"✅ **{uploaded.name}** uploaded")

with st.expander("👁️ Preview document text"):
    st.write(st.session_state.doc_text[:2000] + "…")

st.divider()

# Chat history
if st.session_state.chat_history:
    st.subheader("💬 Conversation")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                prov = msg.get("provider", "AI")
                badge = (
                    f"Auto Agent → **{prov}**"
                    if mode == "auto"
                    else f"Powered by **{prov}**"
                )
                st.caption(badge)
                st.write(msg["content"])

st.divider()

# Question form
st.subheader("🚀 Ask the Agent")

with st.form("question_form", clear_on_submit=True):
    question = st.text_input(
        "Question",
        placeholder="Ask anything about the document…",
        label_visibility="collapsed",
    )
    col1, col2, col3 = st.columns([3, 1.5, 1])
    with col1:
        ask = st.form_submit_button(
            "🚀 Ask Agent", type="primary", use_container_width=True
        )
    with col2:
        summarize = st.form_submit_button("📋 Summarise", use_container_width=True)
    with col3:
        clear = st.form_submit_button("🗑️ Clear", use_container_width=True)

if clear:
    st.session_state.chat_history = []
    st.session_state.last_decision = None
    st.rerun()

final_q = None
if ask and question.strip():
    final_q = question.strip()
elif ask:
    st.warning("Please type a question first.")
elif summarize:
    final_q = "Provide a clear, concise summary of this document."

if final_q:
    if not providers:
        st.error("❌ No providers configured. Add at least one API key in the sidebar.")
    else:
        agent = get_agent(providers, mode=mode)
        status_placeholder = st.empty()

        def update_status(msg):
            status_placeholder.info(msg)

        if enable_tools:
            # --- ReAct Agent Mode ---
            with st.spinner("🔍 Loading memory and tools..."):
                mem_ctx, mem_tokens, mem_turns = memory_manager.get_context(
                    st.session_state.chat_history, max_turns=3, max_tokens=1500
                )

                st.session_state.last_memory_metrics = {
                    "hit": mem_turns > 0,
                    "tokens": mem_tokens,
                    "turns": mem_turns,
                }
                # RAG is handled by the Document Search Tool dynamically
                st.session_state.last_rag_metrics = {
                    "chunks": 0,
                    "score": 0.0,
                    "time": 0.0,
                }

            st.session_state.last_search_telemetry = None
            st.session_state.status_callback = update_status

            tool_registry = ToolRegistry(rag_manager)
            executor = AgentExecutor(agent, tool_registry)

            wrapper = executor.run_react_stream(
                user_question=final_q,
                memory_context=mem_ctx,
                status_callback=update_status,
                show_reasoning=show_reasoning,
            )

            st.write_stream(wrapper)
            status_placeholder.empty()

            decision = executor.last_decision
            st.session_state.last_decision = decision

        else:
            # --- Standard RAG Mode ---
            with st.spinner("🔍 Retrieving semantic context and memory…"):
                context_str, sim_score, ret_time, n_chunks = (
                    rag_manager.retrieve_context(final_q)
                )
                mem_ctx, mem_tokens, mem_turns = memory_manager.get_context(
                    st.session_state.chat_history, max_turns=3, max_tokens=1500
                )

                st.session_state.last_rag_metrics = {
                    "chunks": n_chunks,
                    "score": sim_score,
                    "time": ret_time,
                }
                st.session_state.last_memory_metrics = {
                    "hit": mem_turns > 0,
                    "tokens": mem_tokens,
                    "turns": mem_turns,
                }

            prompt = (
                f"You are an AI assistant. Answer the user's question using the Document Context below.\n\n"
                f"Document Context:\n{context_str}\n\n"
            )
            if mem_ctx:
                prompt += f"Recent Conversation History:\n{mem_ctx}\n\n"

            prompt += f"Current Question:\n{final_q}"

            st.session_state.last_search_telemetry = None
            st.session_state.status_callback = update_status

            wrapper = agent.run_stream(prompt, status_callback=update_status)

            st.write_stream(wrapper)
            status_placeholder.empty()

            decision = wrapper.final_decision
            st.session_state.last_decision = decision

        if decision.response.success:
            tokens = (
                decision.response.token_usage.get("output_tokens", 0)
                if decision.response.token_usage
                else 0
            )
            if decision.response.response_time > 0 and tokens > 0:
                tokens_per_sec = tokens / decision.response.response_time
            else:
                tokens_per_sec = 0.0

            rag_metrics = st.session_state.get("last_rag_metrics", {})
            mem_metrics = st.session_state.get("last_memory_metrics", {})
            db_manager.log_query(
                provider=decision.response.provider,
                latency=decision.response.response_time,
                rag_time=rag_metrics.get("time", 0.0),
                similarity_score=rag_metrics.get("score", 0.0),
                fallback_used=decision.fallback_used,
                memory_hit=mem_metrics.get("hit", False),
                memory_tokens=mem_metrics.get("tokens", 0),
                chat_turns=mem_metrics.get("turns", 0),
                first_token_time=decision.response.first_token_time,
                tokens_per_sec=tokens_per_sec,
            )
            db_manager.log_provider(
                provider_name=decision.response.provider,
                success=True,
                error_msg="",
                response_time=decision.response.response_time,
            )
            telegram_logger.log_query(
                document_name=st.session_state.file_name,
                question=final_q,
                provider=decision.response.provider,
                response_time=decision.response.response_time,
                fallback_used=decision.fallback_used,
            )
            st.session_state.chat_history.append({"role": "user", "content": final_q})
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": decision.response.text,
                    "provider": decision.response.provider,
                }
            )
            st.rerun()
        else:
            err = decision.response.error or ""
            db_manager.log_provider(
                provider_name=decision.selected_provider,
                success=False,
                error_msg=err,
                response_time=decision.response.response_time,
            )
            telegram_logger.log_error(
                provider=decision.selected_provider, error_msg=err
            )
            if "429" in err or "quota" in err.lower():
                st.error(
                    "⚠️ **Quota Exceeded (429)** — Free tier limit reached.\n\n"
                    "- Wait a few minutes and retry\n"
                    "- Try a different provider\n"
                    "- Enable billing on your API account"
                )
            else:
                st.error(f"❌ {decision.response.text}")

# Agent Decision Panel
if st.session_state.last_decision:
    d = st.session_state.last_decision
    r = d.response
    with st.expander("🧠 Agent Decision Panel"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Task Type", task_type_label(d.task_type))
        col2.metric("Provider", r.provider)
        col3.metric("Response Time", f"{r.response_time}s")

        col4, col5, col6 = st.columns(3)
        col4.metric("Intended", d.selected_provider)
        col5.metric("Tokens", format_token_usage(r.token_usage))
        col6.metric("Fallback Used", "Yes ⚠️" if d.fallback_used else "No ✅")

        st.info(f"💡 **Routing reason:** {d.reason}")

        rag = st.session_state.get("last_rag_metrics", {})
        if rag:
            st.divider()
            st.subheader("📚 Retrieval-Augmented Generation (RAG)")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Retrieved Chunks", rag.get("chunks", 0))
            c2.metric("Similarity Score", f"{rag.get('score', 0):.2f}")
            c3.metric("Retrieval Time", f"{rag.get('time', 0):.2f}s")
            c4.metric("RAG Enabled", "Yes ✅")

        search_tel = st.session_state.get("last_search_telemetry")
        if search_tel:
            st.divider()
            st.subheader("🔍 Web Search Performance")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Search Provider", search_tel.get("provider_used"))
            s2.metric("Results Retrieved", search_tel.get("results_count", 0))
            s3.metric("Search Time", f"{search_tel.get('search_time', 0.0):.2f}s")
            s4.metric(
                "Fallback Used",
                "Yes ⚠️" if search_tel.get("fallback_used") else "No ✅",
            )

        if d.fallback_log:
            st.write("**Fallback Log:**")
            for entry in d.fallback_log:
                st.caption(entry)
