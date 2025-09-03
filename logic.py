from langchain_openai import ChatOpenAI 
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from dotenv import load_dotenv 

load_dotenv() 
def load_prompt(path="system_prompt.txt") -> str: 
    with open(path, "r", encoding="utf-8") as f: 
        return f.read() 

# --- Summarizer Chain ---
def summarizer():
    summarizer_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following chat history into a concise form, preserving important context."),
        ("human", "{history}")
    ])

    summarizer_llm = ChatOpenAI( 
        temperature=0, 
        model_name="gpt-5-nano", 
        timeout=30, 
        max_retries=0, 
        service_tier="flex" 
    ) 
    
    return summarizer_prompt | summarizer_llm

# --- Cassandra Chain ---
def cassandra():  
    # Load the Cassandra system prompt 
    system_prompt = load_prompt()

    # Set up the prompt with system + user inputs 
    chat_prompt = ChatPromptTemplate.from_messages([ 
        ("system", system_prompt), 
        MessagesPlaceholder(variable_name="history"), 
        ("human", "{input}") 
    ])
    
    # Create the Main Cassandra LLM
    chat_llm  = ChatOpenAI( 
        temperature=0.7, 
        model_name="gpt-5-nano",
        timeout=30, 
        max_retries=0, 
        service_tier="flex",
        streaming=False
    )    

    chat_chain = chat_prompt  | chat_llm
    
    return chat_chain