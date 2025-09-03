import logging
import streamlit as st
from logic import cassandra, summarizer
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logging.basicConfig(
    level=logging.WARNING,
    filename="logs/cassandra.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
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
                <h1 style="padding-bottom: 5px">Cassandra</h1> 
                <h3 style="padding-top: 5px">Your personal music editor & curator.</h3> 
            </div> 
        """, unsafe_allow_html=True
    )

# --- Replay past messages ---
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- Chat input ---
user_input = st.chat_input("Let's talk music!", max_chars=300)

if user_input:
    # Save + display user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
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

    # --- Call Cassandra (LLM) ---
    try:
        result = st.session_state.cassandra.invoke({
            "input": user_input,
            "history": history_for_cassandra
        })
        print("Raw Cassandra result:", result)
        assistant_text = getattr(result, "content", str(result))
    except Exception:
        logging.exception("Invocation failed")
        assistant_text = "Apologies, Something went wrong. Please try again."

    # Save + display assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
