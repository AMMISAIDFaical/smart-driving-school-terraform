import os
import logging
from typing import Optional
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    CorsOptions,
    SearchIndex,
    InputFieldMappingEntry
)

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

# These can be customized via env for CI/CD flexibility
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "drvschoolcontainer")
DATASOURCE_NAME = os.getenv("DATASOURCE_NAME", "drvschool-datasource")
INDEX_NAME = os.getenv("INDEX_NAME", "drvschoollessons-index")

# -------------------------
# Azure AI Search Functions
# -------------------------

def create_index() -> SearchIndex:
    """Create (or reuse) an Azure Cognitive Search index for PDF documents with key phrases."""
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, retrievable=True, key=True),
        SimpleField(name="metadata_storage_name", type=SearchFieldDataType.String, retrievable=True, filterable=True, sortable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String, retrievable=True, searchable=True),
        SearchableField(name="name", type=SearchFieldDataType.String, retrievable=True, searchable=True),
        SearchableField(name="category", type=SearchFieldDataType.String, retrievable=True, searchable=True, filterable=True),
        SearchableField(name="topic", type=SearchFieldDataType.String, retrievable=True, searchable=True, filterable=True),
        SimpleField(name="metadata_storage_path", type=SearchFieldDataType.String),
        SimpleField(name="keyPhrases", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True, retrievable=True, filterable=True, facetable=True),
        SimpleField(name="mergedContent", type=SearchFieldDataType.String, searchable=True, retrievable=True),
    #     SearchableField(
    #     name="text_vector",
    #     type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
    #     searchable=True,
    #     retrievable=True,
    #     stored=True,
    #     dimensions=1536,
    #     vector_search_profile="vector-index-azureOpenAi-text-profile"
    # )

    ]

    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    index = SearchIndex(name=INDEX_NAME, fields=fields, cors_options=cors_options)

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    try:
        created_index = index_client.create_index(index)
        logger.info(f"Index '{INDEX_NAME}' created successfully with key phrases field.")
        return created_index
    except HttpResponseError as e:
        if e.status_code == 409:
            logger.warning(f"⚠️ Index '{INDEX_NAME}' already exists. Fetching existing index.")
            return index_client.get_index(INDEX_NAME)
        else:
            logger.exception("❌ Failed to create or retrieve index.")
            raise

def create_datasource() -> SearchIndexerDataSourceConnection:
    """Create (or reuse) an Azure Cognitive Search data source for Blob Storage."""
    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    container = SearchIndexerDataContainer(name=BLOB_CONTAINER_NAME)

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
