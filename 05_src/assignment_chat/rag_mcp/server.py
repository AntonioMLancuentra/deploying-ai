from fastmcp import FastMCP
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from dotenv import load_dotenv
import os

from utils.logger import get_logger

# Load environment variables and secrets
load_dotenv()
load_dotenv(".secrets")

# Setup Logger
_logs = get_logger(__name__)


MCP_DOMAIN = os.getenv("MCP_DOMAIN")

# Connect to database
persist_directory="./assignment_chat/chromadb"
chroma_client = chromadb.PersistentClient(path=persist_directory)

# Initialize the same embedding function you used when creating the collection
embedding_function = OpenAIEmbeddingFunction(
    #api_key=os.getenv("OPENAI_API_KEY"),
    api_key_env_var="OPENAI_API_KEY",   # To avoid DeprecationWarning: Please use environment variables via api_key_env_var for persistent storage.
    model_name="text-embedding-3-small"
)
collection_name="my_collection"
# Get the existing collection
collection = chroma_client.get_collection(
    name=collection_name,
    embedding_function=embedding_function
)

# Initialize MCP Server
mcp = FastMCP(
    name="EDGAR 6-K Mexican organizations repository server",
    instructions="""
    This server provides 6-K filings submitted by Mexican organizations to EDGAR in SEC.
    """
)


@mcp.tool(
        name="mcp_rag",
        description="Retrieve chunks of Securities and Exchange Commission EDGAR database 6-K documents relevants to the query.",


)
def mcp_rag(prompt:str, n:int=5): # collection:dict=collection_name  # With it: AttributeError: 'str' object has no attribute 'query'
    """
    Search a persistent ChromaDB collection for chunks of documents similar to the query.
    
    Args:
        prompt (str): The search query
        n (int): Number of results to return (default: 5)
        collection_name (str): Name of the collection (default: "my_collection")
    
    Returns:
        dict: Search results containing chunks of documents, distances, and metadata
    """
    _logs.debug(f'Processing query {prompt} and retrieving {n} closer results')
    results = collection.query(
        query_texts=[prompt],
        n_results=n
    )    
    return results


if __name__ == "__main__":
    # listener = ngrok.forward(3000, authtoken=os.getenv("NGROK_AUTHTOKEN"),
    #                             domain=os.getenv("MCP_DOMAIN"))
    #_logs.info(f'Ngrok tunnel established at {listener.url()}')
    mcp.run(
        transport="http",
        host="localhost", 
        port=3000, 
    )
