from typing import Annotated, Dict, List
from pydantic import BaseModel, Field
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

class Quiz(BaseModel):
    id: str = Field(None, description="Quiz ID")
    topic: str = Field(None, description="Topic to be quized")
    question: str = Field(None, description="Questions to be asked")
    user_answer: str = Field(None, description="User answer to be given")
    hint: str = Field(None, description="Hints to be given")
    explanation: str = Field(None, description="Explanation to be given")
    feedback: str = Field(None, description="Feedback to be given")
    mutliple_choices: List[str] = Field(None, description="Multiple choices for the user the choose from")

class QuizList(BaseModel):
    list_of_quiz: List[Quiz] = Field(None, description="List of quiz to be asked")

# Graph state
class State(TypedDict):
    # modified by the teacher agent
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # modified by the quiz agent
    quiz_topics: List[str] # {topic}
    # modified by the readiness agent
    sender: str # {teacher_agent, quiz_agent}
    # modified by the quiz agent
    quiz_study_material: str # {theory study material}
    # is asking for quiz
    is_asking_for_quiz: bool # {True, False}
    user_gave_answer: bool # {True, False}
    question_answer:List[Dict[str,str]] # {question, answer}
    quiz_completed: bool # {True, False}
    quiz_history: List[Quiz] # {quiz history}