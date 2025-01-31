from typing import Any, Dict, Literal
from langchain_core.prompts import ChatPromptTemplate
from agent.state import ValidateOTPAssistant
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import StateGraph, START, END
from agent.assistant import get_llm
from agent.tools import otp_agent_tools
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode


def route_model_output(state: ValidateOTPAssistant) -> Literal["tools", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def update_valid(state: ValidateOTPAssistant):
    messages = state['messages']
    last_message = messages[-1]
    if isinstance(last_message, ToolMessage):
        if last_message.name == 'verify_processed_otp':
            if last_message.content == "OTP verified successfully.":
                state["valid_otp"] = True
                if "otp_attempt" in state:
                    state["otp_attempt"] += 1
                else:
                    state["otp_attempt"] = 1
            else:
                if "otp_attempt" in state:
                    state["otp_attempt"] += 1
                else:
                    state["otp_attempt"] = 1
    return state

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
    
    def __call__(self, state: ValidateOTPAssistant, config: RunnableConfig):
        result = self.runnable.invoke(state, config)
        return {"messages": result}

def otp_assistant():
    system_prompt = open('/home/ubuntu/VoicingAI-pingone/SYSTEM PROMPTS/otp/otp_v1.txt').read()
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"""{system_prompt}"""),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_llm()
    chain = primary_assistant_prompt | llm.bind_tools(otp_agent_tools)

    graph_builder = StateGraph(ValidateOTPAssistant)
    graph_builder.add_node("otp_agent", Assistant(chain))
    graph_builder.add_node("update_valid", update_valid)
    graph_builder.add_node("tools", ToolNode(otp_agent_tools))

    graph_builder.add_edge(START,"otp_agent")
    graph_builder.add_conditional_edges("otp_agent",route_model_output)
    graph_builder.add_edge("tools", "update_valid")
    graph_builder.add_edge("update_valid", 'otp_agent')
    graph_builder.add_edge("otp_agent", END)

    return graph_builder