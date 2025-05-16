from typing import List
from azure_ai_search import search_documents
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from state import Quiz

@tool
def search_course_documents_tool(query:str):
    """
    Gets Informations from courses content. and it is used by the teacher agent to search for course documents for the quiz preparation.
    """
    output = search_documents(query)
    return output

class quiz_preparation_tool(BaseModel):
    """
    Gives the topics and points that quiz should cover.
    """
    quiz_covered_topics: List[str] = Field(description="the topics the quiz will cover")
    theory_study_material: str = Field(description="theory study material used to prepare the quiz's questions")
    
class quiz_history_save_tool(BaseModel):
    """
    saves quiz in quiz history.
    """
    quiz_history:List[Quiz] = Field(description="Quiz history")

class teacher_understanding_tool(BaseModel):
    """
    Used only when is needed extra informations.
    """
    clarifying_question: str = Field(description="Teacher's clarifying question")