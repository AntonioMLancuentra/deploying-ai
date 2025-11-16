from langchain.tools import tool
from dotenv import load_dotenv
from utils.logger import get_logger
from langchain_tavily import TavilySearch
import os

# Setup Logger
_logs = get_logger(__name__)
# Load environment variables and secrets
load_dotenv()
load_dotenv(".secrets")
if not os.environ.get("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found in environment variables")



@tool
def web_search(query, max_results=3):
    """
    Perform a web search using Tavily.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 3)
    
    Returns:
        Search results from Tavily
    """
    _logs.debug(f'Searching the web for query "{query}" and asking for {max_results} results')
    search = TavilySearch(
        max_results=max_results,
        topic="finance",
        search_depth="basic",
        years=4,
        include_answer= True,
    )
    result = search.invoke({"query": query})
    _logs.debug(f'The result from the web search is "{result['answer']}".')
    return result