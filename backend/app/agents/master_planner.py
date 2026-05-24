import os
from typing import Optional
# 1. Am schimbat importul de la Google la Ollama
from langchain_community.chat_models import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from app.schemas.planner_schemas import JourneyRoadmap
from app.models.coding_problem import CodingProblem

# Persona rămâne aceeași (Senior Engineering Coach)
SYSTEM_PROMPT = """
You are an elite Senior Engineering Coach at a top-tier FAANG company.
Your mission is to create a highly structured, actionable, and personalized learning roadmap for engineers.

STRICT OUTPUT CONSTRAINTS:
1. You MUST respond EXACTLY with a valid JSON object. 
2. Do NOT include any preamble, conversational text, markdown formatting blocks (like ```json), or conclusions. Return ONLY the raw JSON.
3. The JSON must perfectly match this structure:
   - "journey_title": (string) A professional title for the roadmap.
   - "overview": (string) A brief, high-impact description of the overall goal.
   - "daily_plans": (list) A list of daily plan objects. Each object must have:
       - "day_number": (integer)
       - "title": (string) Focus of the day.
       - "concepts_to_cover": (list of strings) 2-4 actionable, specific tasks or concepts.
       - "difficulty": (string: "Beginner", "Intermediate", or "Advanced")
       - "recommended_problem_tags": (list of strings) Select up to 3 tags strictly from the provided UNIQUE_TAGS list.
4. You must generate EXACTLY {target_days} days in the "daily_plans" list. No more, no less.

UNIQUE_TAGS LIST TO CHOOSE FROM: {unique_tags}
""".strip()

async def generate_roadmap(user_goal: str, target_days: int, db: Session) -> JourneyRoadmap:
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")

    try:
        # Fetch all unique tags from CodingProblem table
        all_problems = db.query(CodingProblem).all()
        unique_tags = set()
        for p in all_problems:
            if p.tags:
                unique_tags.update(p.tags)
        
        unique_tags_str = ", ".join(list(unique_tags)) if unique_tags else "python, basic, arrays, loops, functions"
        # 2. Am înlocuit inițializarea Gemini cu ChatOllama
        # Folosim modelul tău qwen2.5-coder:3b și ne conectăm la portul local
        from langchain_core.output_parsers import JsonOutputParser
        
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = ChatOllama(
            model="qwen2.5-coder:3b",
            base_url=ollama_base_url,
            temperature=0,  # Lower temperature for better JSON
            format="json",
        )

        parser = JsonOutputParser(pydantic_object=JourneyRoadmap)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", "My goal is to learn: {user_goal}. I want a plan for exactly {target_days} days."),
        ])

        chain = prompt | llm | parser

        roadmap_data = await chain.ainvoke({
            "user_goal": user_goal,
            "target_days": target_days,
            "format_instructions": parser.get_format_instructions(),
            "unique_tags": unique_tags_str
        })

        assert isinstance(roadmap_data, dict), "Roadmap data must be a dictionary"
        # Parse the dict into the Pydantic model
        return JourneyRoadmap(**roadmap_data)

    except Exception as e:
        print(f"Error generating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to generate learning roadmap: {str(e)}") from e
