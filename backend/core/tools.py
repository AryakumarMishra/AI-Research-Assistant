from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import arxiv
from typing import Union



# Internet Search tool
duckduckgo_search = DuckDuckGoSearchRun(region="us-en")


# Calculator tool
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}



# ArXiv Paper Search tool
@tool
def arxiv_search(query: str, max_results: int = 5) -> Union[list, dict]:
    """
    Search for papers on arXiv using a keyword query.
    Returns a list of paper titles and IDs.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            papers.append({
                "title": result.title,
                "id": result.get_short_id(),
                "url": result.entry_id,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary[:200] + "..." if len(result.summary) > 200 else result.summary
            })
        
        return papers
    except Exception as e:
        return {"error": str(e)}