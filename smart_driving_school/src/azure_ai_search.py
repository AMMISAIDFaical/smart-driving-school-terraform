import os
import logging
from typing import List, Dict

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_openai import AzureOpenAIEmbeddings

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
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")

if not all([SEARCH_SERVICE_ENDPOINT, SEARCH_SERVICE_INDEX_NAME, SEARCH_SERVICE_KEY]):
    logger.error("Missing one or more required Azure Search environment variables.")
    raise ValueError("Environment configuration incomplete.")

# --------------------------
# Azure Credentials
# --------------------------
credential = AzureKeyCredential(SEARCH_SERVICE_KEY)

# --------------------------
# Embedding Utilities
# --------------------------
def create_embeddings() -> AzureOpenAIEmbeddings:
    return AzureOpenAIEmbeddings(
        openai_api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_type="azure",
        azure_deployment=AZURE_DEPLOYMENT,
        model=AZURE_DEPLOYMENT,
        chunk_size=1,
    )

def get_embedding(text: str) -> List[float]:
    embeddings = create_embeddings()
    return embeddings.embed_query(text)

# --------------------------
# Search Function
# --------------------------
def search_documents(search_query: str, use_vector: bool = False) -> List[Dict[str, str]]:
    """
    Search documents in Azure AI Search.
    :param search_query: The user query string
    :param use_vector: Whether to use vector search or traditional full-text search
    """
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=SEARCH_SERVICE_INDEX_NAME,
        credential=credential
    )
    search_vector = get_embedding(search_query)

    try:
        results = search_client.search(
                search_text=search_query,
                top=5,

            )

        output = []
        for doc in results:
            chunk = doc.get("content", "")[:200].replace("\n", " ")
            score = round(doc.get("@search.score", 0), 5)
            output.append({
                "score": score,
                "content": chunk
            })

        return output

    except Exception as e:
        logger.exception("Error while searching documents")
        return []

# --------------------------
# Main Entrypoint
# --------------------------
def main() -> None:
    query = "alcohol and driving"
    logger.info(f" Searching for: '{query}'")
    results = search_documents(query, use_vector=False)  # Set to True if using vector search
    for res in results:
        logger.info(f"[Score: {res['score']}] {res['content']}")

if __name__ == "__main__":
    main()