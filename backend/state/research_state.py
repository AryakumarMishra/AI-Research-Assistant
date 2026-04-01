from typing import TypedDict, List, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ResearchState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    context: List[str]
    research_topic: str
    search_results: List[dict]
    sources: List[dict]
    findings: List[str]
    iteration: int