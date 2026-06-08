import pytest
import asyncio
from app.services.judge0 import submit_code, poll_submission, execute_code
from app.models.user import User
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.models.task import Task
from app.core.security import create_access_token
from tests.conftest import TestingSessionLocal

# We mark the entire class to use pytest-asyncio
@pytest.mark.asyncio
class TestJudge0Integration:
    
    async def test_case_1_basic_success(self):
        """
        Test Case 1: Submit a simple Python script and verify stdout and accepted status.
        """
        source_code = "print('Hello from Larry')"
        language_id = 71  # Python 3
        
        # 1. Send to Judge0
        token = await submit_code(source_code=source_code, language_id=language_id)
        assert token is not None, "Failed to get submission token from Judge0"
        
        # 2. Poll mechanism
        result = await poll_submission(token)
        
        # 3. Verify status and stdout
        assert result.get("status", {}).get("id") == 3, f"Expected Accepted (3), got {result.get('status')}"
        assert result.get("stdout") == "Hello from Larry\n", f"Expected 'Hello from Larry\\n', got {result.get('stdout')}"
        print("\n[Case 1] Passed! Output:", result.get("stdout").strip())

    async def test_case_2_input_output_logic(self):
        """
        Test Case 2: Submit a script that reads from stdin and verify it against expected_output.
        """
        source_code = "import sys\na, b = map(int, sys.stdin.read().split())\nprint(a + b)"
        language_id = 71
        stdin = "5 10"
        expected_output = "15\n"
        
        result = await execute_code(
            source_code=source_code, 
            language_id=language_id, 
            expected_output=expected_output,
            stdin=stdin
        )
        
        assert result.get("status", {}).get("id") == 3, f"Expected Accepted (3) for matching output, got {result.get('status')}"
        print("\n[Case 2] Passed! Output matched expected_output.")

# Non-async test for FastAPI Endpoint
def test_case_3_database_persistence(client):
    """
    Test Case 3: Call the FastAPI submission endpoint and verify DB updates.
    """
    db = TestingSessionLocal()
    
    # 1. Setup Mock Data (User, Journey, DailyPlan, Task)
    user = User(email="judge0@test.com", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    journey = Journey(journey_title="Test Journey", user_id=user.id, original_prompt="Test Prompt")
    db.add(journey)
    db.commit()
    db.refresh(journey)
    
    plan = DailyPlan(day_number=1, title="Day 1", journey_id=journey.id, concepts_to_cover=[], difficulty="Beginner")
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    task = Task(title="Test Task", daily_plan_id=plan.id, problem_id="P1", description="Test", starter_code="", hidden_solution="")
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 2. Get Auth Token
    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Call Endpoint
    payload = {
        "submitted_code": "print('DB Persistence Check')",
        "language_id": 71,
        "user_id": user.id,
        "task_id": task.id,
        "result_status": "pending"
    }
    
    response = client.post("/api/v1/submissions/", json=payload, headers=headers)
    assert response.status_code == 201, f"Failed to submit: {response.text}"
    
    data = response.json()
    assert data["result_status"] == "accepted", f"Expected accepted, got {data['result_status']}"
    assert data["stdout"] == "DB Persistence Check\n"
    assert data["execution_time"] is not None
    assert data["memory_usage"] is not None
    print(f"\n[Case 3] Passed! DB Status: {data['result_status']}, Exec Time: {data['execution_time']}s, Memory: {data['memory_usage']}KB")
    
    db.close()
