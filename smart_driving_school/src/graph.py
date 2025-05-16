from typing import Literal
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import  Command
from langchain_core.messages import HumanMessage

from tools import search_course_documents_tool
from ds_agents import teacher_agent, quiz_agent, student_input_node
from state import State

from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles



tools = [search_course_documents_tool]
tool_node = ToolNode(tools)


def should_continue(
    state: State
) -> Literal["call_tool", "quiz_agent", "__end__"]:
    """
    Determines the next step in the workflow based on the state after the teacher agent execution.

    Args:
        state (State): The current state of the workflow.

    Returns:
        Literal: The next node to transition to in the graph.
    """
    messages = state["messages"]
    is_asking_for_quiz = state.get("is_asking_for_quiz", False)
    last_message = messages[-1]
    quiz_topics = state.get("quiz_topics", [])
    quiz_completed = state.get("quiz_completed", False)

    if last_message.content == '' and last_message.tool_calls:
        return "call_tool"

    if is_asking_for_quiz:
        return "quiz_agent"
    
    if quiz_topics == [] and quiz_completed:
         return "__end__"
    
    return "__end__"


def worker_should_continue(state: State) -> Literal["teacher_agent", "student_input_node"]:
    """
    Determines whether the quiz agent should invoke tools or return control to the teacher/student.

    Args:
        state (State): The current workflow state.

    Returns:
        Literal: The next step in the graph workflow.
    """
    messages = state["messages"]
    last_message = messages[-1]
    quiz_completed = state.get("quiz_completed", False)
    quiz_topics = state.get("quiz_topics", [])
    
    if quiz_topics == [] and quiz_completed:
        return "teacher_agent"
    
    return "student_input_node"

workflow = StateGraph(State)

# Define nodes
workflow.add_node("teacher_agent", teacher_agent)
workflow.add_node("quiz_agent", quiz_agent)
workflow.add_node("tool_node", tool_node)
workflow.add_node("student_input_node", student_input_node)

# Start workflow
workflow.add_edge(START, "teacher_agent")

# Conditional transitions from teacher agent
workflow.add_conditional_edges(
    "teacher_agent",
    should_continue,
    {
        "quiz_agent": "quiz_agent",
        "call_tool": "tool_node",
        "__end__": END
    },
)

# Conditional transitions from quiz agent
workflow.add_conditional_edges(
    "quiz_agent",
    worker_should_continue,
    {
        "teacher_agent": "teacher_agent",
        "student_input_node": "student_input_node",
    }
)

workflow.add_edge("student_input_node", "quiz_agent")

# Conditional transitions from tool node
workflow.add_conditional_edges(
    "tool_node",
    lambda x: x["sender"],
    {
        "teacher_agent": "teacher_agent",
    }
)

def update_graph(graph,thread_config):
    graph.get_state(thread_config).values["messages"][-1].pretty_print()
    user_answer = input("provide your answer : ")
    graph.invoke(Command(resume=user_answer), config=thread_config)
    

def main():
    """
    Entry point for the interactive CLI application running the LangGraph workflow.
    """
    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

    # Initial user input
    user_input = input("Hello, what would we do today in our cool driving school: ")

    # Initial graph stream
    for chunk in graph.stream({"messages": HumanMessage(content=user_input)},
                              config=thread_config,
                              stream_mode='values'):
        print(chunk["messages"][-1].name)
        chunk["messages"][-1].pretty_print()
        print("\n")

    while True:
        if user_input.lower() == "quit":
            print("Exiting the program.")
            break

        state = graph.get_state(thread_config)
        messages = state.values.get("messages", [])

        if messages and messages[-1].name == "quiz_agent":
            update_graph(graph, thread_config)
            messages = graph.get_state(thread_config).values.get("messages", [])
            if messages:
                messages[-1].pretty_print()
        else:
            user_input = input("Provide your answer: ")
            if user_input.lower() == "quit":
                print("Exiting the program.")
                break

            for chunk in graph.stream({"messages": HumanMessage(content=user_input)},
                                      config=thread_config,
                                      stream_mode='values'):
                print(chunk["messages"][-1].name)
                chunk["messages"][-1].pretty_print()
                print("\n")

            
if __name__ == "__main__":
    main()