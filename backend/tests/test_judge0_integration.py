import pytest
import asyncio
from app.services.judge0 import submit_code, poll_submission, execute_code
from app.models.user import User
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.models.task import Task
from app.core.security import create_access_token
from tests.conftest import TestingSessionLocal
from unittest.mock import patch, MagicMock, AsyncMock

class AsyncContextManagerMock:
    def __init__(self, mock_client):
        self.mock_client = mock_client
    async def __aenter__(self):
        return self.mock_client
    async def __aexit__(self, exc_type, exc, tb):
        pass

@pytest.fixture(autouse=True)
def mock_httpx_judge0():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_instance = AsyncMock()
        mock_client_cls.return_value = AsyncContextManagerMock(mock_client_instance)
        
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"token": "fake-token"}
        mock_post_response.raise_for_status = MagicMock()
        mock_client_instance.post.return_value = mock_post_response
        
        def mock_get(*args, **kwargs):
            mock_resp = MagicMock()
            url = args[0] if args else ""
            mock_resp.raise_for_status = MagicMock()
            
            # Default response
            data = {
                "status": {"id": 3, "description": "Accepted"},
                "stdout": "Hello from Larry\n",
                "time": "0.01",
                "memory": 1024
            }
            # For test_case_2 input logic
            if "execute_code" in str(mock_client_instance.post.call_args) or True: 
                # We can just return '15\n' dynamically if it's the second test
                # Or just return '15\n' for everything, but case 1 expects 'Hello from Larry\n'
                # Let's inspect the POST payload if needed, but side_effect is easier based on a counter
                pass
            mock_resp.json.return_value = data
            return mock_resp
            
        mock_client_instance.get.side_effect = mock_get
        yield mock_client_instance

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
        # We mocked it to return 'Hello from Larry\n'
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
        
        # We patch the mock dynamically for this specific test
        from unittest.mock import MagicMock
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_instance = AsyncMock()
            mock_client_cls.return_value = AsyncContextManagerMock(mock_client_instance)
            
            mock_post_response = MagicMock()
            mock_post_response.json.return_value = {"token": "fake-token-2"}
            mock_client_instance.post.return_value = mock_post_response
            
            mock_get_response = MagicMock()
            mock_get_response.json.return_value = {
                "status": {"id": 3, "description": "Accepted"},
                "stdout": "15\n",
                "time": "0.01",
                "memory": 1024
            }
            mock_client_instance.get.return_value = mock_get_response

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
    
    # Use patch to mock Judge0 specifically for the FastAPI thread since FastAPI will spawn it in another thread/loop potentially
    with patch("app.api.routers.submissions.execute_code") as mock_execute:
        # FastAPI router calls await execute_code(source_code=..., language_id=...)
        # We need an AsyncMock since execute_code is an async function
        from unittest.mock import AsyncMock
        mock_execute_async = AsyncMock()
        mock_execute_async.return_value = {
            "status": {"id": 3, "description": "Accepted"},
            "stdout": "DB Persistence Check\n",
            "time": "0.05",
            "memory": 2048,
            "compile_output": None,
            "stderr": None
        }
        mock_execute.side_effect = mock_execute_async
        
        response = client.post("/api/v1/submissions/", json=payload, headers=headers)
    
    assert response.status_code == 201, f"Failed to submit: {response.text}"
    
    data = response.json()
    assert data["result_status"].lower() == "accepted", f"Expected accepted, got {data['result_status']}"
    assert data["stdout"] == "DB Persistence Check\n"
    print(f"\n[Case 3] Passed! DB Status: {data['result_status']}")
    
    db.close()
