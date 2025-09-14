import os
import streamlit as st
from langchain_openai import ChatOpenAI 
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Pull key from Streamlit secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- Summarizer Chain ---
def summarizer():
    summarizer_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following chat history into a concise form, preserving important context."),
        ("human", "{history}")
    ])

    summarizer_llm = ChatOpenAI( 
        temperature=0, 
        model_name="gpt-5-nano", 
        max_retries=0,
        streaming=False
    ) 
    
    return summarizer_prompt | summarizer_llm

# --- Cassandra Chain ---
def cassandra():  
    # Load the Cassandra system prompt 
    system_prompt = st.secrets.get("SYSTEM_PROMPT")

    # Set up the prompt with system + user inputs 
    chat_prompt = ChatPromptTemplate.from_messages([ 
        ("system", system_prompt), 
        MessagesPlaceholder(variable_name="history"), 
        ("human", "{input}") 
    ])
    
    # Create the Main Cassandra LLM
    chat_llm  = ChatOpenAI( 
        temperature=0.5, 
        model_name="gpt-5-nano",
        max_retries=0,
        streaming=True
    )    

    chat_chain = chat_prompt  | chat_llm
    
    return chat_chain
