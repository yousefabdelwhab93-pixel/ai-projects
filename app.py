
import uuid
from pathlib import Path

import streamlit as st

from project1_rag.rag_chain import build_rag_chain
from project2_agent.agent import build_agent


# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Projects Hub",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Projects Hub")
st.caption("RAG • Tool Calling • Conversation Memory")


# --------------------------------------------------
# 2. Session state initialization
# --------------------------------------------------

if "rag_chains" not in st.session_state:
    st.session_state.rag_chains = {}

if "agent" not in st.session_state:
    st.session_state.agent = None

if "agent_thread_id" not in st.session_state:
    st.session_state.agent_thread_id = str(uuid.uuid4())

if "rag_history" not in st.session_state:
    st.session_state.rag_history = []

if "agent_history" not in st.session_state:
    st.session_state.agent_history = []


# --------------------------------------------------
# 3. Sidebar
# --------------------------------------------------

with st.sidebar:
    st.header("Navigation")

    mode = st.radio(
        "Choose a project",
        [
            "Ask Your Documents (RAG)",
            "Teaching Assistant Agent",
        ],
    )

    st.divider()

    if mode == "Ask Your Documents (RAG)":
        search_type = st.selectbox(
            "Retrieval method",
            ["mmr", "similarity"],
        )

        st.caption("MMR balances relevance and diversity.")

        if st.button("Clear RAG chat"):
            st.session_state.rag_history = []
            st.rerun()

    else:
        show_tool_calls = st.checkbox(
            "Show tool calls and results",
            value=True,
        )

        st.caption(
            "The Agent remembers messages within its current thread."
        )

        if st.button("Start a new Agent conversation"):
            st.session_state.agent_thread_id = str(uuid.uuid4())
            st.session_state.agent_history = []
            st.rerun()

        if st.button("Clear Agent chat"):
            st.session_state.agent_history = []
            st.rerun()


# --------------------------------------------------
# 4. RAG application
# --------------------------------------------------

if mode == "Ask Your Documents (RAG)":

    st.header("📚 Ask Your Documents")
    st.write(
        "Ask questions about the PDF and TXT files indexed in Chroma."
    )

    if st.button("Initialize RAG"):
        try:
            with st.spinner("Loading the vector database..."):
                if search_type not in st.session_state.rag_chains:
                    st.session_state.rag_chains[search_type] = (
                        build_rag_chain(search_type)
                    )

            st.success(f"RAG initialized using {search_type}.")

        except Exception as error:
            st.error(f"Could not initialize RAG: {error}")

            st.info(
                "If the database does not exist, open the terminal "
                "at the project root and run: "
                "python -m project1_rag.ingest"
            )

    # Display previous RAG messages
    for item in st.session_state.rag_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

            if item.get("sources"):
                with st.expander("Sources"):
                    for source in item["sources"]:
                        st.write(source)

    question = st.chat_input(
        "Ask a question about your documents..."
    )

    if question:
        st.session_state.rag_history.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        if search_type not in st.session_state.rag_chains:
            with st.chat_message("assistant"):
                st.warning(
                    "Click Initialize RAG before asking your question."
                )

        else:
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Searching your documents..."):
                        rag = st.session_state.rag_chains[search_type]
                        result = rag(question)

                    answer = result["answer"]
                    st.markdown(answer)

                    sources = set()

                    for doc in result["docs"]:
                        filename = Path(
                            doc.metadata.get("source", "Unknown")
                        ).name

                        page = doc.metadata.get("page")

                        if (
                            page is not None
                            and filename.lower().endswith(".pdf")
                        ):
                            source = f"{filename} — page {page + 1}"
                        else:
                            source = filename

                        sources.add(source)

                    sources = sorted(sources)

                    with st.expander("Sources"):
                        if sources:
                            for source in sources:
                                st.write(f"- {source}")
                        else:
                            st.write("No source metadata available.")

                    st.session_state.rag_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                except Exception as error:
                    st.error(f"RAG error: {error}")


# --------------------------------------------------
# 5. Teaching Assistant Agent
# --------------------------------------------------

else:

    st.header("🧑‍🏫 Teaching Assistant Agent")
    st.write(
        "Ask questions, calculate expressions, check grades, "
        "get the date and time, or save notes."
    )

    # Build the agent once per Streamlit session.
    if st.session_state.agent is None:
        try:
            with st.spinner("Initializing the Agent..."):
                st.session_state.agent = build_agent()

        except Exception as error:
            st.error(f"Could not initialize the Agent: {error}")
            st.stop()

    # Display previous messages
    for item in st.session_state.agent_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

            if item.get("events"):
                with st.expander("Tool activity"):
                    for event in item["events"]:
                        st.code(event)

    user_input = st.chat_input(
        "Message your Teaching Assistant..."
    )

    if user_input:
        st.session_state.agent_history.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        assistant_text = ""
        tool_events = []

        config = {
            "configurable": {
                "thread_id": st.session_state.agent_thread_id
            }
        }

        with st.chat_message("assistant"):
            response_area = st.empty()

            try:
                with st.spinner("Agent is thinking..."):
                    for update in st.session_state.agent.stream(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": user_input,
                                }
                            ]
                        },
                        config=config,
                        stream_mode="updates",
                    ):
                        for node_name, node_data in update.items():
                            messages = node_data.get("messages", [])

                            for message in messages:
                                if message.type == "tool":
                                    tool_events.append(
                                        f"Tool result ({message.name}):\n"
                                        f"{message.content}"
                                    )

                                elif message.type == "ai":
                                    for tool_call in (
                                        getattr(message, "tool_calls", [])
                                    ):
                                        tool_events.append(
                                            "Tool call:\n"
                                            f"{tool_call['name']}\n"
                                            f"Arguments: {tool_call['args']}"
                                        )

                                    if message.content:
                                        if isinstance(message.content, str):
                                            assistant_text = message.content
                                        else:
                                            assistant_text = str(
                                                message.content
                                            )

                                        response_area.markdown(
                                            assistant_text
                                        )

                if not assistant_text:
                    assistant_text = (
                        "The Agent finished without a text response."
                    )
                    response_area.markdown(assistant_text)

                if show_tool_calls and tool_events:
                    with st.expander("Tool activity", expanded=True):
                        for event in tool_events:
                            st.code(event)

                st.session_state.agent_history.append(
                    {
                        "role": "assistant",
                        "content": assistant_text,
                        "events": tool_events if show_tool_calls else [],
                    }
                )

            except Exception as error:
                st.error(f"Agent error: {error}")
                st.caption(
                    "Check your API settings and terminal output "
                    "for additional details."
                )
