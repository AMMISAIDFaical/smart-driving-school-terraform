import os
import logging
from typing import List, Dict

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents.models import VectorizableTextQuery

# --------------------------
# Logging Setup
# --------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------
# Load Environment Variables
# --------------------------
load_dotenv(override=True)

SEARCH_SERVICE_NAME = os.getenv("SEARCH_SERVICE_NAME")
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
SEARCH_SERVICE_INDEX_NAME = os.getenv("SEARCH_SERVICE_INDEX_NAME")
SEARCH_SERVICE_KEY = os.getenv("SEARCH_SERVICE_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT", "text-embedding-ada-002")

if not all([SEARCH_SERVICE_ENDPOINT, SEARCH_SERVICE_INDEX_NAME, SEARCH_SERVICE_KEY]):
    logger.error("Missing one or more required Azure Search environment variables.")
    raise ValueError("Environment configuration incomplete.")

# --------------------------
# Azure Credentials
# --------------------------
credential = AzureKeyCredential(SEARCH_SERVICE_KEY)

# --------------------------
# Search Function
# --------------------------
def search_documents(search_query: str) -> List[Dict[str, str]]:
    """
    Search documents in Azure AI Search.
    :param search_query: The user query string
    """
    search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=SEARCH_SERVICE_INDEX_NAME, credential=credential)
    vector_query = VectorizableTextQuery(text=search_query, k_nearest_neighbors=1, fields="vector", exhaustive=True)
    
    results = search_client.search(  
        search_text=search_query,  
        vector_queries= [vector_query],
        select=["parent_id", "chunk_id", "chunk"],
        top=1
    )  
    
    for result in results:  
        print(f"parent_id: {result['parent_id']}")  
        print(f"chunk_id: {result['chunk_id']}")  
        print(f"Score: {result['@search.score']}")  
        print(f"Content: {result['chunk']}")  


# --------------------------
# Main Entrypoint
# --------------------------
def main() -> None:
    query = "alcohol and driving"
    logger.info(f" Searching for: '{query}'")
    results = search_documents(query)  # Set to True if using vector search
    for res in results:
        logger.info(f"[Score: {res['score']}] {res['content']}")

if __name__ == "__main__":
    main()
