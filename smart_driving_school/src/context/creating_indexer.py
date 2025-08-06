import logging
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer, 
    IndexingParameters,
    SearchIndexerSkillset,
    DocumentExtractionSkill,
    OcrSkill,
    MergeSkill,
    KeyPhraseExtractionSkill,  # Added for key phrase extraction
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    FieldMapping)

from dotenv import load_dotenv
from creating_index import create_datasource, create_index

# ---------------------------
# Configuration
# ---------------------------
load_dotenv(override=True)

# Environment variables
INDEXER_NAME = os.getenv("INDEXER_NAME", "drvschool-indexer")
SKILLSET_NAME = os.getenv("SKILLSET_NAME", "drvschool-skillset")
PARSING_MODE = os.getenv("PARSING_MODE", "default")
SEARCH_SERVICE_ENDPOINT = os.environ["SEARCH_SERVICE_ENDPOINT"]
SEARCH_SERVICE_KEY = os.environ["SEARCH_SERVICE_KEY"]
COGNITIVE_SERVICES_KEY = os.environ.get("COGNITIVE_SERVICES_KEY")

# ---------------------------
# Logger Setup
# ---------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def create_skillset():
    """
    Create a skillset for PDF processing with OCR and Key Phrase Extraction capabilities.
    """
    client = SearchIndexerClient(SEARCH_SERVICE_ENDPOINT, AzureKeyCredential(SEARCH_SERVICE_KEY))
    
    # Document Extraction - Extract text and images from PDFs
    doc_extraction_input = InputFieldMappingEntry(name="file_data", source="/document/file_data")
    doc_extraction_output1 = OutputFieldMappingEntry(name="content", target_name="extractedContent")
    doc_extraction_skill = DocumentExtractionSkill(
        name="document-extraction-skill",
        inputs=[doc_extraction_input], 
        outputs=[doc_extraction_output1]
    )
    
    # OCR Skill - Extract text from images within PDFs
    ocr_input = InputFieldMappingEntry(name="image", source="/document/normalized_images/*")
    ocr_output = OutputFieldMappingEntry(name="text", target_name="ocrText")
    ocr_skill = OcrSkill(
        name="ocr-skill",
        inputs=[ocr_input], 
        outputs=[ocr_output],
        default_language_code="en"
    )
    
    # Merge Skill - Combine extracted text and OCR text
    merge_input1 = InputFieldMappingEntry(name="text", source="/document/extractedContent")
    merge_input2 = InputFieldMappingEntry(name="itemsToInsert", source="/document/normalized_images/*/ocrText")
    merge_output = OutputFieldMappingEntry(name="mergedText", target_name="merged_content")
    merge_skill = MergeSkill(
        name="merge-skill",
        inputs=[merge_input1, merge_input2], 
        outputs=[merge_output],
        insertion_marker=" "
    )
    
    # Key Phrase Extraction - Extract key phrases from merged content
    keyphrases_input = InputFieldMappingEntry(name="text", source="/document/merged_content")
    keyphrases_output = OutputFieldMappingEntry(name="keyPhrases", target_name="keyPhrases")
    keyphrases_skill = KeyPhraseExtractionSkill(
        name="keyphrases-skill",
        inputs=[keyphrases_input],
        outputs=[keyphrases_output],
        default_language_code="en"
    )
    
    # Create skillset with all skills
    skillset = SearchIndexerSkillset(
        name=SKILLSET_NAME, 
        skills=[doc_extraction_skill, ocr_skill, merge_skill, keyphrases_skill], 
        description="Skillset for PDF content extraction, OCR, and key phrase extraction",
        cognitive_services_account={
            "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
            "key": COGNITIVE_SERVICES_KEY
        } if COGNITIVE_SERVICES_KEY else None
    )
    
    try:
        result = client.create_skillset(skillset)
        logger.info(f"Skillset '{SKILLSET_NAME}' created successfully.")
        return result
    except HttpResponseError as e:
        if e.status_code == 409:
            logger.warning(f"Skillset '{SKILLSET_NAME}' already exists. Updating...")
            result = client.create_or_update_skillset(skillset)
            logger.info(f"Skillset '{SKILLSET_NAME}' updated successfully.")
            return result
        else:
            raise

# ---------------------------
# Main Workflow
# ---------------------------

def run_indexer_workflow() -> None:
    """
    Main workflow to create and run the Azure AI Search indexer for PDFs with key phrase extraction.
    """
    try:
        indexer_client = SearchIndexerClient(SEARCH_SERVICE_ENDPOINT, AzureKeyCredential(SEARCH_SERVICE_KEY))
        
        # Create data source
        data_source = create_datasource()
        logger.info(f"Data source created: {data_source.name}")

        # Create index
        index = create_index()
        logger.info(f"Index created: {index.name}")

        # Create skillset with key phrase extraction
        skillset_result = create_skillset()

        # Create indexer with skillset
        indexer = SearchIndexer(
            name=INDEXER_NAME,
            description="Indexer for driving school content with AI enrichment and key phrase extraction",
            data_source_name=data_source.name,
            target_index_name=index.name,
            skillset_name=SKILLSET_NAME,
            parameters=IndexingParameters(
                configuration={
                    "parsingMode": PARSING_MODE,
                    "dataToExtract": "contentAndMetadata",
                    "imageAction": "generateNormalizedImages",
                    "allowSkillsetToReadFileData": True
                }
            ),
            # Map the key phrases output to the index using correct FieldMapping
            output_field_mappings=[
                FieldMapping(source_field_name="/document/keyPhrases", target_field_name="keyPhrases")
            ]
        )

        try:
            indexer_client.create_indexer(indexer)
            logger.info(f"Indexer '{INDEXER_NAME}' created successfully.")
        except HttpResponseError as e:
            if e.status_code == 409:
                logger.warning(f"Indexer '{INDEXER_NAME}' already exists. Updating...")
                indexer_client.create_or_update_indexer(indexer)
                logger.info(f"Indexer '{INDEXER_NAME}' updated successfully.")
            else:
                raise

        # Confirm indexer creation
        result = indexer_client.get_indexer(INDEXER_NAME)
        logger.info(f"Indexer retrieved: {result.name}")

        # Run indexer
        logger.info(f"Running indexer '{result.name}'...")
        indexer_client.run_indexer(result.name)
        logger.info("Indexer execution started with AI enrichment and key phrase extraction (may take several minutes for PDFs).")

    except HttpResponseError as http_err:
        logger.error(f"Azure HTTP error: {http_err.message}")
        if http_err.response:
            logger.error(f"   Status code: {http_err.response.status_code}")
            if hasattr(http_err.response, 'text'):
                logger.error(f"   Response: {http_err.response.text}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        raise

# ---------------------------
# Entrypoint
# ---------------------------

if __name__ == "__main__":
    run_indexer_workflow()