# flake8: noqa: E501
"""
styles.py – Complete Design System · NeuraFlow AI
"""


def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
.stApp { background: #080D1A !important; color: #E2E8F0 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 4rem !important; max-width: 1400px !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0C1222 !important;
    border-right: 1px solid rgba(139,92,246,0.15) !important;
    width: 272px !important;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1.1rem !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important; color: #CBD5E1 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.12) !important;
}
section[data-testid="stSidebar"] label { color: #64748B !important; font-size: 11px !important; font-weight: 600 !important; letter-spacing: 0.8px !important; text-transform: uppercase !important; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, rgba(139,92,246,0.12) 0%, rgba(59,130,246,0.08) 100%);
    border-bottom: 1px solid rgba(139,92,246,0.15);
    padding: 48px 40px 40px; margin: 0 -2rem 32px; text-align: center;
}
.hero h1 {
    font-size: 46px !important; font-weight: 800 !important; letter-spacing: -1.5px !important;
    background: linear-gradient(135deg,#A78BFA 0%,#818CF8 50%,#60A5FA 100%);
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    margin-bottom: 12px !important;
}
.hero p { font-size: 17px !important; color: #64748B !important; max-width: 480px; margin: 0 auto 28px !important; }

/* ── Stats bar ── */
.stats-bar { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
.stat-chip {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 7px 16px; font-size: 13px; color: #94A3B8; font-weight: 500;
}
.stat-chip span { color: #A78BFA; font-weight: 700; }

/* ── Two-col panel ── */
.left-panel {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 20px; height: fit-content;
}
.right-panel {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 20px; min-height: 500px;
}

/* ── Provider Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important; padding: 4px !important; gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #475569 !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 13px !important; padding: 8px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,rgba(139,92,246,0.25),rgba(59,130,246,0.2)) !important;
    color: #A78BFA !important; font-weight: 600 !important;
}

/* ── Upload Zone ── */
[data-testid="stFileUploadDropzone"] {
    background: rgba(139,92,246,0.03) !important;
    border: 2px dashed rgba(139,92,246,0.3) !important;
    border-radius: 14px !important;
    transition: all 0.25s ease !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    background: rgba(139,92,246,0.07) !important;
    border-color: rgba(139,92,246,0.55) !important;
}

/* ── File card ── */
.file-card {
    background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.22);
    border-radius: 12px; padding: 14px 16px;
    display: flex; align-items: center; gap: 12px; margin-top: 10px;
}
.file-name { font-size: 13px; font-weight: 600; color: #E2E8F0; }
.file-meta { font-size: 11px; color: #64748B; margin-top: 2px; }

/* ── Suggestion pills ── */
.suggestion-pill {
    display: inline-block; background: rgba(139,92,246,0.08);
    border: 1px solid rgba(139,92,246,0.25); border-radius: 20px;
    padding: 6px 14px; font-size: 12px; color: #A78BFA;
    cursor: pointer; margin: 4px 2px; transition: all 0.2s ease;
}
.suggestion-pill:hover { background: rgba(139,92,246,0.18); }

/* ── Chat bubbles ── */
.chat-user { display: flex; justify-content: flex-end; margin: 12px 0; }
.bubble-user {
    background: linear-gradient(135deg,#7C3AED,#2563EB);
    color: white; border-radius: 18px 18px 4px 18px;
    padding: 11px 16px; max-width: 78%; font-size: 14px; line-height: 1.6;
}
.chat-ai { display: flex; gap: 10px; margin: 12px 0; align-items: flex-start; }
.ai-avatar {
    width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
    background: linear-gradient(135deg,#8B5CF6,#3B82F6);
    display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.bubble-ai {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 16px 16px 16px; padding: 14px 16px;
    max-width: 85%; font-size: 14px; line-height: 1.75; color: #CBD5E1;
}
.bubble-ai pre { background: rgba(0,0,0,0.3) !important; border-radius: 8px !important; padding: 12px !important; font-size: 12px !important; }

/* ── Provider badge ── */
.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 16px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.4px;
    margin-bottom: 10px; text-transform: uppercase;
}

/* ── Chat action buttons ── */
.chat-actions { display: flex; gap: 8px; margin-top: 8px; margin-left: 44px; }
.action-btn {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px; padding: 4px 10px; font-size: 11px; color: #475569;
    cursor: pointer; transition: all 0.15s ease;
}
.action-btn:hover { background: rgba(255,255,255,0.08); color: #94A3B8; }

/* ── Input & Textarea ── */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important; color: #E2E8F0 !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 13px !important; transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#7C3AED,#2563EB) !important;
    border: none !important; color: white !important; padding: 10px 20px !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(124,58,237,0.35) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important; color: #94A3B8 !important;
}
.stButton > button[kind="secondary"]:hover { background: rgba(255,255,255,0.09) !important; color: #E2E8F0 !important; }

/* ── Decision Panel ── */
.dp-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(120px,1fr)); gap: 10px; margin: 14px 0; }
.dp-chip { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 10px 12px; }
.dp-chip .lbl { font-size: 10px; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
.dp-chip .val { font-size: 13px; color: #CBD5E1; font-weight: 600; }

/* ── Status dots ── */
.status-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.status-row:last-child { border-bottom: none; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; margin-right: 5px; }
.dot-on  { background: #10B981; box-shadow: 0 0 5px #10B981; }
.dot-off { background: #374151; }

/* ── Misc ── */
hr { border-color: rgba(255,255,255,0.05) !important; margin: 16px 0 !important; }
.section-label { font-size: 11px; font-weight: 700; color: #374151; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 10px; }
.stAlert { border-radius: 10px !important; }
.stSuccess { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.25) !important; }
.stWarning { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.25) !important; }
.stError   { background: rgba(239,68,68,0.08) !important; border: 1px solid rgba(239,68,68,0.25) !important; }
details { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 10px !important; }
summary { color: #64748B !important; font-size: 13px !important; font-weight: 500 !important; padding: 10px 14px !important; cursor: pointer !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.25); border-radius: 3px; }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.animate { animation: fadeUp 0.3s ease forwards; }

/* ── Empty state ── */
.empty-state { text-align: center; padding: 60px 24px; }
.empty-state .icon { font-size: 52px; margin-bottom: 16px; }
.empty-state h3 { color: #CBD5E1 !important; font-size: 18px !important; margin-bottom: 8px !important; }
.empty-state p { color: #374151 !important; font-size: 14px !important; }

/* ── Export btn ── */
.stDownloadButton > button {
    background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.3) !important;
    color: #34D399 !important; border-radius: 8px !important; font-size: 12px !important;
}
</style>
"""
