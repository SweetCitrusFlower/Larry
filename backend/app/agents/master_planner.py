import os
from typing import Optional
# 1. Am schimbat importul de la Google la Ollama
from langchain_community.chat_models import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.planner_schemas import JourneyRoadmap

# Persona rămâne aceeași (Senior Engineering Coach)
SYSTEM_PROMPT = """
You are an elite Senior Engineering Coach at a top-tier FAANG company. 
...
""".strip()

async def generate_roadmap(user_goal: str, target_days: int) -> JourneyRoadmap:
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")

    try:
        # 2. Am înlocuit inițializarea Gemini cu ChatOllama
        # Folosim modelul tău qwen2.5-coder:3b și ne conectăm la portul local
        llm = ChatOllama(
            model="qwen2.5-coder:3b",
            base_url="http://localhost:11434",
            temperature=0.7,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "My goal is to learn: {user_goal}. I want a plan for exactly {target_days} days."),
        ])

        # 3. ChatOllama suportă de asemenea with_structured_output 
        # (Va forța modelul Qwen să scoată formatul JSON cerut de JourneyRoadmap)
        chain = prompt | llm.with_structured_output(JourneyRoadmap)

        roadmap: JourneyRoadmap = await chain.ainvoke({
            "user_goal": user_goal,
            "target_days": target_days
        })

        return roadmap

    except Exception as e:
        print(f"Error generating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to generate learning roadmap: {str(e)}") from e