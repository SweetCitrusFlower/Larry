import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.planner_schemas import JourneyRoadmap

# Define the persona and logic for the Master Planner
SYSTEM_PROMPT = """
You are an elite Senior Engineering Coach at a top-tier FAANG company. 
Your specialty is taking complex technical topics and breaking them down into digestible, highly effective learning roadmaps for aspiring software engineers.

Your task is to create a structured learning journey based on the user's goal and a specific number of days.

GUIDELINES:
1. Divide the requested topic logically over EXACTLY the number of days specified.
2. Ensure a progressive learning curve: start with foundational concepts (Beginner) and move towards more complex integration or architecture (Intermediate/Advanced).
3. Be specific with the "concepts_to_cover" - use industry-standard terminology.
4. The "journey_title" should be professional yet motivating.
5. The "overview" should clearly state the value proposition and what the user will be able to build or explain after completion.
6. Maintain a professional, encouraging, and authoritative FAANG coach persona.

You must output a structured JSON response matching the required schema.
""".strip()

async def generate_roadmap(user_goal: str, target_days: int) -> JourneyRoadmap:
    """
    Generates a structured learning roadmap using Gemini Pro.
    
    Args:
        user_goal: The topic or skill the user wants to learn.
        target_days: The number of days the roadmap should span.
        
    Returns:
        A JourneyRoadmap object containing the daily plan.
        
    Raises:
        ValueError: If the input parameters are invalid.
        RuntimeError: If the LLM fails to generate a valid roadmap.
    """
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")

    try:
        # Initialize the LangChain model for Gemini
        # Note: Ensure GOOGLE_API_KEY is in your environment
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_retries=2,
        )

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "My goal is to learn: {user_goal}. I want a plan for exactly {target_days} days."),
        ])

        # Chain the prompt and the model with structured output
        # This ensures the output is parsed directly into our Pydantic model
        chain = prompt | llm.with_structured_output(JourneyRoadmap)

        # Execute the chain
        roadmap: JourneyRoadmap = await chain.ainvoke({
            "user_goal": user_goal,
            "target_days": target_days
        })

        return roadmap

    except Exception as e:
        # Log the error in a real production environment
        print(f"Error generating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to generate learning roadmap: {str(e)}") from e
