import streamlit as st
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessageChunk
from dental_agent.agent import dental_graph

load_dotenv()

st.set_page_config(
    page_title="DantaVaidya AI",
    page_icon="🦷",
    layout="wide"
)

st.title("🦷 DantaVaidya AI")
st.caption("Multi-Agent Dental Appointment Assistant")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Display previous messages
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    else:
        with st.chat_message("assistant"):
            st.write(msg.content)

# Chat input
prompt = st.chat_input("Ask anything about appointments...")

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):

        placeholder = st.empty()
        response = ""

        final_messages = None

        try:
            for event_type, data in dental_graph.stream(
                {"messages": st.session_state.history},
                stream_mode=["messages", "values"],
                config={"recursion_limit": 20},
            ):

                if event_type == "messages":

                    chunk, meta = data

                    if (
                        isinstance(chunk, AIMessageChunk)
                        and chunk.content
                        and not getattr(chunk, "tool_calls", None)
                    ):
                        response += chunk.content
                        placeholder.markdown(response)

                elif event_type == "values":
                    final_messages = data.get("messages", [])

            if final_messages:
                st.session_state.history = final_messages

        except Exception as e:
            st.error(str(e))