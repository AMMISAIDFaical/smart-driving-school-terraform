import os
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
import getpass
import os

API_HOST = os.getenv("API_HOST", "github")

def load_model():
    
    model = ChatOpenAI(
        model="gpt-4o-mini", base_url="https://models.inference.ai.azure.com", api_key=os.environ["GITHUB_TOKEN"]
    )
    return model

# def load_model():
    # model = ChatMistralAI(
    #         model="ministral-3b",
    #         temperature=0,
    #         max_retries=2,
    #         api_key=os.environ["GITHUB_TOKEN"],
    #         base_url="https://models.inference.ai.azure.com"
            
    #     )
    # return model
#just to test the models 
# def main():
#     model = ChatMistralAI(
#         model="ministral-3b",
#         temperature=0,
#         max_retries=2,
#         api_key=os.environ["GITHUB_TOKEN"],
#         base_url="https://models.inference.ai.azure.com"
        
#     )

# if __name__ == "__main__":
#     main()