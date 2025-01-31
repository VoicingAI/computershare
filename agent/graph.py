from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.graph import StateGraph, START, END
from agent.state import AssistantGraphState, VerifyEmailAssistant, ValidateOTPAssistant, ValidateSecurityQuestionsAssistant
from agent.email_agent import email_assistant
from agent.otp_agent import otp_assistant
from agent.securityqa_agent import security_assistant
from agent.safe_agent import safe_assistant
from typing import Literal

def route_subgraph(state: VerifyEmailAssistant) -> Literal["email_assistant","safe_assistant","otp_assistant","security_assistant", END]:
    if len(state['messages']) <= 1:
        return "email_assistant"
    else:
        if 'valid_email' in state and state['valid_email'] == True:
            if 'valid_qa' in state and state["valid_qa"] == True:
                if 'valid_otp' in state and state['valid_otp'] == True:
                    return "safe_assistant"
                else:
                    return "otp_assistant"
            else:
                return "security_assistant"
        else:
            return "email_assistant"
        
def email_verify(state: VerifyEmailAssistant) -> Literal["security_assistant", END]:
    if 'valid_email' in state and state['valid_email'] == True:
        return "security_assistant"
    else:
        return END
    
def security_qa_verify(state: ValidateSecurityQuestionsAssistant) -> Literal["otp_assistant", END]:
    if 'valid_qa' in state and state["valid_qa"] == True:
        return "otp_assistant"
    else:
        return END
    
def otp_verify(state: ValidateOTPAssistant) -> Literal["safe_assistant", END]:
    if 'valid_otp' in state and state['valid_otp'] == True:
        return "safe_assistant"
    else:
        return END

memory = MemorySaver()

def compile_langgraph_workflow():

    email_assistant_agent = email_assistant().compile()
    otp_assistant_agent = otp_assistant().compile()
    security_assistant_agent = security_assistant().compile()
    safe_assistant_agent = safe_assistant().compile()

    email_assistant_agent.get_graph().draw_mermaid_png(output_file_path="email_graph.png")
    security_assistant_agent.get_graph().draw_mermaid_png(output_file_path="security_graph.png")
    otp_assistant_agent.get_graph().draw_mermaid_png(output_file_path="otp_graph.png")

    workflow = StateGraph(AssistantGraphState)
    # Define Nodes
    workflow.add_node('email_assistant', email_assistant_agent)
    workflow.add_node('otp_assistant', otp_assistant_agent)
    workflow.add_node('security_assistant', security_assistant_agent)
    workflow.add_node('safe_assistant', safe_assistant_agent)

    workflow.add_conditional_edges(START, route_subgraph)
    workflow.add_conditional_edges('email_assistant', email_verify)
    workflow.add_conditional_edges('security_assistant', security_qa_verify)
    workflow.add_conditional_edges('otp_assistant', otp_verify)
    workflow.add_edge('safe_assistant', END)

    # Compile the Graph
    graph = workflow.compile(checkpointer=memory)

    # Visualize the Graph
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

    return graph
