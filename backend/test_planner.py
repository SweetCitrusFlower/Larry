import asyncio
import traceback
import json
import os
import sys

# Add the backend directory to sys.path so we can import 'app' modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.master_planner import generate_roadmap

async def test_planner():
    user_goal = "I want to learn Python in 3 days"
    target_days = 3
    
    print(f"--- Testing Master Planner ---")
    print(f"Goal: '{user_goal}'")
    print(f"Target Days: {target_days}\n")
    print("Generating roadmap... (this may take a few seconds)\n")
    
    try:
        # 1. Execute the function
        roadmap = await generate_roadmap(user_goal=user_goal, target_days=target_days)
        
        # 2. Pretty-print the resulting Pydantic model as JSON
        # JourneyRoadmap inherits from BaseModel, so we can use model_dump()
        roadmap_dict = roadmap.model_dump()
        
        print("--- Success! Resulting Roadmap ---")
        print(json.dumps(roadmap_dict, indent=4))
        
    except Exception as e:
        # 3. Exact error traceback if LLM/Ollama fails
        print("--- Error Occurred ---")
        traceback.print_exc()

if __name__ == "__main__":
    # Mocking environment variables or DB sessions would go here if needed.
    # Fortunately, `generate_roadmap` operates purely on the LLM level and requires no DB mocks.
    asyncio.run(test_planner())
