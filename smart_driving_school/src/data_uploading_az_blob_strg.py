from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
# from dotenv import load_dotenv uncomment this line if you are using .env file

# Load environment variables
load_dotenv(override=True)

# Configuration
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING") # Replace with your Azure Storage connection string
container_name = "your-container-name"  # Replace with your container name
local_folder = "/workspaces/python-ai-agent-frameworks-demos/smart_driving_school/data"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Optional: Create container if it doesn't exist
try:
    container_client.create_container()
except Exception as e:
    print("Container may already exist:", e)

# Upload PDF files
for filename in os.listdir(local_folder):
    if filename.endswith(".pdf"):
        file_path = os.path.join(local_folder, filename)
        blob_client = container_client.get_blob_client(filename)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded: {filename}")
