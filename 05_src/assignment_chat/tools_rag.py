from langchain.tools import tool
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from utils.logger import get_logger
import os

# Setup Logger
_logs = get_logger(__name__)
# Load environment variables and secrets
load_dotenv()
load_dotenv(".secrets")

# Connect to database
persist_directory="./assignment_chat/chromadb"
chroma_client = chromadb.PersistentClient(path=persist_directory)

# Initialize the same embedding function you used when creating the collection
embedding_function = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
collection_name="my_collection"
# Get the existing collection
collection = chroma_client.get_collection(
    name=collection_name,
    embedding_function=embedding_function
)


@tool
def rag(prompt:str, n:int=5):  # collection:chromadb.api.models.Collection,
    """
    Search a persistent ChromaDB collection for chunks of documents similar to the query.
    
    Args:
        prompt (str): The search query
        n (int): Number of results to return (default: 5)
        collection_name (str): Name of the collection (default: "my_collection")
    
    Returns:
        dict: Search results containing chunks of documents, distances, and metadata
    """
    results = collection.query(
        query_texts=[prompt],
        n_results=n
    )    
    return results