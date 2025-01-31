from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from agent.state import AssistantGraphState
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import StateGraph, START, END
from agent.assistant import get_llm
import os

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
    
    def __call__(self, state: AssistantGraphState, config: RunnableConfig):
        result = self.runnable.invoke(state, config)
        return {"messages": result}

def safe_assistant():
    system_prompt = open(os.path.join("SYSTEM PROMPTS","safe_llm", "v1.txt")).read()

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", f"""{system_prompt}"""),
            ("placeholder", "{messages}"),
        ]
    )


    llm = get_llm()
    chain = prompt_template | llm

    graph_builder = StateGraph(AssistantGraphState)
    graph_builder.add_node("safe_agent", Assistant(chain))

    graph_builder.add_edge(START,"safe_agent")
    graph_builder.add_edge("safe_agent", END)

    return graph_builder