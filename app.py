import time
import streamlit as st
from logic import cassandra, summarizer
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# --- Streamlit page config ---
st.set_page_config(
    page_title="Cassandra",
    page_icon="C.png",
)

# --- Initialize Cassandra (LLM wrapper) ---
if "cassandra" not in st.session_state:
    st.session_state.cassandra = cassandra()

# --- Initialize summarizer ---
if "summarizer" not in st.session_state:
    st.session_state.summarizer = summarizer()

# --- Initialize chat history (simple dicts for UI) ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{role: "user"/"assistant", content: str}]

# --- Initialize summary ---
if "summary" not in st.session_state:
    st.session_state.summary = ""

# --- Initialize history cache ---
if "history_for_cassandra" not in st.session_state:
    st.session_state.history_for_cassandra = []
if "last_msg_count" not in st.session_state:
    st.session_state.last_msg_count = 0

# --- Header (only when no messages yet) ---
if not st.session_state.messages:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Lato:wght@100;300;400;700;900&family=Noto+Sans+Arabic:wght@100..900&family=Spectral:wght@200;300;400;500;600;700;800&display=swap');

            .full-screen-center {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 80vh; /* almost full viewport height */
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="full-screen-center">
            <p style="margin-bottom: 0; font-size: 2.75rem; font-weight: 700; font-family: 'Spectral';">Cassandra</p>
            <p style="font-size: 1.75rem; font-weight: 600;">Your personal music editor & curator.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Replay past messages in UI ---
if st.session_state.messages:
    for msg in st.session_state.messages:
        avatar = "C.png" if msg["role"] == "assistant" else "U.png"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- Update history only when new messages are added ---
if len(st.session_state.messages) != st.session_state.last_msg_count:
    if len(st.session_state.messages) > 10:
        # summarize everything except last 4 turns
        history_to_summarize = st.session_state.messages[:-4]
        history_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in history_to_summarize
        )

        try:
            result = st.session_state.summarizer.invoke({"history": history_text})
            st.session_state.summary = getattr(result, "content", str(result))
        except Exception:
            st.session_state.summary = ""

        # collapsed history = summary + last 4 turns
        st.session_state.history_for_cassandra = [
            SystemMessage(content=f"Conversation summary: {st.session_state.summary}")
        ]
        for m in st.session_state.messages[-4:]:
            if m["role"] == "user":
                st.session_state.history_for_cassandra.append(
                    HumanMessage(content=m["content"])
                )
            elif m["role"] == "assistant":
                st.session_state.history_for_cassandra.append(
                    AIMessage(content=m["content"])
                )

    else:
        # full history if <= 10
        st.session_state.history_for_cassandra = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                st.session_state.history_for_cassandra.append(
                    HumanMessage(content=m["content"])
                )
            elif m["role"] == "assistant":
                st.session_state.history_for_cassandra.append(
                    AIMessage(content=m["content"])
                )

    # update tracker
    st.session_state.last_msg_count = len(st.session_state.messages)

# always use cached history
history_for_cassandra = st.session_state.history_for_cassandra

# --- Chat input ---
user_input = st.chat_input("Let's talk music!", max_chars=300)

if user_input:
    # display user input
    with st.chat_message("user", avatar="U.png"):
        st.markdown(user_input)

    # save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- Stream Cassandra response ---
    try:
        assistant_text = ""
        with st.chat_message("assistant", avatar="C.png"):
            response_box = st.empty()  # placeholder
            for chunk in st.session_state.cassandra.stream(
                {"input": user_input, "history": history_for_cassandra}
            ):
                text_chunk = getattr(chunk, "content", str(chunk))
                assistant_text += text_chunk
                response_box.markdown(assistant_text)  # updates in real-time
                time.sleep(0.05)  # slight delay to improve UX

    except Exception:
        assistant_text = "Apologies, something went wrong. Please try again."
        with st.chat_message("assistant", avatar="C.png"):
            st.markdown(assistant_text)

    # save assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
