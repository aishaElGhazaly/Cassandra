import time
import logging
import streamlit as st
from logic import cassandra, summarizer
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logging.basicConfig(
    level=logging.WARNING,
    filename="logs/cassandra.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

# Display header only if no messages yet 
if not st.session_state.messages: 
    # Centered vertically and horizontally 
    st.markdown( 
        """ 
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Noto+Sans+Arabic:wght@100..900&family=Spectral:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,800;1,200;1,300;1,400;1,500;1,600;1,700;1,800&display=swap');

            .full-screen-center 
            {
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center; 
                height: 80vh; /* almost full viewport height */ 
                text-align: center;
            } 
        </style> 
        """, unsafe_allow_html=True 
    ) 
    st.markdown( 
        """ 
            <div class="full-screen-center"> 
                <p style="margin-bottom: 0; font-size: 2.75rem; font-weight: 700; font-family: 'Spectral';">Cassandra</p> 
                <p style="font-size: 1.75rem; font-weight: 600;">Your personal music editor & curator.</p> 
            </div>
        """, unsafe_allow_html=True
    )

# --- Replay past messages ---
if st.session_state.messages:
    for msg in st.session_state.messages:
        avatar = "C.png" if msg["role"] == "assistant" else "U.png"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- Chat input ---
user_input = st.chat_input("Let's talk music!", max_chars=300)

if user_input:
    # Save + display user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="U.png"):
        st.markdown(user_input)

    # --- Prepare history for LangChain ---
    if len(st.session_state.messages) > 20:
        history_to_summarize = st.session_state.messages[:-4]
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history_to_summarize)

        try:
            result = st.session_state.summarizer.invoke({"history": history_text})
            st.session_state.summary = getattr(result, "content", str(result))
            print("Summary:", st.session_state.summary)
        except Exception:
            logging.exception("Summarization failed")

        # Collapse: summary + last 4 turns
        history_for_cassandra = [SystemMessage(content=f"Conversation summary: {st.session_state.summary}")]
        for m in st.session_state.messages[-4:]:
            if m["role"] == "user":
                history_for_cassandra.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                history_for_cassandra.append(AIMessage(content=m["content"]))
    else:
        # Convert all messages
        history_for_cassandra = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                history_for_cassandra.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                history_for_cassandra.append(AIMessage(content=m["content"]))

    # --- Stream Cassandra response ---
    try:
        assistant_text = ""
        with st.chat_message("assistant", avatar="C.png"):
            response_box = st.empty()  # placeholder
            for chunk in st.session_state.cassandra.stream({
                "input": user_input,
                "history": history_for_cassandra
            }):
                text_chunk = getattr(chunk, "content", str(chunk))
                assistant_text += text_chunk
                response_box.markdown(assistant_text)  # updates in real-time
                time.sleep(0.05) # slight delay to improve UX

    except Exception as e:
        logging.exception(f"Invocation failed: {e}")
        assistant_text = "Apologies, Something went wrong. Please try again."
        with st.chat_message("assistant"):
            st.markdown(assistant_text, avatar="C.png")

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
