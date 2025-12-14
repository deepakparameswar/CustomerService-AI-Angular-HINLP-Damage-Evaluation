import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
else:
    raise ValueError("GROQ_API_KEY environment variable is not set")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def callGroq(messages):
    """Call Groq LLM with messages"""
    print(f"callGroq messages: {messages}")
    return llm.invoke(messages)
