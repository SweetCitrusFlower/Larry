import os
from typing import Optional
# 1. Am schimbat importul de la Google la Ollama
from langchain_community.chat_models import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.planner_schemas import JourneyRoadmap

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
       - "theoretical_topic_content": (string) Comprehensive theoretical content explaining the concepts for the day. Use markdown.
       - "task": (object) A practical coding task with:
           - "problem_title": (string)
           - "problem_description": (string) Detailed markdown description.
           - "starter_code": (string) Starter code snippet.
           - "hidden_solution": (string) The complete working solution code.
4. You must generate EXACTLY {target_days} days in the "daily_plans" list. No more, no less.
{extra_constraints}
""".strip()

def get_llm():
    from langchain_core.output_parsers import JsonOutputParser
    # 2. Am înlocuit inițializarea Gemini cu ChatOllama
    # Folosim modelul tău qwen2.5-coder:3b și ne conectăm la portul local
    llm = ChatOllama(
        model="qwen2.5-coder:3b",
        base_url="http://localhost:11434",
        temperature=0,  # Lower temperature for better JSON
        format="json",
    )
    return llm, JsonOutputParser(pydantic_object=JourneyRoadmap)

async def generate_roadmap(user_goal: str, target_days: int) -> JourneyRoadmap:
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")

    try:
        llm, parser = get_llm()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", "My goal is to learn: {user_goal}. I want a plan for exactly {target_days} days."),
        ])

        chain = prompt | llm | parser

        roadmap_data = await chain.ainvoke({
            "user_goal": user_goal,
            "target_days": target_days,
            "extra_constraints": "",
            "format_instructions": parser.get_format_instructions()
        })

        return JourneyRoadmap(**roadmap_data)

    except Exception as e:
        print(f"Error generating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to generate learning roadmap: {str(e)}") from e

async def regenerate_roadmap(original_prompt: str, target_days: int, min_difficulty: str) -> JourneyRoadmap:
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")
    if min_difficulty not in ["Beginner", "Intermediate", "Advanced"]:
        raise ValueError("Difficulty must be Beginner, Intermediate, or Advanced.")

    try:
        llm, parser = get_llm()
        
        extra_constraints = f"5. NO regenerated DailyTask may have a difficulty lower than '{min_difficulty}'. Ensure difficulty progression remains pedagogically coherent."

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", "My goal was originally: {user_goal}. I want you to REGENERATE the entire plan for exactly {target_days} days. Ensure the minimum difficulty across all days is at least {min_difficulty}."),
        ])

        chain = prompt | llm | parser

        roadmap_data = await chain.ainvoke({
            "user_goal": original_prompt,
            "target_days": target_days,
            "min_difficulty": min_difficulty,
            "extra_constraints": extra_constraints,
            "format_instructions": parser.get_format_instructions()
        })

        return JourneyRoadmap(**roadmap_data)

    except Exception as e:
        print(f"Error regenerating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to regenerate learning roadmap: {str(e)}") from e