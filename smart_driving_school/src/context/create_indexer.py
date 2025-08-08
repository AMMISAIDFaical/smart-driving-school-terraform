from azure.search.documents.indexes.models import (
    SearchIndexer,
    IndexingParameters,
    IndexingParametersConfiguration
)
import os
import logging
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential

# -------------------------
# Logging Setup
# -------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------
# Environment Variables
# -------------------------
load_dotenv(override=True)

SEARCH_SERVICE_ENDPOINT = os.environ["SEARCH_SERVICE_ENDPOINT"]
SEARCH_SERVICE_KEY = os.environ["SEARCH_SERVICE_KEY"]
DATASOURCE_NAME = os.getenv("DATASOURCE_NAME")
INDEX_NAME = os.getenv("INDEX_NAME", "drvschoollessons-index")
indexer_name = f"{INDEX_NAME}-indexer"  

def create_indexer():

    indexer_parameters = IndexingParameters( 
        configuration=IndexingParametersConfiguration( allow_skillset_to_read_file_data=True, 
                                                                                           query_timeout=None)
                                                                                           )

    indexer = SearchIndexer(  
        name=indexer_name,  
        description="Indexer to index documents and generate embeddings",  
        skillset_name=f"{INDEX_NAME}-skillset",
        target_index_name=INDEX_NAME,
        data_source_name=DATASOURCE_NAME,
        parameters=indexer_parameters
    )  

    indexer_client = SearchIndexerClient(SEARCH_SERVICE_ENDPOINT, AzureKeyCredential(SEARCH_SERVICE_KEY))

    indexer_result = indexer_client.create_or_update_indexer(indexer)  
    
    # Run the indexer  
    indexer_client.run_indexer(indexer_name)  
    print(f' {indexer_name} is created and running. If queries return no results, please wait a bit and try again.')  
    return indexer_result

indexer_result = create_indexer()  # Call the function to create the indexer