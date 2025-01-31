from langchain_openai import ChatOpenAI
import os

def get_llm():
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5, api_key=os.getenv("OPENAI_API"))
    return llm