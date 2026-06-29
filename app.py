# import streamlit as st
# from dotenv import load_dotenv

# from langchain_core.messages import HumanMessage, AIMessageChunk
# from dental_agent.agent import dental_graph

# load_dotenv()

# st.set_page_config(
#     page_title="DantaVaidya AI",
#     page_icon="🦷",
#     layout="wide"
# )

# st.title("🦷 DantaVaidya AI")
# st.caption("Multi-Agent Dental Appointment Assistant")

# # Initialize chat history
# if "history" not in st.session_state:
#     st.session_state.history = []

# # Display previous messages
# for msg in st.session_state.history:
#     if isinstance(msg, HumanMessage):
#         with st.chat_message("user"):
#             st.write(msg.content)
#     else:
#         with st.chat_message("assistant"):
#             st.write(msg.content)

# # Chat input
# prompt = st.chat_input("Ask anything about appointments...")

# if prompt:
#     # Show user message
#     with st.chat_message("user"):
#         st.write(prompt)

#     st.session_state.history.append(HumanMessage(content=prompt))

#     with st.chat_message("assistant"):

#         placeholder = st.empty()
#         response = ""

#         final_messages = None

#         try:
#             for event_type, data in dental_graph.stream(
#                 {"messages": st.session_state.history},
#                 stream_mode=["messages", "values"],
#                 config={"recursion_limit": 20},
#             ):

#                 if event_type == "messages":

#                     chunk, meta = data

#                     if (
#                         isinstance(chunk, AIMessageChunk)
#                         and chunk.content
#                         and not getattr(chunk, "tool_calls", None)
#                     ):
#                         response += chunk.content
#                         placeholder.markdown(response)

#                 elif event_type == "values":
#                     final_messages = data.get("messages", [])

#             if final_messages:
#                 st.session_state.history = final_messages

#         except Exception as e:
#             st.error(str(e))




import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from dental_agent.agent import dental_graph

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DantaVaidya AI",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global resets */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f8f7f4;
    border-right: 1px solid #e5e3dc;
    min-width: 240px !important;
    max-width: 240px !important;
}
[data-testid="stSidebar"] .stMarkdown p { margin: 0; }

/* Chat messages */
.user-bubble {
    background: #1D9E75;
    color: #fff;
    padding: 10px 14px;
    border-radius: 12px 4px 12px 12px;
    font-size: 14px;
    line-height: 1.55;
    max-width: 78%;
    margin-left: auto;
    margin-bottom: 4px;
}
.ai-bubble {
    background: #ffffff;
    border: 1px solid #e5e3dc;
    padding: 10px 14px;
    border-radius: 4px 12px 12px 12px;
    font-size: 14px;
    line-height: 1.55;
    max-width: 82%;
    margin-bottom: 4px;
}
.agent-tag {
    display: inline-block;
    font-size: 11px;
    color: #085041;
    background: #E1F5EE;
    border-radius: 4px;
    padding: 2px 8px;
    margin-bottom: 5px;
    font-weight: 500;
}
.chat-time {
    font-size: 11px;
    color: #b4b2a9;
    margin-top: 3px;
}
.user-time { text-align: right; }

/* Quick action chips */
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 12px; }
.chip {
    font-size: 12px;
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid #d3d1c7;
    background: #fff;
    color: #5f5e5a;
    cursor: pointer;
    transition: all .15s;
}
.chip:hover { border-color: #1D9E75; color: #085041; background: #E1F5EE; }

/* Metric cards */
.metric-row { display: flex; gap: 8px; margin: 0 0 12px; }
.metric-card {
    flex: 1;
    background: #fff;
    border: 1px solid #e5e3dc;
    border-radius: 8px;
    padding: 10px 12px;
}
.metric-label { font-size: 11px; color: #888780; margin-bottom: 4px; }
.metric-val { font-size: 20px; font-weight: 500; color: #2c2c2a; }

/* Agent status dots */
.agent-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 0;
    font-size: 13px;
    color: #5f5e5a;
}
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: #1D9E75; }
.dot-amber { background: #EF9F27; }
.dot-gray  { background: #B4B2A9; }

/* Thinking spinner */
.thinking-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #1D9E75;
    background: #E1F5EE;
    border: 1px solid #9FE1CB;
    border-radius: 6px;
    padding: 4px 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "agents_used" not in st.session_state:
    st.session_state.agents_used = set()
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 16px">
      <div style="width:34px;height:34px;border-radius:8px;background:#1D9E75;
                  display:flex;align-items:center;justify-content:center;
                  font-size:18px;flex-shrink:0">🦷</div>
      <div>
        <div style="font-size:15px;font-weight:500;color:#2c2c2a">DantaVaidya</div>
        <div style="font-size:11px;color:#888780">AI Dental Assistant</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Agent status
    st.markdown("<div style='font-size:11px;font-weight:500;color:#888780;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px'>Agents</div>", unsafe_allow_html=True)

    agents_used = st.session_state.agents_used
    agent_defs = [
        ("info_agent",          "Info agent",        "Answers queries"),
        ("booking_agent",       "Booking agent",     "Books appointments"),
        ("cancellation_agent",  "Cancel agent",      "Cancels bookings"),
        ("rescheduling_agent",  "Reschedule agent",  "Changes bookings"),
    ]
    for key, name, role in agent_defs:
        dot_cls = "dot-green" if key in agents_used else "dot-gray"
        status  = "Active" if key in agents_used else "Standby"
        st.markdown(f"""
        <div class="agent-row">
          <div class="dot {dot_cls}"></div>
          <div>
            <div style="font-weight:500;color:#2c2c2a;font-size:13px">{name}</div>
            <div style="font-size:11px;color:#888780">{status}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Session metrics
    st.markdown("<div style='font-size:11px;font-weight:500;color:#888780;text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px'>This session</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Messages</div>
          <div class="metric-val">{st.session_state.msg_count}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Agents used</div>
          <div class="metric-val">{len(agents_used)} / 4</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # System info
    st.markdown("<div style='font-size:11px;font-weight:500;color:#888780;text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px'>System</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px;color:#5f5e5a;line-height:2">
      <div style="display:flex;justify-content:space-between">
        <span>LangGraph</span><span style="color:#1D9E75;font-weight:500">Running</span>
      </div>
      <div style="display:flex;justify-content:space-between">
        <span>Stream mode</span><span>Messages</span>
      </div>
      <div style="display:flex;justify-content:space-between">
        <span>Recursion limit</span><span>20</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.agents_used = set()
        st.session_state.msg_count = 0
        st.rerun()

# ── Main area ──────────────────────────────────────────────────────────────────
# Header bar
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:14px 24px;border-bottom:1px solid #e5e3dc;background:#fafaf8">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:15px;font-weight:500;color:#2c2c2a">Appointment assistant</span>
    <span style="font-size:12px;color:#085041;background:#E1F5EE;
                 border:1px solid #9FE1CB;border-radius:20px;padding:3px 10px">
      ✓ Multi-agent active
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Render chat history ────────────────────────────────────────────────────────
AGENT_LABELS = {
    "info_agent":          ("Info agent",       "🔍"),
    "booking_agent":       ("Booking agent",    "📅"),
    "cancellation_agent":  ("Cancel agent",     "✖"),
    "rescheduling_agent":  ("Reschedule agent", "🔄"),
}

chat_container = st.container()
with chat_container:
    # Welcome message on first load
    if not st.session_state.history:
        st.markdown("""
        <div style="max-width:640px;margin:32px auto 0">
          <div class="agent-tag">🔍 Info agent</div>
          <div class="ai-bubble">
            Hello! I'm <strong>DantaVaidya</strong>, your dental appointment assistant.
            I can help you <strong>book</strong>, <strong>cancel</strong>, or
            <strong>reschedule</strong> appointments, and answer any questions about our services.
            How can I help you today?
          </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.history:
        if isinstance(msg, HumanMessage):
            st.markdown(f"""
            <div style="max-width:640px;margin:8px auto;text-align:right">
              <div class="user-bubble">{msg.content}</div>
            </div>""", unsafe_allow_html=True)
        elif isinstance(msg, AIMessage) and msg.content:
            # Try to get agent tag from metadata
            agent_key  = getattr(msg, "name", None) or "info_agent"
            label, ico = AGENT_LABELS.get(agent_key, ("Assistant", "🤖"))
            st.markdown(f"""
            <div style="max-width:640px;margin:8px auto">
              <div class="agent-tag">{ico} {label}</div>
              <div class="ai-bubble">{msg.content}</div>
            </div>""", unsafe_allow_html=True)

# ── Quick action chips ─────────────────────────────────────────────────────────
QUICK_ACTIONS = [
    "What services do you offer?",
    "Book a teeth cleaning",
    "Cancel my appointment",
    "Reschedule to next week",
    "What are your clinic timings?",
    "Emergency dental care",
]

st.markdown("<div style='max-width:640px;margin:8px auto'>", unsafe_allow_html=True)
chip_cols = st.columns(len(QUICK_ACTIONS))
for i, (col, action) in enumerate(zip(chip_cols, QUICK_ACTIONS)):
    with col:
        if st.button(action, key=f"chip_{i}", use_container_width=False):
            st.session_state._chip_prompt = action

# ── Chat input ─────────────────────────────────────────────────────────────────
st.markdown("<div style='max-width:640px;margin:12px auto 0'>", unsafe_allow_html=True)
prompt = st.chat_input("Ask about appointments, services, or dental queries…")

# Handle chip or typed input
final_prompt = prompt or st.session_state.pop("_chip_prompt", None)

if final_prompt:
    st.session_state.history.append(HumanMessage(content=final_prompt))
    st.session_state.msg_count += 1

    # Show user message immediately
    st.markdown(f"""
    <div style="max-width:640px;margin:8px auto;text-align:right">
      <div class="user-bubble">{final_prompt}</div>
    </div>""", unsafe_allow_html=True)

    # Thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("""
    <div style="max-width:640px;margin:8px auto">
      <div class="agent-tag">⚙ Supervisor</div>
      <div class="ai-bubble" style="color:#888780;font-style:italic">
        Routing to the right agent…
      </div>
    </div>""", unsafe_allow_html=True)

    # Stream response
    response_placeholder = st.empty()
    response = ""
    final_messages = None
    current_agent = "info_agent"

    try:
        for event_type, data in dental_graph.stream(
            {"messages": st.session_state.history},
            stream_mode=["messages", "values"],
            config={"recursion_limit": 20},
        ):
            if event_type == "messages":
                chunk, meta = data
                node = meta.get("langgraph_node", "info_agent")

                # Detect which agent is active
                if node in AGENT_LABELS:
                    current_agent = node
                    st.session_state.agents_used.add(node)
                    label, ico = AGENT_LABELS[node]
                    thinking_placeholder.markdown(f"""
                    <div style="max-width:640px;margin:8px auto">
                      <div class="agent-tag">{ico} {label}</div>
                      <div class="ai-bubble" style="color:#888780;font-style:italic">
                        Working on your request…
                      </div>
                    </div>""", unsafe_allow_html=True)

                if (
                    isinstance(chunk, AIMessageChunk)
                    and chunk.content
                    and not getattr(chunk, "tool_calls", None)
                ):
                    response += chunk.content
                    label, ico = AGENT_LABELS.get(current_agent, ("Assistant", "🤖"))
                    response_placeholder.markdown(f"""
                    <div style="max-width:640px;margin:8px auto">
                      <div class="agent-tag">{ico} {label}</div>
                      <div class="ai-bubble">{response}</div>
                    </div>""", unsafe_allow_html=True)

            elif event_type == "values":
                final_messages = data.get("messages", [])

        thinking_placeholder.empty()
        if final_messages:
            st.session_state.history = final_messages
            st.session_state.msg_count += 1

    except Exception as e:
        thinking_placeholder.empty()
        st.error(f"Something went wrong: {e}")

    st.rerun()

# ── Footer hint ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;font-size:11px;color:#b4b2a9;padding:16px 0 8px">
  DantaVaidya routes each request through specialised AI agents — info, booking, cancellation, and rescheduling
</div>""", unsafe_allow_html=True)