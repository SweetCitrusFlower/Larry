from typing import List
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# -----------------------------------------------------------------------------
# Pydantic Models for Structured Output
# -----------------------------------------------------------------------------

class DailyPlanItem(BaseModel):
    day_number: int = Field(description="The day number in the learning journey (e.g., 1, 2, 3).")
    title: str = Field(description="The main title or theme of the day's lesson.")
    concepts_to_cover: List[str] = Field(description="A list of specific concepts, skills, or topics to be covered on this day.")
    difficulty: str = Field(description="The difficulty level for this day (e.g., Beginner, Intermediate, Advanced).")

class MasterPlannerOutput(BaseModel):
    journey_title: str = Field(description="A catchy and descriptive title for the entire learning journey.")
    overview: str = Field(description="A brief overview or summary of what the student will learn throughout the journey.")
    daily_plans: List[DailyPlanItem] = Field(description="An array of daily learning plans.")

# -----------------------------------------------------------------------------
# LangChain Pipeline Setup
# -----------------------------------------------------------------------------

# Initialize the Ollama model.
# Ensure Ollama is running locally and the model is pulled (`ollama run qwen2.5-coder:3b`)
llm = ChatOllama(
    model="qwen2.5-coder:3b",
    temperature=0.2, # Low temperature for more deterministic/structured output
)

# Set up the Pydantic parser
parser = PydanticOutputParser(pydantic_object=MasterPlannerOutput)

# Define the Prompt Template
PROMPT_TEMPLATE = """You are an Expert Curriculum Designer and AI Coding Coach.
Your task is to generate a highly effective, logical, and structured learning journey based on the student's request.

Student Request: {prompt}
Total Days Allowed: {total_days}

Guidelines:
1. Break down the topic into logical, progressive steps across exactly {total_days} days.
2. Ensure the progression makes sense (fundamentals before advanced concepts).
3. Be concise and actionable.

IMPORTANT: You must output a valid JSON object containing the actual curriculum data. 
DO NOT output the JSON schema. DO NOT parrot back the instructions. 
Fill in the JSON object with the real generated titles, overviews, and daily plan content.

{format_instructions}

Do not include any other text, markdown blocks, or conversational filler outside of the JSON structure.
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["prompt", "total_days"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Construct the Runnable chain
# We pipe the prompt -> llm -> parser
chain = prompt | llm | parser

async def generate_journey(user_prompt: str, total_days: int) -> MasterPlannerOutput:
    """
    Invokes the Master Planner LLM agent to generate a structured learning curriculum.
    
    Args:
        user_prompt (str): The user's requested topic (e.g., "I want to learn Python loops").
        total_days (int): How many days the curriculum should span.
        
    Returns:
        MasterPlannerOutput: A Pydantic object containing the structured journey.
    """
    result = await chain.ainvoke({"prompt": user_prompt, "total_days": total_days})
    return result
