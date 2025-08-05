import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from typing import List, Dict

# Load environment variables
load_dotenv(override=True)

# Azure Search + OpenAI Config
SEARCH_SERVICE_NAME = os.getenv("SEARCH_SERVICE_NAME")
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
SEARCH_SERVICE_INDEX_NAME = os.getenv("SEARCH_SERVICE_INDEX_NAME")
SEARCH_SERVICE_KEY = os.getenv("SEARCH_SERVICE_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Azure credentials
credential = AzureKeyCredential(SEARCH_SERVICE_KEY)

# Azure AI Search headers
HEADERS = {
    'Content-Type': 'application/json',
    'api-key': SEARCH_SERVICE_KEY
}

# === Embedding and LLM ===
def create_embeddings():
    return AzureOpenAIEmbeddings(
        openai_api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_type='azure',
        azure_deployment='text-embedding-ada-002',
        model="text-embedding-ada-002",
        chunk_size=1
    )

def get_embedding(text):
    embeddings = create_embeddings()
    return embeddings.embed_query(text)

def search_documents(search_query: str) -> List[Dict[str, str]]:
    """
    Search documents using indexed PDFs about driving lessons stored in Azure AI Search vector store.
    """
    search_client = SearchClient(SEARCH_SERVICE_ENDPOINT, SEARCH_SERVICE_INDEX_NAME, credential=credential)
    # search_vector = get_embedding(search_query)
    
    results = search_client.search(
        search_text=search_query,
        top=5,
        # vector_queries=[VectorizedQuery(vector=search_vector, k_nearest_neighbors=5, fields="text_vector")]
    )
    
    output = []
    for doc in results:
        chunk = doc["chunk"].replace("\n", " ")[:200]
        score = round(doc['@search.score'], 5)
        output.append({
            "score": score,
            "content": chunk
        })
    
    return output

def main():
    result = search_documents("alcahol and driving")
    print(result)
    
if __name__ == "__main__":
    main()