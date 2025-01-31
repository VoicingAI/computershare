from typing import Any, Dict, Literal, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from agent.state import VerifyEmailAssistant
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import StateGraph, START, END
from agent.assistant import get_llm
from agent.tools import email_agent_tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langchain_core.messages import AnyMessage


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
    
    def __call__(self, state: VerifyEmailAssistant, config: RunnableConfig):
        result = self.runnable.invoke({'messages':state['messages']}, config)
        return {"messages": result}

def route_model_output(state: VerifyEmailAssistant) -> Literal["tools", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    
    return END

def update_valid(state: VerifyEmailAssistant):
    messages = state['messages']
    last_message = messages[-1]
    if isinstance(last_message, ToolMessage):
        if last_message.content == "User Valid":
            state["valid_email"] = True
            if "email_attempt" in state:
                state["email_attempt"] += 1
            else:
                state["email_attempt"] = 1
        else:
            if "email_attempt" in state:
                state["email_attempt"] += 1
            else:
                state["email_attempt"] = 1
    return state


def email_assistant():
    system_prompt = open('SYSTEM PROMPTS/email.txt').read()
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"""{system_prompt}"""),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_llm()
    chain = primary_assistant_prompt | llm.bind_tools(email_agent_tools)

    graph_builder = StateGraph(VerifyEmailAssistant)
    graph_builder.add_node("email_agent", Assistant(chain))
    graph_builder.add_node("update_valid", update_valid)
    graph_builder.add_node("tools", ToolNode(email_agent_tools))

    graph_builder.add_edge(START,"email_agent")
    graph_builder.add_conditional_edges("email_agent",route_model_output)
    graph_builder.add_edge("tools", "update_valid")
    graph_builder.add_edge("update_valid", 'email_agent')
    graph_builder.add_edge("email_agent", END)

    return graph_builder