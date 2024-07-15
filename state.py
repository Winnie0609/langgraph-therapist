from typing import Sequence, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator


class Message(TypedDict):
    speaker: str
    message: str


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    # conversation: List[Message]
    current_stage: str
    selected_technique: str
    suggestion: str
    suggestion_reply: str
    is_suitable: bool
    feedback: str
    reply: str


state = {
    "messages": [],
    "next": None,
    # "conversation": [],
    "current_stage": None,
    "selected_technique": None,
    "suggestion": None,
    "suggestion_reply": None,
    "is_suitable": None,
    "feedback": None,
    "reply": None,
}
