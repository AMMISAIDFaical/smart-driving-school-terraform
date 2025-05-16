from typing import Literal
from state import QuizList, State, Quiz
from prompts import teacher_prompt, quiz_prompt
from model import load_model
from tools import (
    quiz_preparation_tool,
    search_course_documents_tool,
    teacher_understanding_tool,
)
from langgraph.types import interrupt, Command
from langchain_core.messages import AIMessage, HumanMessage


def teacher_agent(state: State):
    """
    it handles the following:
    - Detecting student(user) intent. 
    - ask clarifying questions if the user is not clear about the topic.
    - provide answers for his questions. 
    - prepares topics list, study material for the quiz agent so that it can construct a quiz. if the user is asked for the quiz.
    - gives final evaluation of the student.
    Args:
        state (State): The current dialogue and memory state, including messages and context.

    Returns:
        dict: shared state modified.
    """
    # getting list of messages
    messages = state.get("messages", [])
    quiz_history = state.get("quiz_history", [])
    quiz_completed = state.get("quiz_completed", False)
    # loading the model and binding the tools to it
    model = load_model()
    model = model.bind_tools([
        quiz_preparation_tool, # a tool gives the agent ability to prepare quiz topics and study material
        teacher_understanding_tool, # a tool gives the agent ability to ask clarifying questions
        search_course_documents_tool # a tool gives the agent ability to search course documents
    ])
    chain = teacher_prompt | model
    response = chain.invoke({
        "messages": messages,
        "quiz_history": quiz_history
    })

    # the response can be either a message or a tool call(s)
    for calls in response.tool_calls:
        # if the tool was teacher_understanding_tool means the agent decided to ask clarifying question
        # so we push the passed payload that holds the clarifying question to the list of messages
        if calls['name'] == "teacher_understanding_tool":
            return {
                "messages": calls['args']['clarifying_question'],
                "sender": "teacher_agent" # this used by the tool node to know which agent to call next
            }
        # if the tool was teacher_understanding_tool means the agent decided to prepare quiz topics and study material
        # so we push the passed payload that holds the quiz topics, study material to the varaibles in the state
        if calls['name'] == "quiz_preparation_tool":
            return {
                "quiz_topics": calls['args']['quiz_covered_topics'],
                "quiz_study_material": calls['args']['theory_study_material'],
                "sender": "teacher_agent",
                "is_asking_for_quiz": True
            }
        # if the tool was search_course_documents_tool means the agent decided to search course documents
        # so we push the passed payload that holds the search result to the list of messages
        else:
            return {
                "messages": response,
                "sender": "teacher_agent"
            }
    # if there is no tool calls means the agent decided to answer the user question
    return {
                "messages": response,
                "sender": "teacher_agent"
            }

def quiz_agent(state: State):
    """
    Generates quiz questions based on provided topics and study materials when the student is ready.

    Args:
        state (State): The current state including messages, quiz context, and quiz history.

    Returns:
        dict | None: A dictionary containing the AI-generated quiz message and the updated state, 
                     or None if no quiz is generated.
    """
    messages = state.get("messages", [])
    last_message = messages[-1]
    quiz_topics = state.get("quiz_topics", [])
    quiz_study_material = state.get("quiz_study_material", "")
    if quiz_topics == []:
        return {
            "messages": AIMessage(
                content="Quiz is finished.",
                name="quiz_agent"
            ),
            "quiz_topics": quiz_topics,  # Return updated list
            "quiz_completed": True,
            "is_asking_for_quiz":False
        }
    # Prepare model and chain
    model = load_model()
    model = model.with_structured_output(Quiz)
    chain = quiz_prompt | model

    response = chain.invoke({
        "quiz_topics": quiz_topics,
        "quiz_study_material": quiz_study_material
    })

    # Remove the first topic after generating the quiz
    used_topic = quiz_topics.pop(0)

    return {
        "messages": AIMessage(
            content=str(
                response.question + '\n' +
                response.hint + '\n' +
                str(response.mutliple_choices) + '\n'
            ),
            name="quiz_agent"
        ),
        "quiz_topics": quiz_topics  # Return updated list
    }


def student_input_node(state: State) -> Command[Literal["quiz_agent"]]:
    """
    Captures the student's latest input and wraps it in a `HumanMessage` to be processed by agents.

    Args:
        state (State): The current state containing the message history and context.

    Returns:
        Command[Literal["teacher_agent", "quiz_agent"]]: A command object with the human message, 
        used to route the response to the appropriate agent.
    """
    last_message = state.get("messages", [])[-1]
    value = interrupt({ "messages": last_message, "sender": "student_input_node" })

    return Command(update={"messages": HumanMessage(content=value, name="student"),"user_gave_answer": True}, goto="quiz_agent") 
