import os
import logging
from typing import Optional
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
    SearchIndex,
    SearchIndexerDataContainer
)
from azure.identity import DefaultAzureCredential

# -------------------------
# Logging Setup
# -------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------
# Environment Variables
# -------------------------
load_dotenv(override=True)

service_endpoint = os.environ["SEARCH_SERVICE_ENDPOINT"]
key = os.environ["SEARCH_SERVICE_KEY"]
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
azure_openai_model_name = os.getenv("AZURE_OPENAI_MODEL_NAME", "text-embedding-ada-002")

# These can be customized via env for CI/CD flexibility
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "drvschoolcontainer")
DATASOURCE_NAME = os.getenv("DATASOURCE_NAME")
INDEX_NAME = os.getenv("SEARCH_SERVICE_INDEX_NAME")

credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY")) if os.getenv("AZURE_SEARCH_ADMIN_KEY") else DefaultAzureCredential()
# -------------------------
# Azure AI Search Functions
# -------------------------

def create_index() -> SearchIndex:

    # Create a search index  
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
 
    fields = [  
        SearchField(name="parent_id", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),  
        SearchField(name="title", type=SearchFieldDataType.String),  
        SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
        SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
        SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),  
    ]
    
    vector_search = VectorSearch(  
        algorithms=[  
            HnswAlgorithmConfiguration(name="myHnsw"),
        ],  
        profiles=[  
            VectorSearchProfile(  
                name="myHnswProfile",  
                algorithm_configuration_name="myHnsw",  
                vectorizer_name="myOpenAI",  
            )
        ],  
        vectorizers=[  
            AzureOpenAIVectorizer(  
                vectorizer_name="myOpenAI",  
                kind="azureOpenAI",  
                parameters=AzureOpenAIVectorizerParameters(  
                    resource_url="https://drvl.openai.azure.com/", 
                    deployment_name=azure_openai_embedding_deployment,
                    model_name=azure_openai_model_name,
                    api_key=azure_openai_key,
                ),
            ),  
        ],  
    )  

    semantic_config = SemanticConfiguration(  
        name="my-semantic-config",  
        prioritized_fields=SemanticPrioritizedFields(  
            content_fields=[SemanticField(field_name="chunk")],
            title_field=SemanticField(field_name="title")
        ),  
    )
    
    # Create the semantic search with the configuration  
    semantic_search = SemanticSearch(configurations=[semantic_config])  
    
    # Create the search index
    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search, semantic_search=semantic_search)  
    result = index_client.create_or_update_index(index)  
    print(f"{result.name} created")
    logger.info(f"Index '{INDEX_NAME}' created successfully.")
    return result

def create_datasource() -> SearchIndexerDataSourceConnection:
    """Create (or reuse) an Azure Cognitive Search data source for Blob Storage."""
    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    container = SearchIndexerDataContainer(name=CONTAINER_NAME)

    datasource = SearchIndexerDataSourceConnection(
        name=DATASOURCE_NAME,
        type="azureblob",
        connection_string=connection_string,
        container=container
    )

    try:
        created_ds = indexer_client.create_data_source_connection(datasource)
        logger.info(f"Data source '{DATASOURCE_NAME}' created successfully.")
        return created_ds
    except HttpResponseError as e:
        if e.status_code == 409:
            logger.warning(f"Data source '{DATASOURCE_NAME}' already exists. Fetching existing connection.")
            return indexer_client.get_data_source_connection(DATASOURCE_NAME)
        else:
            logger.exception("Failed to create or retrieve data source.")
            raise



datasource = create_datasource()
index = create_index()