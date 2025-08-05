import os
import datetime
from typing import Optional

from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndex,
    SearchIndexer,
    SimpleField,
    SearchFieldDataType,
    CorsOptions,
    IndexingSchedule,
    SearchableField,
    IndexingParameters,
    SearchIndexerDataSourceConnection,
    IndexingParametersConfiguration,
    FieldMapping,
)
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents import SearchClient
from azure.core.exceptions import HttpResponseError

# Load environment variables from .env file
load_dotenv(override=True)

service_endpoint = os.environ["SEARCH_SERVICE_ENDPOINT"]
key = os.environ["SEARCH_SERVICE_KEY"]
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

def _create_index():
    """Create an index suitable for PDF documents with extracted content and metadata"""
    name = "drvschoollessons-index"

    # Index fields for PDF documents - Azure Search automatically extracts these
    fields = [
        # Key field - required and must be unique
        SimpleField(name="id", type=SearchFieldDataType.String, retrievable=True, key=True),
        SimpleField(name="metadata_storage_name", type=SearchFieldDataType.String, retrievable=True, filterable=True, sortable=True, facetable=True),

        # Main searchable content from PDF
        SearchableField(name="content", type=SearchFieldDataType.String, 
                       retrievable=True, analyzer_name="standard.lucene"),
        # Custom fields for driving test content
        SearchableField(name="lessonName", type=SearchFieldDataType.String, 
                       retrievable=True, searchable=True),
        SimpleField(name="category", type=SearchFieldDataType.String, 
                   retrievable=True, filterable=True, facetable=True),
        SearchableField(name="topic", type=SearchFieldDataType.String, 
                       retrievable=True, searchable=True, filterable=True),
        SimpleField(name="metadata_storage_path", type=SearchFieldDataType.String),

    ]
    
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)

    # Create the index
    index = SearchIndex(name=name, fields=fields, cors_options=cors_options)
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    
    try:
        result = index_client.create_index(index)
        print(f"Index '{name}' created successfully")
        return result
    except HttpResponseError as e:
        if e.status_code == 409:  # Index already exists
            print(f"Index '{name}' already exists")
            return index_client.get_index(name)
        else:
            raise

def _create_datasource():
    """Create a data source connection to Azure Blob Storage"""
    ds_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    container = SearchIndexerDataContainer(name="drvschoolcontainer")
    
    data_source_connection = SearchIndexerDataSourceConnection(
        name="drvschool-datasource", 
        type="azureblob", 
        connection_string=connection_string, 
        container=container
    )
    
    try:
        data_source = ds_client.create_data_source_connection(data_source_connection)
        print("Data source created successfully")
        return data_source
    except HttpResponseError as e:
        if e.status_code == 409:  # Data source already exists
            print("Data source already exists")
            return ds_client.get_data_source_connection("drvschool-datasource")
        else:
            raise

def sample_indexer_workflow():
    """Main workflow to create and run the Azure AI Search indexer for PDFs"""
    
    try:
        # Create data source
        data_source_name = _create_datasource().name
        print(f"Data source: {data_source_name}")

        # Create index
        index_name = _create_index().name
        print(f"Index: {index_name}")
        # Configuration for PDF parsing
        indexer_name = "drvschool-indexer"
        
        indexer = SearchIndexer(
            name=indexer_name,
            description="Indexer for driving school content",
            data_source_name=data_source_name,
            target_index_name=index_name,
            parameters=IndexingParameters(configuration={"parsingMode": "default"})
        )

        indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
        
        try:
            indexer_result = indexer_client.create_indexer(indexer)
            print("Indexer created successfully")
        except HttpResponseError as e:
            if e.status_code == 409:  # Indexer already exists
                print("Indexer already exists, updating...")
                indexer_result = indexer_client.create_or_update_indexer(indexer)
            else:
                raise

        # Get the indexer
        result = indexer_client.get_indexer("drvschool-indexer")
        print(f"Indexer retrieved: {result.name}")

        # Run the indexer immediately
        print(" Running indexer...")
        indexer_client.run_indexer(result.name)
        print("Indexer is running... This may take several minutes for PDFs.")


    except Exception as e:
        print(f" Error occurred: {str(e)}")
        
        # Get more detailed error information
        if hasattr(e, 'response') and e.response:
            print(f"   Status code: {e.response.status_code}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
        
        raise

if __name__ == "__main__":
    # Run the main workflow
    sample_indexer_workflow()
    
