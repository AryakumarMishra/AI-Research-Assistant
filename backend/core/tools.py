import os
from langchain_core.tools import tool
import arxiv
from typing import Union
from tavily import TavilyClient
from io import BytesIO
from pypdf import PdfReader
import requests
from dotenv import load_dotenv

load_dotenv(override=True)



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


# Internet Search tool
@tool
def tavily_search(query: str, max_results: int = 5) -> list:
    """
    Search the internet for the given query using Tavily.
    """
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query=query, max_results=max_results)

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "source": item.get("source", "web")
            })

        return results
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



# Arxiv Paper Download Tool
@tool
def read_arxiv_pdf(url: str) -> dict:
    """
    Download and read an arXiv paper.
    Returns the extracted text content.
    """
    try:
        # Convert arXiv URL to PDF URL
        if "arxiv.org/abs/" in url:
            pdf_url = url.replace("/abs/", "/pdf/") + ".pdf"
        elif "arxiv.org/pdf/" in url:
            pdf_url = url
        else:
            return {"error": "Not an arXiv URL. Use arxiv.org/abs/ or arxiv.org/pdf/ URLs"}
        
        # downloading the paper
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()

        # extracting text
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""

        # reading first 3 pages
        for page in reader.pages[:3]:
            text += page.extract_text() + "\n"

        
        if len(text) > 8000:
            text = text[:8000] + "... (truncated)"
            

        return {"content": text}
    except Exception as e:
        return {"error": str(e)}