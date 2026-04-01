from langchain_groq import ChatGroq
import os


def get_llm():
    return ChatGroq(
        api_key= os.getenv('GROQ_API_KEY'),
        model="llama-3.1-8b-instant"
    )
