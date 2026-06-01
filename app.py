"""
app.py – Multi-LLM AI Agent Platform
Premium glassmorphism Streamlit UI with intelligent provider routing.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from services.ai_router import build_providers, get_agent, get_all_provider_meta
from utils.helpers import format_token_usage, status_badge, task_type_label

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Doc Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS – Premium Dark Glassmorphism Theme ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

/* Dark background */
.stApp { background: linear-gradient(135deg,#07070f 0%,#0d0d1a 60%,#070712 100%) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(13,13,26,0.95) !important;
    border-right: 1px solid rgba(168,85,247,0.2) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label { color: #c4b5fd !important; font-size: 13px !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Headings */
h1 { background: linear-gradient(90deg,#a855f7,#3b82f6); -webkit-background-clip: text;
     -webkit-text-fill-color: transparent; font-weight: 800 !important; letter-spacing:-1px; }
h2,h3 { color: #e2e8f0 !important; font-weight: 600 !important; }

/* Glass card */
.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    margin-bottom: 16px;
}

/* Provider badge */
.provider-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 7px 16px; border-radius: 24px; font-size: 13px;
    font-weight: 600; letter-spacing: 0.3px; margin-bottom: 12px;
}

/* Decision panel */
.decision-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
.decision-chip {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px; padding: 8px 14px; font-size: 12px; color: #cbd5e1;
}
.decision-chip strong { color: #e2e8f0; display: block; margin-bottom: 2px; }

/* Fallback log */
.fallback-item { font-size: 12px; color: #94a3b8; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(168,85,247,0.3) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 2px rgba(168,85,247,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg,#7c3aed,#3b82f6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    padding: 10px 24px !important; transition: all .2s ease !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* Radio – provider selector */
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; padding: 8px 16px !important;
    color: #cbd5e1 !important; cursor: pointer !important;
    transition: all .2s ease !important;
}
div[role="radiogroup"] label:hover { border-color: #a855f7 !important; color:#e2e8f0 !important; }

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(168,85,247,0.4) !important;
    border-radius: 14px !important;
}

/* Expander */
details { background: rgba(255,255,255,0.03) !important; border-radius: 12px !important;
          border: 1px solid rgba(255,255,255,0.08) !important; }
summary { color: #c4b5fd !important; font-weight: 500 !important; }

/* Alerts */
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State Defaults ────────────────────────────────────────────────────
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "Auto Agent"
if "last_decision" not in st.session_state:
    st.session_state.last_decision = None

# ── Provider Metadata ─────────────────────────────────────────────────────────
PROVIDER_META = {
    "Gemini":       {"icon": "🔵", "color": "#3b82f6", "key_env": "GEMINI_API_KEY"},
    "Groq":         {"icon": "⚡", "color": "#f59e0b", "key_env": "GROQ_API_KEY"},
    "OpenRouter":   {"icon": "🌐", "color": "#10b981", "key_env": "OPENROUTER_API_KEY"},
    "Hugging Face": {"icon": "🤗", "color": "#f97316", "key_env": "HUGGINGFACE_API_KEY"},
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Multi-LLM Agent")
    st.markdown("*AI Document Platform*")
    st.divider()

    # API Keys section
    st.markdown("### 🔑 API Keys")
    api_keys = {}
    for name, meta in PROVIDER_META.items():
        env_val = os.getenv(meta["key_env"], "")
        user_val = st.text_input(
            f"{meta['icon']} {name}",
            value=env_val,
            type="password",
            key=f"key_{name}",
            placeholder=f"Enter {name} API key…",
        )
        api_keys[meta["key_env"]] = user_val or env_val

    st.divider()

    # Provider status indicators
    st.markdown("### 📡 Provider Status")
    for name, meta in PROVIDER_META.items():
        key = api_keys.get(meta["key_env"], "")
        status = "🟢 Online" if key else "⚫ Offline"
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06)">'
            f'<span style="color:#e2e8f0">{meta["icon"]} {name}</span>'
            f'<span style="font-size:12px;color:#94a3b8">{status}</span></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        '<p style="font-size:11px;color:#475569;text-align:center">'
        'Fallback chain: Groq → Gemini → OpenRouter → HF</p>',
        unsafe_allow_html=True,
    )

# ── Build providers & agent ───────────────────────────────────────────────────
providers = build_providers(api_keys)

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("# 📄 AI Document Agent")
st.markdown(
    '<p style="color:#94a3b8;margin-top:-8px;margin-bottom:24px">'
    "Upload a PDF and ask questions — powered by intelligent multi-LLM routing.</p>",
    unsafe_allow_html=True,
)

# Provider Selector
st.markdown("### 🎛️ Select AI Provider")
mode_options = ["Auto Agent (Recommended)", "Groq ⚡", "Gemini 🔵", "OpenRouter 🌐", "Hugging Face 🤗"]
mode_labels  = ["auto", "Groq", "Gemini", "OpenRouter", "Hugging Face"]

selected_label = st.radio(
    "Provider",
    mode_options,
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)
selected_mode = mode_labels[mode_options.index(selected_label)]

# If a specific provider is chosen but not configured, warn
if selected_mode != "auto" and selected_mode not in providers:
    st.warning(
        f"⚠️ **{selected_mode}** is not configured. Please add its API key in the sidebar."
    )

st.divider()

# PDF Upload
st.markdown("### 📂 Upload Document")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf", label_visibility="collapsed")

if not uploaded_file:
    st.markdown(
        '<div class="glass" style="text-align:center;color:#475569;padding:40px">'
        "📄 Drop a PDF above to get started</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# Extract text
st.success("✅ Document uploaded successfully")
reader = PdfReader(uploaded_file)
doc_text = ""
for page in reader.pages:
    t = page.extract_text()
    if t:
        doc_text += t
doc_text = doc_text[:15000]

with st.expander("👁️ Preview Document Text"):
    st.write(doc_text[:2000] + ("…" if len(doc_text) > 2000 else ""))

st.divider()

# ── Question Interface ────────────────────────────────────────────────────────
st.markdown("### 💬 Ask the Agent")

col1, col2 = st.columns([4, 1])
with col1:
    user_question = st.text_input(
        "Question",
        placeholder="Ask anything about the document…",
        label_visibility="collapsed",
    )
with col2:
    summarize = st.button("📋 Summarise", use_container_width=True)

ask = st.button("🚀 Ask AI Agent", use_container_width=False)

# Determine final question
question = None
if summarize:
    question = "Provide a clear, concise summary of this document."
elif ask and user_question:
    question = user_question
elif ask and not user_question:
    st.warning("Please type a question first.")

# ── Agent Execution ───────────────────────────────────────────────────────────
if question:
    if not providers:
        st.error("❌ No providers configured. Please add at least one API key in the sidebar.")
        st.stop()

    prompt = f"""Answer the question using the document below.

Document:
{doc_text}

Question:
{question}
"""
    agent = get_agent(providers, mode=selected_mode)

    with st.spinner("🤖 Agent is routing and generating your response…"):
        decision = agent.run(prompt)

    st.session_state.last_decision = decision

# ── Display Decision + Response ───────────────────────────────────────────────
if st.session_state.last_decision:
    d = st.session_state.last_decision
    r = d.response

    # ── Agent Decision Panel
    st.markdown("### 🧠 Agent Decision Panel")
    meta = PROVIDER_META.get(r.provider, {"icon": "🤖", "color": "#888"})
    badge_color = meta["color"]
    badge_icon  = meta["icon"]

    st.markdown(
        f'<div class="glass">'
        f'<div class="decision-row">'
        f'<div class="decision-chip"><strong>Task Type</strong>{task_type_label(d.task_type)}</div>'
        f'<div class="decision-chip"><strong>Intended Provider</strong>{d.selected_provider}</div>'
        f'<div class="decision-chip"><strong>Actual Provider</strong>{badge_icon} {r.provider}</div>'
        f'<div class="decision-chip"><strong>Response Time</strong>⏱ {r.response_time}s</div>'
        f'<div class="decision-chip"><strong>Token Usage</strong>{format_token_usage(r.token_usage)}</div>'
        f'<div class="decision-chip"><strong>Fallback Used</strong>{"⚠️ Yes" if d.fallback_used else "✅ No"}</div>'
        f'</div>'
        f'<p style="margin-top:12px;font-size:13px;color:#94a3b8">💡 <strong style="color:#c4b5fd">Why:</strong> {d.reason}</p>'
        + (
            f'<details style="margin-top:8px"><summary style="font-size:12px;color:#64748b;cursor:pointer">🔁 Fallback Log</summary>'
            + "".join(f'<div class="fallback-item">{entry}</div>' for entry in d.fallback_log)
            + "</details>"
            if d.fallback_log else ""
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    # ── Response
    st.markdown("### 💬 Response")
    if r.success:
        # Auto-agent badge vs manual badge
        if selected_mode == "auto":
            badge_text = f"Auto Agent Selected: {r.provider}"
        else:
            badge_text = f"Powered by {r.provider}"

        st.markdown(
            f'<div class="provider-badge" style="background:{badge_color}22;'
            f'border:1px solid {badge_color}55;color:{badge_color}">'
            f'{badge_icon} {badge_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="glass">{r.text}</div>',
            unsafe_allow_html=True,
        )
    else:
        err = r.error or ""
        if "429" in err or "quota" in err.lower():
            st.error(
                "⚠️ **Quota Exceeded (429):** Free tier limit reached.\n\n"
                "- Wait a few minutes and retry\n"
                "- Enable billing or use a different API key"
            )
        else:
            st.error(f"❌ {r.text}")