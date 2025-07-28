from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Configuration
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("CONTAINER_NAME")
local_folder = "/workspaces/smart-driving-school-project/smart_driving_school/data"

# Check environment variables
if not connection_string or not container_name:
    raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING or CONTAINER_NAME in environment variables")

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Create container if it doesn't exist
try:
    container_client.create_container()
    print(f"Created container: {container_name}")
except ResourceExistsError:
    print(f"Container already exists: {container_name}")

# Upload PDF files
for filename in os.listdir(local_folder):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(local_folder, filename)
        blob_client = container_client.get_blob_client(filename)

        try:
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type='application/pdf')
                )
            print(f"Uploaded: {filename}")
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")