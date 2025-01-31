from typing import Any, Dict, Literal
from langchain_core.prompts import ChatPromptTemplate
from agent.state import ValidateSecurityQuestionsAssistant 
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import StateGraph, START, END
from agent.tools import securityqa_agent_tools
from agent.assistant import get_llm
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode


def route_model_output(state: ValidateSecurityQuestionsAssistant) -> Literal["tools", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    
    return END

def update_valid(state: ValidateSecurityQuestionsAssistant):
    messages = state['messages']
    last_message = messages[-1]
    if isinstance(last_message, ToolMessage):
        if last_message.name == 'verify_security_question':
            if last_message.content == "Answer Valid":
                state["valid_qa"] = True
                if "security_attempt" in state:
                    state["security_attempt"] += 1
                else:
                    state["security_attempt"] = 1
            else:
                if "security_attempt" in state:
                    state["security_attempt"] += 1
                else:
                    state["security_attempt"] = 1
        
    return state

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
    
    def __call__(self, state: ValidateSecurityQuestionsAssistant, config: RunnableConfig):
        result = self.runnable.invoke(state, config)
        return {"messages": result}

def security_assistant():
    system_prompt = open('SYSTEM PROMPTS/qa.txt').read()
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"""{system_prompt}"""),
            ("placeholder", "{messages}"),
        ]
    )

    llm = get_llm()
    chain = primary_assistant_prompt | llm.bind_tools(securityqa_agent_tools)

    graph_builder = StateGraph(ValidateSecurityQuestionsAssistant)
    graph_builder.add_node("qa_agent", Assistant(chain))
    graph_builder.add_node("update_valid", update_valid)
    graph_builder.add_node("tools", ToolNode(securityqa_agent_tools))

    graph_builder.add_edge(START,"qa_agent")
    graph_builder.add_conditional_edges("qa_agent",route_model_output)
    graph_builder.add_edge("tools", "update_valid")
    graph_builder.add_edge("update_valid", 'qa_agent')
    graph_builder.add_edge("qa_agent", END)

    return graph_builder