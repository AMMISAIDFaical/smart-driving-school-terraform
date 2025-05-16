from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
    VectorSearchVectorizer,
    AzureOpenAIVectorizer,
    VectorSearchAlgorithmKind,
    BM25SimilarityAlgorithm
)
from azure.core.credentials import AzureKeyCredential
import os
# from dotenv import load_dotenv uncomment this line if you are using .env file

# Load environment variables
load_dotenv(override=True)

search_endpoint = os.getenv("SEARCH_SERVICE_ENDPOINT")
search_api_key = os.getenv("SEARCH_SERVICE_KEY")
index_name = "another-index-name"  # Replace with your index name

credential = AzureKeyCredential(search_api_key)
index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

# Define fields
fields = [
    SimpleField(
        name="chunk_id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=False,
        sortable=True,
        facetable=False,
        retrievable=True,
        stored=True
    ),
    SimpleField(
        name="parent_id",
        type=SearchFieldDataType.String,
        filterable=True,
        retrievable=True,
        stored=True
    ),
    SearchableField(
        name="chunk",
        type=SearchFieldDataType.String,
        retrievable=True,
        stored=True
    ),
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        retrievable=True,
        stored=True
    ),
    SearchableField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        retrievable=True,
        stored=True,
        dimensions=1536,
        vector_search_profile="vector-index-azureOpenAi-text-profile"
    )
]

# Define semantic configuration
semantic_config = SemanticConfiguration(
    name="vector-index-semantic-configuration",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        prioritized_content_fields=[SemanticField(field_name="chunk")]
    )
)

# Define vector search components
vector_search = VectorSearch(
    algorithms=[
        VectorSearchAlgorithmConfiguration(
            name="vector-index-algorithm",
            kind=VectorSearchAlgorithmKind.HNSW,
            hnsw_parameters={
                "metric": "cosine",
                "m": 4,
                "efConstruction": 400,
                "efSearch": 500
            }
        )
    ],
  
)

# Create the search index=
index = SearchIndex(name=index_name, fields=fields, suggesters=[], scoring_profiles=[])
result = index_client.create_or_update_index(index)
print(f' {result.name} created')

# Create or update the index
result = index_client.create_or_update_index(index)
print(f"{result.name} created successfully.")
