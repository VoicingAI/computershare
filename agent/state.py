from typing import Annotated, TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage


class VerifyEmailAssistant(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    valid_email: bool = False
    email_attempt: int = 0

class ValidateSecurityQuestionsAssistant(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    valid_qa: bool = False
    security_attempt: int = 0

class ValidateOTPAssistant(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    valid_otp: bool = False
    otp_attempt: int = 0

class AssistantGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    verified: bool = False
    valid_email: bool = False
    valid_qa: bool = False
    valid_otp: bool = False
