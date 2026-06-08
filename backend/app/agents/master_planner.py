import os
# 1. Am schimbat importul de la Google la Ollama
from langchain_ollama import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from app.schemas.planner_schemas import JourneyRoadmap
from app.models.coding_problem import CodingProblem

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
       - "recommended_problem_tags": (list of strings) Select up to 3 tags strictly from the provided UNIQUE_TAGS list.
       - "theoretical_topic_content": (string) A text description of the current plan's theoretical overview. 
       - "completion_status": (bool) The flag that tells if the concepts of the current plan were completed.
       - "content_status": (string) The status of the creation process of the plan. 
4. You must generate EXACTLY {target_days} days in the "daily_plans" list. No more, no less.
{extra_constraints}

UNIQUE_TAGS LIST TO CHOOSE FROM: {unique_tags}
""".strip()

def get_llm_and_tags(db: Session):
    all_problems = db.query(CodingProblem).all()
    unique_tags = set()
    for p in all_problems:
        if p.tags:
            unique_tags.update(p.tags)
    
    unique_tags_str = ", ".join(list(unique_tags)) if unique_tags else "python, basic, arrays, loops, functions"
    
    from langchain_core.output_parsers import JsonOutputParser
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = ChatOllama(
        model="qwen2.5-coder:3b",
        base_url=ollama_base_url,
        temperature=0,
        format="json",
    )
    parser = JsonOutputParser(pydantic_object=JourneyRoadmap)
    return llm, parser, unique_tags_str

async def generate_roadmap(user_goal: str, target_days: int, db: Session) -> JourneyRoadmap:
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")

    try:
        llm, parser, unique_tags_str = get_llm_and_tags(db)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", "My goal is to learn: {user_goal}. I want a plan for exactly {target_days} days."),
        ])

        chain = prompt | llm | parser

        roadmap_data = await chain.ainvoke({
            "user_goal": user_goal,
            "target_days": target_days,
            "extra_constraints": "",
            "unique_tags": unique_tags_str,
            "format_instructions": parser.get_format_instructions()
        })

        assert isinstance(roadmap_data, dict), "Roadmap data must be a dictionary"
        
        return JourneyRoadmap(**roadmap_data)

    except Exception as e:
        print(f"Error generating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to generate learning roadmap: {str(e)}") from e

async def regenerate_roadmap(original_prompt: str, target_days: int, min_difficulty: str, db: Session) -> JourneyRoadmap:
    if target_days <= 0:
        raise ValueError("Target days must be a positive integer.")
    if min_difficulty not in ["Beginner", "Intermediate", "Advanced"]:
        raise ValueError("Difficulty must be Beginner, Intermediate, or Advanced.")

    try:
        llm, parser, unique_tags_str = get_llm_and_tags(db)
        
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
            "unique_tags": unique_tags_str,
            "format_instructions": parser.get_format_instructions()
        })

        assert isinstance(roadmap_data, dict), "Roadmap data must be a dictionary"
        return JourneyRoadmap(**roadmap_data)

    except Exception as e:
        print(f"Error regenerating roadmap: {str(e)}")
        raise RuntimeError(f"Failed to regenerate learning roadmap: {str(e)}") from e
