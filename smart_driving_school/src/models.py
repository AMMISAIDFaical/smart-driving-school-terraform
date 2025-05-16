import os
from langchain_openai import ChatOpenAI
import os

API_HOST = os.getenv("API_HOST", "github")

def load_model():
    
    model = ChatOpenAI(
        model="gpt-4o-mini", base_url="https://models.inference.ai.azure.com", api_key=os.environ["GITHUB_TOKEN"]
    )
    return model

def main():
    model = load_model()
    result = model.invoke("hello")
    print(result)
if __name__ == "__main__":
    main()