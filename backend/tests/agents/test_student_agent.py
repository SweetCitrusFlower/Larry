import pytest
from fastapi.testclient import TestClient
from typing import Generator

# We'll import the app and dependency to mock auth
from app.main import app
from app.api.deps import get_current_user
from app.models.user import User

# --- AUTH MOCKING STRATEGY ---
# Best Practice for FastAPI + Pytest:
# Instead of generating a real JWT and sending it in headers, we use `app.dependency_overrides`.
# This allows us to intercept the `get_current_user` dependency and return a mock User object.
# It makes tests faster, less brittle, and avoids hardcoding secrets in the test environment.

def override_get_current_user() -> User:
    """Mock user to bypass JWT authentication during tests."""
    return User(
        id=1,
        email="student@ai-platform.test",
        hashed_password="mock_hashed_password"
    )

@pytest.fixture(scope="module")
def student_client() -> Generator[TestClient, None, None]:
    """
    A specific test client for the Student Agent that automatically 
    has the authentication mocked out.
    """
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class TestStudentAgentWorkflow:
    """
    Simulated Student Agent: 
    Tests the end-to-end learning workflow from generating a journey
    to executing code via Judge0.
    """

    def test_1_student_journey_generation(self, student_client: TestClient):
        """
        Step 1: The student asks the Master Planner for a learning journey.
        """
        # Note: Adjust the payload according to your actual schema
        payload = {"prompt": "I want to learn Python loops", "target_days": 5}
        
        response = student_client.post("/api/v1/journeys/generate", json=payload)
        
        # Assert the endpoint exists and successfully processes the request
        assert response.status_code == 200, f"Journey generation failed: {response.text}"
        
        # Assert the response is valid JSON and contains Daily Plans
        data = response.json()
        assert "days" in data or "daily_plans" in data, "Response JSON missing daily plans structure"
        
        plans = data.get("days", data.get("daily_plans", []))
        assert isinstance(plans, list), "Daily plans should be a list"
        assert len(plans) > 0, "The journey should contain at least one day of learning"

    def test_2_student_code_execution_failure(self, student_client: TestClient):
        """
        Step 2: The student writes broken code. We expect Judge0 to return an error state.
        """
        # Note: Adjust the payload according to your UserSubmissionCreate schema
        broken_code_payload = {
            "user_id": 1,
            "task_id": 1, # Dummy task ID
            "submitted_code": "print('Hello World'", # Syntax error (missing parenthesis)
            "language": "python",
            "result_status": "pending"
        }
        
        response = student_client.post("/api/v1/submissions/", json=broken_code_payload)
        assert response.status_code in [200, 201, 404], f"Submission endpoint crashed: {response.text}"
        
        data = response.json()
        
        # In a real Judge0 integration, the status might update asynchronously.
        # If your endpoint is synchronous and waits for Judge0:
        status = data.get("status", "").lower()
        
        # Assert it caught the error
        assert status in ["error", "failed", "compilation error", "runtime error"], \
            f"Expected a failure status, but got: {status}"
            
        # Assert execution metrics exist
        assert "execution_time" in data or "time" in data, "Missing execution time"
        assert "memory_usage" in data or "memory" in data, "Missing memory usage"

    def test_3_student_code_execution_success(self, student_client: TestClient):
        """
        Step 3: The student writes valid code. We expect a success state from Judge0.
        """
        valid_code_payload = {
            "user_id": 1,
            "task_id": 1, 
            "submitted_code": "print('Hello World')", # Valid Python
            "language": "python",
            "result_status": "pending"
        }
        
        response = student_client.post("/api/v1/submissions/", json=valid_code_payload)
        assert response.status_code in [200, 201, 404], f"Submission endpoint crashed: {response.text}"
        
        data = response.json()
        
        status = data.get("status", "").lower()
        assert status in ["accepted", "success", "completed"], \
            f"Expected a success status, but got: {status}"
            
        # Assert the output exactly matches expectations (including newline)
        # Note: stdout or output field depends on your schema mapping from Judge0
        output = data.get("output", data.get("stdout", ""))
        assert output == "Hello World\n", f"Expected 'Hello World\\n', got {repr(output)}"
