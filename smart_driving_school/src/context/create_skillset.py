from azure.search.documents.indexes.models import (
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    OcrSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    )
from dotenv import load_dotenv
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
load_dotenv(override=True)

INDEX_NAME = os.getenv("INDEX_NAME", "drvschoollessons-index")
endpoint = os.environ["SEARCH_SERVICE_ENDPOINT"]
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
azure_openai_model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
# Create a skillset name 
skillset_name = f"{INDEX_NAME}-skillset"
credential = AzureKeyCredential(os.getenv("SEARCH_SERVICE_KEY"))

def create_skillset():
    split_skill = SplitSkill( 
        odata_type="#Microsoft.Skills.Text.SplitSkill",
        name= skillset_name,
        description="Split skill to chunk documents",  
        text_split_mode="pages",  
        context="/document",  
        maximum_page_length=2000,  
        page_overlap_length=500,  
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/content"),  
        ],
        outputs=[  
            OutputFieldMappingEntry(name="textItems", target_name="pages")  
        ]
    )

    embedding_skill = AzureOpenAIEmbeddingSkill(  
        description="Skill to generate embeddings via Azure OpenAI",  
        context="/document/pages/*",  
        resource_url="https://drvl.openai.azure.com/",  
        deployment_name=azure_openai_embedding_deployment,  
        model_name=azure_openai_model_name,
        dimensions=1536,
        api_key=azure_openai_key,  
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/pages/*"),  
        ],  
        outputs=[
            OutputFieldMappingEntry(name="embedding", target_name="vector")  
        ]
    )

    index_projections = SearchIndexerIndexProjection(  
        selectors=[  
            SearchIndexerIndexProjectionSelector(
                target_index_name=INDEX_NAME,  
                parent_key_field_name="parent_id",  
                source_context="/document/pages/*",  
                mappings=[
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
                    InputFieldMappingEntry(name="vector", source="/document/pages/*/vector"),
                    InputFieldMappingEntry(name="title", source="/document/metadata_storage_name")
                ]
            )
        ],  
        parameters=SearchIndexerIndexProjectionsParameters(  
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
        )  
    )

    skills = [embedding_skill, split_skill,index_projections]

    return SearchIndexerSkillset(  
        name=skillset_name,  
        description="Skillset to chunk documents and generating embeddings",  
        skills=skills,  
        index_projection=index_projections
    )

skillset = create_skillset()
  
client = SearchIndexerClient(endpoint, credential)  
client.create_or_update_skillset(skillset)  
print(f"{skillset.name} created")  
