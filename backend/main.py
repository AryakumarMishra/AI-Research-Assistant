from fastapi import FastAPI
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import json

from sqlalchemy import exc

load_dotenv(override=True)

from .state.research_state import ResearchState
from .core.get_llm import get_llm
from .core.tools import calculator, arxiv_search, tavily_search



app = FastAPI()



llm = get_llm()

tools = [tavily_search, calculator, arxiv_search]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)


# Helper Functions
def has_tool_calls(state: ResearchState) -> bool:
    """Check if the last message contains tool calls"""
    if not state.get("messages"):
        return False
    last_msg = state["messages"][-1]
    return hasattr(last_msg, "tool_calls") and last_msg.tool_calls


def extract_findings(state: ResearchState):
    """Extract findings from the last message and update state"""
    if not state.get("messages"):
        return state
    
    last_msg = state["messages"][-1]
    
    if hasattr(last_msg, "content") and last_msg.content:
        if "findings" not in state:
            state["findings"] = []
        state["findings"].append(last_msg.content)


        if "sources" not in state:
            state["sources"] = []
        
        try:
            parsed = json.loads(last_msg.content)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "url" in item:
                        state["sources"].append({
                            "title": item.get("title", "Unknown"),
                            "url": item["url"],
                            "authors": item.get("authors", []),
                            "type": "arxiv" if "arxiv.org" in item["url"] else "web"
                        })
        
        except (json.JSONDecodeError, TypeError):
            pass
            
        
        current_iter = state.get("iteration", 0)
        state["iteration"] = current_iter + 1
    
    return state


# Router: Decide next step
def router(state: ResearchState):
    """Route to tools, synthesize, or end based on state"""
    if has_tool_calls(state):
        return "tools"
    
    if state.get("iteration", 0) >= 2 and state.get("findings"):
        return "synthesize"
    
    return END


# Node Functions
def extract_findings_node(state: ResearchState):
    """Node to extract findings after tool execution"""
    return extract_findings(state)


def synthesize_findings(state: ResearchState):
    """Combine all findings into a coherent report"""
    findings_text = "\n".join(state.get("findings", [])) if state.get("findings") else "No findings available."
    
    messages = [
        SystemMessage(content="You are a research synthesizer. Create a clear, concise report based on the findings. Include citations where available."),
        HumanMessage(content=f"Research Topic: {state.get('research_topic', 'Unknown')}\n\nFindings:\n{findings_text}")
    ]
    response = llm.invoke(messages)
    
    return {"messages": [AIMessage(content=response.content)]}


def chat_node(state: ResearchState):
    """LLM node that may answer or request tool calls"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}



# Defining the Graph
graph = StateGraph(ResearchState)
 
graph.add_node("chat", chat_node)
graph.add_node("tools", tool_node)
graph.add_node("extract", extract_findings_node)
graph.add_node("synthesize", synthesize_findings)
 
graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", router, {"tools": "tools", "synthesize": "synthesize", END: END})
graph.add_edge("tools", "extract")
graph.add_edge("extract", "chat")
graph.add_edge("synthesize", END)
 
workflow = graph.compile()




# API Endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(request: dict):
    user_message = request.get("message", "")
    
    system_message = SystemMessage(content="""You are a research assistant with access to these tools:
        - tavily_search: Search the web for current information
        - arxiv_search: Search academic papers on arXiv
        - calculator: Perform mathematical calculations

        Only use these exact tool names. Do not attempt to use any other tools.""")
    
    state = {
        "messages": [system_message, HumanMessage(content=user_message)],
        "context": [],
        "research_topic": user_message,
        "search_results": [],
        "sources": [],
        "findings": [],
        "iteration": 0
    }

    final_state = workflow.invoke(state)
    
    return {
        "response": final_state["messages"][-1].content,
        "sources": final_state.get("sources", []),
        "findings": final_state.get("findings", [])
    }
