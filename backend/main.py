from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv(override=True)

from .state.research_state import ResearchState
from .core.get_llm import get_llm
from .core.tools import calculator, arxiv_search, tavily_search, read_arxiv_pdf



app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


llm = get_llm()

tools = [tavily_search, calculator, arxiv_search, read_arxiv_pdf]
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
    """Combine all findings into a coherent report with citations"""
    findings_text = "\n".join(state.get("findings", [])) if state.get("findings") else "No findings available."
    sources = state.get("sources", [])
    
    sources_text = ""
    for idx, source in enumerate(sources, 1):
        if isinstance(source, dict):
            title = source.get("title", "Unknown")
            url = source.get("url", "")
            authors = source.get("authors", [])
            sources_text += f"[{idx}] {title}\n"
            if authors:
                sources_text += f"    Authors: {', '.join(authors[:3])}"
                if len(authors) > 3:
                    sources_text += " et al."
                sources_text += "\n"
            if url:
                sources_text += f"    URL: {url}\n"
            sources_text += "\n"
    
    system_prompt = """You are an expert research synthesizer. Create a well-structured research report based on the findings.

    Your report must follow this structure:

    ## Executive Summary
    Brief overview of the research topic and key takeaways (2-3 sentences)

    ## Key Findings
    Main findings organized by themes or categories. Use inline citations like [1], [2] to reference sources.

    ## Conclusion
    Summary of the research and any implications or future directions

    ## References
    List all sources cited in the report

    Guidelines:
    - Be clear and concise
    - Use inline citations [1], [2] when referencing specific sources
    - Remove duplicate information
    - Organize findings logically
    - Maintain academic tone
    - If sources are provided, use the reference numbers provided"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Research Topic: {state.get('research_topic', 'Unknown')}

    Available Sources:
    {sources_text if sources_text else "No sources available."}

    Findings:
    {findings_text}""")
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
        - read_arxiv_pdf: Download and read the full text of an arXiv paper

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




@app.post("/export")
def export_report(data: dict):
    """Export research report as Markdown file"""
    
    topic = data.get("topic", "Research Report")
    response = data.get("response", "")
    sources = data.get("sources", [])
    findings = data.get("findings", [])
    
    # Build Markdown
    markdown = f"""# Research Report: {topic}

                Generated by AI Research Assistant

                ---

                ## Summary

                {response}

                ---

                ## Key Findings

            """
    
    # Add findings
    for idx, finding in enumerate(findings, 1):
        markdown += f"{idx}. {finding}\n\n"
    
    # Add sources
    if sources:
        markdown += "## Sources\n\n"
        for idx, source in enumerate(sources, 1):
            if isinstance(source, dict):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                authors = source.get("authors", [])
                author_str = ", ".join(authors) if authors else "Unknown"
                
                markdown += f"{idx}. **{title}**\n"
                markdown += f"   - Authors: {author_str}\n"
                if url:
                    markdown += f"   - URL: {url}\n"
                markdown += "\n"
    
    markdown += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d')}*"
    
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="research_report_{topic.replace(" ", "_")}.md"'}
    )