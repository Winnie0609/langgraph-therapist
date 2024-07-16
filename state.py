from typing import Sequence, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator


class Message(TypedDict):
    speaker: str
    message: str


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    current_stage: str
    selected_intention: str
    selected_skill: str
    suggestion: str
    suggest_reply: str
    is_suitable: bool
    feedback: str
    reply: str


state = {
    "messages": [],
    "next": None,
    "current_stage": None,
    "selected_intention": None,
    "selected_skill": None,
    "suggestion": None,
    "suggest_reply": None,
    "is_suitable": None,
    "feedback": None,
    "reply": None,
}
