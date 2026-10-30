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

st.set_page_config(
    page_title="HR Atlas · Policy Assistant",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

EXAMPLE_QUESTIONS = [
    "How many days of annual leave do I get?",
    "How do I request work from home?",
    "What is the notice period when I resign?",
    "How are travel expenses reimbursed?",
    "What are the rules during probation?",
    "What public holidays does the company observe?",
]

_APP_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap");

html, body, [class*="st-"], .stMarkdown, .stChatMessage {
  font-family: "Source Sans 3", "Segoe UI", sans-serif;
}

.stApp {
  background:
    radial-gradient(1200px 420px at 8% -10%, rgba(26, 122, 116, 0.08), transparent 55%),
    radial-gradient(900px 380px at 100% 0%, rgba(15, 39, 68, 0.06), transparent 50%),
    #F4F6F8;
}

[data-testid="stHeader"] {
  background: rgba(244, 246, 248, 0.85);
  backdrop-filter: blur(8px);
}

[data-testid="stToolbar"] { display: none; }
footer { visibility: hidden; height: 0; }

.block-container {
  max-width: 920px;
  padding-top: 1.15rem;
  padding-bottom: 6.5rem;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0E2238 0%, #12324D 58%, #0F2744 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stSidebar"] * { color: #E8EEF4 !important; }
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
  color: #A9B8C7 !important;
}
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #F4F8FB !important;
  font-weight: 600;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(26, 122, 116, 0.35);
  border-color: rgba(26, 122, 116, 0.7);
}
[data-testid="stSidebar"] hr {
  border-color: rgba(255, 255, 255, 0.1);
  margin: 0.85rem 0;
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.2rem 0 1rem;
}
.brand-mark .mark {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  background: linear-gradient(145deg, #1A7A74, #2A9B93);
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: 0.02em;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.22);
}
.brand-mark h1 {
  font-size: 1.05rem;
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.brand-mark p {
  margin: 0;
  font-size: 0.78rem;
  color: #A9B8C7 !important;
}

.hero {
  background: #ffffff;
  border: 1px solid #E3E8EE;
  border-radius: 18px;
  padding: 1.35rem 1.45rem 1.2rem;
  box-shadow: 0 10px 30px rgba(15, 39, 68, 0.06);
  margin-bottom: 1rem;
}
.hero h2 {
  margin: 0 0 0.35rem;
  font-size: clamp(1.35rem, 2.4vw, 1.85rem);
  letter-spacing: -0.03em;
  color: #0F2744;
}
.hero p {
  margin: 0;
  color: #5B6B7C;
  font-size: 0.98rem;
  line-height: 1.5;
}

.status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.9rem;
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 999px;
  padding: 0.22rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #D7E0E8;
  background: #F8FAFC;
  color: #345;
}
.pill.ok { background: #E8F6F1; border-color: #B7E0D4; color: #146057; }
.pill.warn { background: #FFF6E8; border-color: #F0D7A3; color: #8A5A12; }

.topic-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.topic {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 0.28rem 0.55rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.empty {
  background: #fff;
  border: 1px dashed #D5DEE7;
  border-radius: 16px;
  padding: 1.15rem 1.2rem 1.3rem;
}
.empty h3 {
  margin: 0 0 0.35rem;
  font-size: 1.02rem;
  color: #0F2744;
}
.empty p {
  margin: 0 0 0.9rem;
  color: #5B6B7C;
  font-size: 0.92rem;
}

[data-testid="stChatMessage"] {
  background: #ffffff;
  border: 1px solid #E3E8EE;
  border-radius: 16px;
  padding: 0.15rem 0.35rem;
  box-shadow: 0 4px 14px rgba(15, 39, 68, 0.04);
}
[data-testid="stChatInput"] {
  max-width: 920px;
  margin: 0 auto;
}

.gate {
  max-width: 460px;
  margin: 8vh auto 0;
  background: #fff;
  border: 1px solid #E3E8EE;
  border-radius: 20px;
  padding: 2rem 1.7rem;
  box-shadow: 0 18px 40px rgba(15, 39, 68, 0.08);
  text-align: center;
}
.gate h2 { margin: 0.4rem 0 0.45rem; color: #0F2744; }
.gate p { color: #5B6B7C; margin: 0 0 1.2rem; }

@media (max-width: 768px) {
  .block-container { padding-left: 0.85rem; padding-right: 0.85rem; padding-bottom: 7.25rem; }
  .hero { padding: 1.05rem 1rem; }
  .empty { padding: 1rem; }
}
</style>
"""

st.markdown(_APP_CSS, unsafe_allow_html=True)


def _auth_configured() -> bool:
    try:
        return bool(st.secrets.get("auth"))
    except Exception:
        return False


def _render_gate(title: str, body: str, button_label: str, on_click, args=()) -> None:
    st.markdown(
        f'<div class="gate"><div class="brand-mark" style="justify-content:center">'
        f'<div class="mark">HA</div></div>'
        f"<h2>{title}</h2><p>{body}</p></div>",
        unsafe_allow_html=True,
    )
    col = st.columns([1, 2, 1])[1]
    with col:
        st.button(button_label, on_click=on_click, args=args, type="primary", use_container_width=True)


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
else:
    pass


@st.cache_resource(show_spinner=False)
def _tracing_status():
    try:
        return check_langsmith_tracing()
    except Exception as exc:
        return False, f"LangSmith check errored: {exc}"


@st.cache_resource(show_spinner="Connecting to the policy knowledge base…")
def get_agent():
    return build_hr_assistant()


def _render_sidebar(tracing_ok: bool, tracing_msg: str) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-mark">
              <div class="mark">HA</div>
              <div>
                <h1>HR Atlas</h1>
                <p>Hybrid RAG policy desk</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("New conversation", use_container_width=True):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption("POLICY TOPICS")
        chips = "".join(f'<span class="topic">{name}</span>' for name in sorted(config.HR_POLICY_CATEGORIES))
        st.markdown(f'<div class="topic-wrap">{chips}</div>', unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("Workspace status", expanded=False):
            st.caption(("Tracing online · " if tracing_ok else "Tracing idle · ") + tracing_msg)
            st.caption(f"Safety guardrail: {config.GUARDRAIL_PROVIDER}")
            st.caption(f"Collection: {config.QDRANT_COLLECTION_NAME}")

        st.markdown("---")
        if _auth_configured():
            st.caption(f"Signed in as {st.user.email}")
            st.button("Log out", on_click=st.logout, use_container_width=True)
        else:
            st.caption("Local mode — Google login is not configured.")


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h2>Ask company HR policy with cited answers</h2>
          <p>
            HR Atlas retrieves from official policy documents — leave, work from home,
            probation, notice period, reimbursement, and related topics. If it is not
            in the source, the assistant will say so.
          </p>
          <div class="status-row">
            <span class="pill ok">Grounded in policy files</span>
            <span class="pill">Hybrid search</span>
            <span class="pill">Safety screened</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty">
          <h3>Try a policy question</h3>
          <p>Start with one of these, or type your own question below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, question in enumerate(EXAMPLE_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"example_{i}", use_container_width=True):
                st.session_state.pending_prompt = question
                st.rerun()


tracing_ok, tracing_msg = _tracing_status()
_render_sidebar(tracing_ok, tracing_msg)

agent, cache = get_agent()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

_render_hero()

if not st.session_state.messages:
    _render_empty_state()
else:
    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "🗂️"
        with st.chat_message(message["role"], avatar=avatar):
            if message.get("blocked"):
                st.warning(message["content"])
            else:
                st.markdown(message["content"])

typed = st.chat_input("Ask about leave, WFH, notice period, expenses…")
question = st.session_state.pop("pending_prompt", None) or typed

if question:
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🗂️"):
        with st.spinner("Looking up the policy…"):
            answer = ask(agent, cache, question, thread_id=st.session_state.thread_id)
        blocked = answer in (INPUT_BLOCKED_MESSAGE, OUTPUT_BLOCKED_MESSAGE)
        if blocked:
            st.warning(answer)
        else:
            st.markdown(answer)

    if answer != INPUT_BLOCKED_MESSAGE:
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "blocked": blocked}
        )
        st.rerun()
