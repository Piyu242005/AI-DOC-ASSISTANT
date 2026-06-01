# flake8: noqa: E501
"""
app.py – AI Document Assistant · Multi-LLM Platform
Clean default Streamlit UI with intelligent provider routing.
"""

import base64
import os

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from services.ai_router import build_providers, get_agent
from utils.helpers import format_token_usage, task_type_label

load_dotenv(override=True)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Document Assistant",
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
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            {logo_img}
            <h2 style="margin: 0;">AI Doc Assistant</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Multi-LLM Agent Platform")
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

    st.markdown(
        """
## 📝 About

AI Document Assistant is a production-grade Multi-LLM AI platform that intelligently analyzes documents and routes queries to the most suitable AI model. By leveraging Groq, Gemini, OpenRouter, and Hugging Face, the system delivers fast, accurate, and cost-effective responses through intelligent routing and automatic fallback mechanisms.

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
        """
    )

    st.divider()
    st.caption("Fallback chain: Groq → Gemini → OpenRouter → HF")

# ── Build Providers ───────────────────────────────────────────────────────────
providers = build_providers(api_keys)

# ── Main Page ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
        {logo_img}
        <h1 style="margin: 0;">AI Document Assistant</h1>
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

st.divider()

# PDF Upload
st.subheader("📂 Upload Document")
uploaded = st.file_uploader("Upload a PDF", type="pdf")

if not uploaded:
    st.stop()

# Extract text on new upload
if uploaded.name != st.session_state.file_name:
    with st.spinner("Reading document…"):
        reader = PdfReader(uploaded)
        text = "".join(p.extract_text() for p in reader.pages if p.extract_text())[
            :15000
        ]
    st.session_state.doc_text = text
    st.session_state.file_name = uploaded.name
    st.session_state.chat_history = []

st.success(f"✅ **{uploaded.name}** uploaded — {len(PdfReader(uploaded).pages)} pages")

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
        prompt = (
            f"Answer the question using the document below.\n\n"
            f"Document:\n{st.session_state.doc_text}\n\n"
            f"Question:\n{final_q}"
        )
        agent = get_agent(providers, mode=mode)

        with st.spinner("🤖 Agent is routing and generating response…"):
            decision = agent.run(prompt)

        st.session_state.last_decision = decision

        if decision.response.success:
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

        if d.fallback_log:
            st.write("**Fallback Log:**")
            for entry in d.fallback_log:
                st.caption(entry)
