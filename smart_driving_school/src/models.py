import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


from dotenv import load_dotenv
load_dotenv(override=True)

API_HOST = os.getenv("API_HOST", "github")

def load_model():
    
    model = ChatOpenAI(
        model="gpt-4o-mini", base_url="https://models.inference.ai.azure.com", api_key=os.environ["GITHUB_TOKEN"]
    )
    return model

def load_embedding_model():
    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.environ["EMBEDDING_MODEL_KEY"])
    return embedding_model

def main():
    model = load_model()
    load_embedding_model = load_embedding_model()
    result = model.invoke("hello")
    print(result.content)
    
if __name__ == "__main__":
    main()