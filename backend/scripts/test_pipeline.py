import sys
import os
import asyncio

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal
from app.models.user import User
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.models.task import Task
from app.models.coding_problem import CodingProblem
from app.agents.master_planner import generate_roadmap
from app.agents.content_creator import generate_daily_lesson

async def main():
    print("--- Starting End-to-End Pipeline Test ---")
    
    db = SessionLocal()
    
    try:
        # Setup: Ensure a dummy user exists
        user = db.query(User).filter_by(email="pipeline_tester@larry.com").first()
        if not user:
            user = User(email="pipeline_tester@larry.com", hashed_password="dummy_hash")
            db.add(user)
            db.commit()
            db.refresh(user)

        # ---------------------------------------------------------
        # Step 1: Master Planner
        # ---------------------------------------------------------
        print("\n[Step 1] Calling Master Planner...")
        user_goal = "I want to learn Python basics in 3 days"
        target_days = 3
        
        # Generate the structured JSON roadmap using the LLM
        roadmap = await generate_roadmap(user_goal=user_goal, target_days=target_days, db=db)
        
        print("   -> Roadmap Generated! Saving Journey and DailyPlans to DB...")
        journey = Journey(
            user_id=user.id,
            original_prompt=user_goal,
            target_days=target_days,
            journey_title=roadmap.journey_title,
            overview=roadmap.overview
        )
        db.add(journey)
        db.commit()
        db.refresh(journey)
        
        for plan_item in roadmap.daily_plans:
            dp = DailyPlan(
                journey_id=journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty,
                recommended_problem_tags=plan_item.recommended_problem_tags
            )
            db.add(dp)
        db.commit()
        
        # Validation 1
        saved_plans = db.query(DailyPlan).filter(DailyPlan.journey_id == journey.id).order_by(DailyPlan.day_number).all()
        print(f"\n[Validation 1] Successfully created Journey (ID: {journey.id}) and {len(saved_plans)} DailyPlans.")
        for dp in saved_plans:
            print(f"   - Day {dp.day_number}: {dp.title}")
            print(f"     Recommended Tags: {dp.recommended_problem_tags}")
            
        if not saved_plans:
            print("Error: No DailyPlans were saved.")
            return

        # ---------------------------------------------------------
        # Step 2: Content Creator
        # ---------------------------------------------------------
        first_day_plan = saved_plans[0]
        print(f"\n[Step 2] Calling Content Creator for DailyPlan ID: {first_day_plan.id} (Day 1)...")
        
        await generate_daily_lesson(daily_plan_id=first_day_plan.id, db=db)
        
        # Validation 2
        print("\n[Validation 2] Fetching updated DailyPlan and Task...")
        # Refresh the session object to ensure we get the latest DB state
        db.refresh(first_day_plan)
        
        print(f"   -> Final Content Status: {first_day_plan.content_status}")
        
        if first_day_plan.theoretical_topic_content:
            snippet = first_day_plan.theoretical_topic_content[:200].replace('\n', ' ')
            print(f"   -> Content Snippet: {snippet}...")
        else:
            print("   -> Error: No theoretical content generated.")
            
        # Fetch the attached task
        task = db.query(Task).filter(Task.daily_plan_id == first_day_plan.id).first()
        if task:
            # Look up the original coding problem to see its tags
            problem = db.query(CodingProblem).filter(CodingProblem.problem_id == task.problem_id).first()
            print(f"   -> Attached Task: '{task.title}'")
            if problem:
                print(f"   -> Problem Original Tags: {problem.tags}")
                print(f"   -> Overlap Check: The tags {problem.tags} should have at least 50% overlap with recommended tags {first_day_plan.recommended_problem_tags}")
        else:
            print("   -> Error: No Task was attached to the DailyPlan.")

    except Exception as e:
        print(f"\n[!] Test failed with error: {e}")
        db.rollback()
    finally:
        db.close()
        print("\n--- Pipeline Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
