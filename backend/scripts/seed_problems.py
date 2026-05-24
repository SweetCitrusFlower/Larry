import sys
import os
import json

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, engine, Base
from app.models.coding_problem import CodingProblem
from datasets import load_dataset

def seed_db():
    print("Starting independent problem pool seeding...")
    
    db = SessionLocal()
    
    try:
        # Fetch the mbpp dataset from HuggingFace
        print("Fetching 'mbpp' dataset from Hugging Face...")
        dataset = load_dataset("mbpp", split="train")
        
        # Extract and map the first 100 problems
        problems_to_insert = []
        for i, row in enumerate(dataset):
            if i >= 100:
                break
                
            problem_id = f"mbpp_{row['task_id']}"
            
            # Check if problem already exists
            existing_prob = db.query(CodingProblem).filter_by(problem_id=problem_id).first()
            if existing_prob:
                continue
                
            test_cases = row["test_list"]
            solution_code = row["code"]
            
            # Formatting as JSON for robust extraction by the Judge0 execution pipeline
            hidden_solution_data = {
                "reference_code": solution_code,
                "test_cases_asserts": test_cases
            }
            hidden_solution_json = json.dumps(hidden_solution_data, indent=2)
            
            # Extract function definition line for starter code
            func_def_line = [line for line in solution_code.split("\n") if line.startswith("def ")]
            starter_code = f"{func_def_line[0]}\n    # Write your solution here\n    pass\n" if func_def_line else "# Write your solution here\n"

            problem = CodingProblem(
                problem_id=problem_id,
                title=f"MBPP Problem {row['task_id']}",
                description=row["text"],
                difficulty="Beginner",  # MBPP defaults to mostly basic/beginner
                tags=["python", "mbpp", "functions"],
                starter_code=starter_code,
                hidden_solution=hidden_solution_json
            )
            problems_to_insert.append(problem)
            
        if problems_to_insert:
            db.add_all(problems_to_insert)
            db.commit()
            print(f"Successfully seeded {len(problems_to_insert)} CodingProblems into the database.")
        else:
            print("No new problems to seed. Database already contains these problems.")
            
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
