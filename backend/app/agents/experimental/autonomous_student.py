"""
autonomous_student.py
Architectural draft for an Autonomous, Self-Reflective Student Agent.

This module uses LangGraph to define a cyclic state machine representing a student's
coding process: attempting a task, failing, asking a tutor, reflecting on the mistake,
saving the memory to ChromaDB, and trying again.

NOTE: This is an architectural draft. Execution components (Judge0 HTTP calls, Ollama)
are stubbed or represented as structural logic.
"""

import os
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator

from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
import chromadb

# ==========================================
# 1. State Definition
# ==========================================
# The State represents the memory of the agent during a single coding loop.
# `messages` or specific fields track the history of the current attempt.

class StudentState(TypedDict):
    task_description: str
    current_code: Optional[str]
    retrieved_memories: List[str]
    execution_status: str  # "Pending", "Success", "Error"
    execution_error: Optional[str]
    tutor_hint: Optional[str]
    reflection: Optional[str]
    attempt_count: int


# ==========================================
# 2. ChromaDB Integration
# ==========================================
# Local ChromaDB client to act as the Long-Term Memory (LTM).
# Stores reflections extracted from past failures to prevent repeating mistakes.

# Note: In production, persistent storage path should be used (e.g., persistent_client)
chroma_client = chromadb.Client() 
# Using default embedding function (all-MiniLM-L6-v2) for simplicity in draft
collection = chroma_client.get_or_create_collection(name="student_memories")


# ==========================================
# 3. Agent Tooling & LLMs
# ==========================================

# We instantiate the local LLM. 
# (Execution is disabled per constraints; this is structural setup)
llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0.2)


# ==========================================
# 4. Graph Nodes (The Cognitive Steps)
# ==========================================

def retrieve_memory(state: StudentState) -> StudentState:
    """
    NODE: Queries ChromaDB for past mistakes related to the current coding task.
    """
    task = state["task_description"]
    
    # Query ChromaDB for memories similar to the current task
    results = collection.query(
        query_texts=[task],
        n_results=2
    )
    
    memories = []
    if results and results.get("documents"):
        # Flatten the list of lists
        memories = [doc for sublist in results["documents"] for doc in sublist]
        
    return {"retrieved_memories": memories}


def write_code(state: StudentState) -> StudentState:
    """
    NODE: Generates Python code based on the task and retrieved memories.
    """
    prompt = f"""You are a student writing Python code to solve the following task:
Task: {state['task_description']}

Here are some things you learned from past mistakes (DO NOT repeat these mistakes):
{state['retrieved_memories']}

If you have a hint from a tutor for your previous failed attempt, use it:
Hint: {state.get('tutor_hint', 'None')}

Write only the Python code to solve the task.
"""
    # Generate code
    response = llm.invoke(prompt)
    code = response.content.strip()
    
    # Clean up markdown blocks if present
    if code.startswith("```python"):
        code = code.replace("```python", "").replace("```", "").strip()
        
    return {
        "current_code": code,
        "attempt_count": state.get("attempt_count", 0) + 1,
        "execution_status": "Pending"
    }


def evaluate_judge0(state: StudentState) -> StudentState:
    """
    NODE: Simulates sending the code to the Judge0 endpoint.
    In a real implementation, this would make an HTTP POST to `/api/v1/submissions/`.
    """
    code = state["current_code"]
    
    # --- SIMULATED JUDGE0 BEHAVIOR ---
    # For architectural drafting, we simulate a failure if the code lacks a colon (Syntax error)
    if code and "for " in code and ":" not in code:
        return {
            "execution_status": "Error",
            "execution_error": "SyntaxError: expected ':'"
        }
    elif state["attempt_count"] > 3:
        # Force fail safe
        return {
            "execution_status": "Error",
            "execution_error": "TimeoutError: Logic loops infinitely"
        }
    
    # If the code passes the simulated judge
    return {
        "execution_status": "Success",
        "execution_error": None
    }


def consult_tutor(state: StudentState) -> StudentState:
    """
    NODE: Socratic Tutor analyzes the broken code and the execution error,
    providing a helpful hint without giving away the direct answer.
    """
    prompt = f"""You are a Socratic AI Tutor. Your student wrote this code:
{state['current_code']}

It failed with this error:
{state['execution_error']}

Provide a brief, 1-sentence hint guiding them to the syntax or logic error without writing the code for them.
"""
    response = llm.invoke(prompt)
    hint = response.content.strip()
    
    return {"tutor_hint": hint}


def reflect_and_remember(state: StudentState) -> StudentState:
    """
    NODE: Extracts a core learning from the mistake and hint, 
    and saves it to ChromaDB (Long-Term Memory).
    """
    prompt = f"""Analyze the failure to extract a concise memory for the future.
Task: {state['task_description']}
Code: {state['current_code']}
Error: {state['execution_error']}
Tutor Hint: {state['tutor_hint']}

Write a 1-sentence reflection starting with "I must remember to..."
"""
    response = llm.invoke(prompt)
    reflection = response.content.strip()
    
    # Save the reflection to ChromaDB
    # We use the task and the error as metadata so we can trace it later
    doc_id = f"mem_{hash(state['task_description'] + str(state['attempt_count']))}"
    
    collection.add(
        documents=[reflection],
        metadatas=[{"task": state["task_description"], "error": str(state["execution_error"])}],
        ids=[doc_id]
    )
    
    return {"reflection": reflection}


# ==========================================
# 5. Routing Logic (Conditional Edges)
# ==========================================

def route_after_evaluation(state: StudentState) -> str:
    """
    Conditional edge routing: Determines if the agent loops back to learn
    or finishes the task.
    """
    if state["execution_status"] == "Success":
        return END
    else:
        return "consult_tutor"


# ==========================================
# 6. Building the LangGraph State Machine
# ==========================================

# Initialize the graph
workflow = StateGraph(StudentState)

# Add all nodes
workflow.add_node("retrieve_memory", retrieve_memory)
workflow.add_node("write_code", write_code)
workflow.add_node("evaluate_judge0", evaluate_judge0)
workflow.add_node("consult_tutor", consult_tutor)
workflow.add_node("reflect_and_remember", reflect_and_remember)

# Define the flow (Edges)
workflow.set_entry_point("retrieve_memory")
workflow.add_edge("retrieve_memory", "write_code")
workflow.add_edge("write_code", "evaluate_judge0")

# Conditional routing from Evaluation
workflow.add_conditional_edges(
    "evaluate_judge0",
    route_after_evaluation,
    {
        END: END,
        "consult_tutor": "consult_tutor"
    }
)

# The learning loop
workflow.add_edge("consult_tutor", "reflect_and_remember")
workflow.add_edge("reflect_and_remember", "write_code")

# Compile the graph
autonomous_student_app = workflow.compile()

# Example usage (Commented out per architectural constraints):
# if __name__ == "__main__":
#     initial_state = {
#         "task_description": "Write a Python for loop that prints numbers 0 to 4",
#         "attempt_count": 0
#     }
#     result = autonomous_student_app.invoke(initial_state)
#     print("Final Status:", result.get("execution_status"))
