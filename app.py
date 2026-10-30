"""
HR Atlas · Streamlit UI
Professional Hybrid RAG policy assistant — redesigned UI.
"""

import uuid

import streamlit as st

from hr_assistant import config
from hr_assistant.logging_config import configure_logging
from hr_assistant.pipeline import (
    INPUT_BLOCKED_MESSAGE,
    OUTPUT_BLOCKED_MESSAGE,
    ask,
    build_hr_assistant,
)
from hr_assistant.tracing import check_langsmith_tracing, enable_tracing

configure_logging()
enable_tracing()

# ──────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Atlas · Policy Assistant",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────
EXAMPLE_QUESTIONS = [
    "How many days of annual leave do I get?",
    "How do I request work from home?",
    "What is the notice period when I resign?",
    "How are travel expenses reimbursed?",
    "What are the rules during probation?",
    "What public holidays does the company observe?",
]

_VERSION = "v1.0.0"

# ──────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────
_APP_CSS = """
<style>
/* ── Google Font ── */
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");

html, body, [class*="st-"], .stMarkdown, .stChatMessage, p, h1, h2, h3, h4 {
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}

/* ── App background ── */
.stApp {
  background:
    radial-gradient(ellipse 1100px 400px at 4% -5%,  rgba(20, 96, 90, 0.07),  transparent 55%),
    radial-gradient(ellipse  900px 360px at 98%  0%, rgba(15, 39, 68, 0.055), transparent 50%),
    #F2F5F9;
}

/* ── Hide Streamlit chrome ── */
[data-testid="stToolbar"]     { display: none !important; }
[data-testid="stDecoration"]  { display: none !important; }
footer                        { visibility: hidden; height: 0; }
#MainMenu                     { display: none; }

/* ── Frosted top bar ── */
[data-testid="stHeader"] {
  background: rgba(242, 245, 249, 0.82);
  backdrop-filter: blur(10px);
}

/* ── Main content width ── */
.block-container {
  max-width: 940px;
  padding-top: 1rem;
  padding-bottom: 7rem;   /* room for sticky chat input */
}

/* ══════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(175deg, #0C1F35 0%, #112D48 55%, #0D2340 100%);
  border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #DDE6F0 !important; }
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small    { color: #8FA5BB !important; }
[data-testid="stSidebar"] a        { color: #5BC4BD !important; }

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.13);
  background: rgba(255,255,255,0.055);
  color: #EEF3F8 !important;
  font-weight: 600;
  font-size: 0.87rem;
  transition: background 0.18s, border-color 0.18s;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(26,154,148,0.3);
  border-color: rgba(26,154,148,0.65);
}

/* Sidebar dividers */
[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.09);
  margin: 0.75rem 0;
}

/* ── Brand mark (sidebar logo) ── */
.brand-mark {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin: 0.1rem 0 1rem;
}
.brand-mark .mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(145deg, #19857F, #28A89F);
  display: grid;
  place-items: center;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #fff !important;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
  flex-shrink: 0;
}
.brand-mark h1 {
  font-size: 1.05rem;
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: #EEF3F8 !important;
}
.brand-mark p {
  margin: 0;
  font-size: 0.76rem;
  color: #8FA5BB !important;
}

/* ── Policy topic chips ── */
.topic-wrap { display: flex; flex-wrap: wrap; gap: 0.38rem; }
.topic {
  font-size: 0.71rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 0.25rem 0.52rem;
  border-radius: 7px;
  background: rgba(255,255,255,0.065);
  border: 1px solid rgba(255,255,255,0.095);
  color: #C4D5E3 !important;
  line-height: 1.4;
}

/* ── Sidebar expander ── */
[data-testid="stSidebar"] .stExpander {
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 10px !important;
  background: rgba(255,255,255,0.03) !important;
}
[data-testid="stSidebar"] .stExpander summary { color: #B8CDD9 !important; }

/* ── Sidebar footer note ── */
.sidebar-footer {
  font-size: 0.72rem;
  color: #607A8E !important;
  text-align: center;
  margin-top: 0.5rem;
}

/* ══════════════════════════════════════════════════════════
   HERO CARD
══════════════════════════════════════════════════════════ */
.hero {
  background: #ffffff;
  border: 1px solid #E0E7EF;
  border-radius: 20px;
  padding: 1.35rem 1.5rem 1.25rem;
  box-shadow: 0 8px 28px rgba(15,39,68,0.07);
  margin-bottom: 1.1rem;
  position: relative;
  overflow: hidden;
}
/* Decorative teal accent bar */
.hero::before {
  content: "";
  position: absolute;
  top: 0; left: 0;
  width: 4px; height: 100%;
  background: linear-gradient(180deg, #19857F, #28A89F);
  border-radius: 20px 0 0 20px;
}
.hero h2 {
  margin: 0 0 0.3rem;
  font-size: clamp(1.2rem, 2.5vw, 1.65rem);
  letter-spacing: -0.03em;
  color: #0E2540;
  font-weight: 700;
}
.hero p {
  margin: 0;
  color: #52667A;
  font-size: 0.93rem;
  line-height: 1.55;
  max-width: 640px;
}

/* ── Status pills row ── */
.status-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.85rem; }
.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  border-radius: 999px;
  padding: 0.22rem 0.68rem;
  font-size: 0.74rem;
  font-weight: 600;
  border: 1px solid #D5DFE9;
  background: #F5F8FB;
  color: #3A5068;
}
.pill.ok   { background: #E6F5F0; border-color: #AEDCCF; color: #135E55; }
.pill.info { background: #EAF1FB; border-color: #AECAE8; color: #1A456A; }

/* ══════════════════════════════════════════════════════════
   EMPTY STATE / SUGGESTION AREA
══════════════════════════════════════════════════════════ */
.empty-header {
  background: #fff;
  border: 1px dashed #CBD5E0;
  border-radius: 16px;
  padding: 1.1rem 1.25rem 1.15rem;
  margin-bottom: 0.75rem;
}
.empty-header h3 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: #0E2540;
  font-weight: 600;
}
.empty-header p {
  margin: 0;
  color: #52667A;
  font-size: 0.88rem;
}

/* Example question buttons — override default Streamlit style */
div[data-testid="stHorizontalBlock"] .stButton > button {
  border-radius: 10px !important;
  border: 1px solid #D5DFE9 !important;
  background: #FAFCFE !important;
  color: #1A3A52 !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  text-align: left !important;
  transition: background 0.15s, border-color 0.15s, box-shadow 0.15s !important;
  padding: 0.5rem 0.8rem !important;
  line-height: 1.4 !important;
  height: auto !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
  background: #EAF5F3 !important;
  border-color: #19857F !important;
  box-shadow: 0 3px 10px rgba(25,133,127,0.1) !important;
  color: #0E4F4A !important;
}

/* ══════════════════════════════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
  background: #ffffff;
  border: 1px solid #E0E7EF;
  border-radius: 16px;
  padding: 0.2rem 0.45rem;
  box-shadow: 0 3px 12px rgba(15,39,68,0.04);
  margin-bottom: 0.15rem;
}

/* Chat input box */
[data-testid="stChatInput"] {
  max-width: 940px;
  margin: 0 auto;
}
[data-testid="stChatInput"] > div {
  border-radius: 14px !important;
  border: 1.5px solid #D0DCE8 !important;
  box-shadow: 0 4px 16px rgba(15,39,68,0.07) !important;
  background: #fff !important;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: #19857F !important;
  box-shadow: 0 0 0 3px rgba(25,133,127,0.12), 0 4px 16px rgba(15,39,68,0.07) !important;
}

/* ── Blocked / warning card ── */
.blocked-card {
  background: #FFF8EC;
  border: 1px solid #F0D080;
  border-left: 4px solid #E0A020;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #7A4A08;
  line-height: 1.5;
}
.blocked-card .bc-icon { font-size: 1.1rem; margin-right: 0.4rem; }

/* ── Source citation pills inside answers ── */
.src-tag {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: #EAF1FB;
  border: 1px solid #AECAE8;
  color: #1A456A;
  margin: 0 0.15rem;
}

/* ══════════════════════════════════════════════════════════
   AUTH GATE CARD
══════════════════════════════════════════════════════════ */
.gate {
  max-width: 460px;
  margin: 9vh auto 0;
  background: #ffffff;
  border: 1px solid #E0E7EF;
  border-radius: 22px;
  padding: 2.1rem 1.8rem 1.9rem;
  box-shadow: 0 20px 50px rgba(15,39,68,0.09);
  text-align: center;
}
.gate .gate-icon {
  width: 52px; height: 52px;
  border-radius: 14px;
  background: linear-gradient(145deg, #19857F, #28A89F);
  display: grid; place-items: center;
  margin: 0 auto 0.85rem;
  font-weight: 700;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  color: #fff;
  box-shadow: 0 8px 20px rgba(25,133,127,0.25);
}
.gate h2 { margin: 0 0 0.45rem; color: #0E2540; font-size: 1.3rem; font-weight: 700; }
.gate p  { color: #52667A; margin: 0 0 1.3rem; font-size: 0.93rem; line-height: 1.5; }

/* ══════════════════════════════════════════════════════════
   FOOTER ATTRIBUTION
══════════════════════════════════════════════════════════ */
.app-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.73rem;
  color: #8096AA;
  padding: 0.5rem 0;
  flex-wrap: wrap;
}
.app-footer span { opacity: 0.6; }
.app-footer .dot { opacity: 0.35; }

/* ══════════════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .block-container {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    padding-bottom: 7.5rem;
  }
  .hero    { padding: 1rem 1.05rem; }
  .gate    { margin-top: 5vh; padding: 1.5rem 1.2rem; }
}

/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #C8D6E2; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #A0B5C5; }
</style>
"""

st.markdown(_APP_CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# AUTH HELPERS
# ──────────────────────────────────────────────────────────
def _auth_configured() -> bool:
    try:
        return bool(st.secrets.get("auth"))
    except Exception:
        return False


def _render_gate(title: str, body: str, button_label: str, on_click, args=()) -> None:
    """Render a centred auth / access-denied card."""
    st.markdown(
        f"""
        <div class="gate">
          <div class="gate-icon">HA</div>
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col = st.columns([1, 2, 1])[1]
    with col:
        st.button(
            button_label,
            on_click=on_click,
            args=args,
            type="primary",
            use_container_width=True,
        )


# ── Auth gate ──
if _auth_configured():
    if not st.user.is_logged_in:
        _render_gate(
            "Sign in to HR Atlas",
            "Use your company Google account to ask questions about official HR policy.",
            "Continue with Google",
            st.login,
            ("google",),
        )
        st.stop()

    email = (st.user.email or "").lower()
    if config.ALLOWED_EMPLOYEE_EMAILS and email not in config.ALLOWED_EMPLOYEE_EMAILS:
        _render_gate(
            "Access not granted",
            f"{st.user.email} is not on the approved employee list. Contact HR if you need access.",
            "Log out",
            st.logout,
        )
        st.stop()


# ──────────────────────────────────────────────────────────
# CACHED RESOURCES
# ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _tracing_status():
    try:
        return check_langsmith_tracing()
    except Exception as exc:
        return False, f"LangSmith check errored: {exc}"


@st.cache_resource(show_spinner="Connecting to the policy knowledge base…")
def get_agent():
    return build_hr_assistant()


# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────
def _render_sidebar(tracing_ok: bool, tracing_msg: str) -> None:
    with st.sidebar:
        # ── Brand ──────────────────────────────────────────
        st.markdown(
            """
            <div class="brand-mark">
              <div class="mark">HA</div>
              <div>
                <h1>HR Atlas</h1>
                <p>Hybrid RAG · Policy Desk</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── New conversation ────────────────────────────────
        if st.button("＋  New conversation", use_container_width=True):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")

        # ── Policy topics ───────────────────────────────────
        st.caption("POLICY TOPICS")
        chips = "".join(
            f'<span class="topic">{name}</span>'
            for name in sorted(config.HR_POLICY_CATEGORIES)
        )
        st.markdown(f'<div class="topic-wrap">{chips}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Workspace status ────────────────────────────────
        with st.expander("Workspace status", expanded=False):
            trace_icon = "🟢" if tracing_ok else "⚪"
            st.caption(f"{trace_icon} Tracing · {tracing_msg}")
            st.caption(f"🛡️ Guardrail: {config.GUARDRAIL_PROVIDER}")
            st.caption(f"📚 Collection: {config.QDRANT_COLLECTION_NAME}")
            st.caption(f"🤖 Model: {config.LLM_MODEL_NAME}")

        st.markdown("---")

        # ── Auth / user ─────────────────────────────────────
        if _auth_configured():
            st.caption(f"Signed in as **{st.user.email}**")
            st.button("Log out", on_click=st.logout, use_container_width=True)
        else:
            st.caption("🔓 Local mode — Google login not configured.")

        # ── Sidebar footer ──────────────────────────────────
        st.markdown(
            f'<p class="sidebar-footer">HR Atlas {_VERSION}</p>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────
# HERO CARD
# ──────────────────────────────────────────────────────────
def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h2>Ask company policy — get cited answers</h2>
          <p>
            HR Atlas retrieves information directly from official policy documents.
            Topics covered include leave, work from home, probation, notice period,
            reimbursement, travel expense, and more. If it's not in the source, the
            assistant will say so — it never fabricates policy.
          </p>
          <div class="status-row">
            <span class="pill ok">&#10003; Grounded in policy files</span>
            <span class="pill info">Hybrid search · BM25 + semantic</span>
            <span class="pill">&#128737; Safety screened</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────
# EMPTY STATE  (shown when no messages yet)
# ──────────────────────────────────────────────────────────
def _render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-header">
          <h3>💡 Try a policy question</h3>
          <p>Select one of the common questions below, or type your own in the chat box.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"example_{i}", use_container_width=True):
                st.session_state.pending_prompt = q
                st.rerun()


# ──────────────────────────────────────────────────────────
# BLOCKED MESSAGE CARD
# ──────────────────────────────────────────────────────────
def _blocked_card(text: str) -> None:
    st.markdown(
        f'<div class="blocked-card"><span class="bc-icon">⚠️</span>{text}</div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────
# FOOTER  (attribution row)
# ──────────────────────────────────────────────────────────
def _render_footer() -> None:
    st.markdown(
        """
        <div class="app-footer">
          <span>Powered by</span>
          <span>Gemini</span>
          <span class="dot">·</span>
          <span>Qdrant</span>
          <span class="dot">·</span>
          <span>LangChain / LangGraph</span>
          <span class="dot">·</span>
          <span>Jina AI</span>
          <span class="dot">·</span>
          <span>Groq</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ──────────────────────────────────────────────────────────
# ASSEMBLE PAGE
# ──────────────────────────────────────────────────────────
tracing_ok, tracing_msg = _tracing_status()
_render_sidebar(tracing_ok, tracing_msg)

agent, cache = get_agent()

_render_hero()

# ── Chat history or empty state ──
if not st.session_state.messages:
    _render_empty_state()
else:
    for msg in st.session_state.messages:
        avatar = "🧑" if msg["role"] == "user" else "🗂️"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("blocked"):
                _blocked_card(msg["content"])
            else:
                st.markdown(msg["content"])

# ── Chat input ──
typed = st.chat_input("Ask about leave, WFH, notice period, expenses…")
question = st.session_state.pop("pending_prompt", None) or typed

if question:
    # Immediately show the user bubble
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    # Assistant response
    with st.chat_message("assistant", avatar="🗂️"):
        with st.spinner("Looking up the policy…"):
            answer = ask(agent, cache, question, thread_id=st.session_state.thread_id)

        blocked = answer in (INPUT_BLOCKED_MESSAGE, OUTPUT_BLOCKED_MESSAGE)
        if blocked:
            _blocked_card(answer)
        else:
            st.markdown(answer)

    # Persist to session state and rerender
    if answer != INPUT_BLOCKED_MESSAGE:
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "blocked": blocked}
        )
        st.rerun()

_render_footer()
