from langchain_core.tools import tool
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.logger import get_logger

# Setup Logger
_logs = get_logger(__name__)
# Load environment variables
load_dotenv()
load_dotenv(".secrets")

client = OpenAI()
MCP_URL = os.getenv("MCP_URL")

@tool
def rag_mcp(prompt: str, n: int = 5) -> str:
    """
    Retrieve chunks of Securities and Exchange Commission EDGAR database 6-K documents relevant to the query.
    Uses the MCP server to search the ChromaDB collection.
    
    Args:
        prompt: The search query
        n: Number of results to return (default: 5)
    
    Returns:
        Search results containing chunks of documents, distances, and metadata
    """
    _logs.debug(f'Connecting to MCP to process query {prompt} and retrieve {n} closer results')
    
    tools = [{
        "type": "mcp",
        "server_label": "edgar_service",
        "server_description": "EDGAR 6-K Mexican organizations repository server",
        "server_url": MCP_URL,
        "require_approval": "never",
    }]
    
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            tools=tools,
            instructions=f"You must use the rag_mcp tool to search. Call it with prompt='{prompt}' and n={n}",
            input=f"Search for: {prompt}",
        )
        _logs.debug(f'Received response from MCP')
        return resp.output_text
    except Exception as e:
        _logs.error(f"Error: {e}")
        return f"Error calling MCP: {e}"