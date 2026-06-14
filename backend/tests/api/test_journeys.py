import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app
from app.api.deps import get_current_user
from app.models.user import User
from app.models.journey import Journey
from app.schemas.planner_schemas import JourneyRoadmap, DailyPlanItem

# ─────────────────────────────────────────────
# Auth Mocking
# ─────────────────────────────────────────────
def override_get_current_user() -> User:
    return User(
        id=100,
        email="journey_tester@larry.ai",
        hashed_password="mock_hashed_password"
    )

@pytest.fixture(scope="module")
def auth_client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def dummy_journey_in_db(db):
    user = User(id=999, email="another_user@larry.ai", hashed_password="mock")
    db.add(user)
    db.commit()
    
    # Insert a dummy journey belonging to ANOTHER user
    journey = Journey(
        user_id=999,
        original_prompt="Learn Java basics",
        target_days=5,
        journey_title="Java 101",
        overview="Intro to Java",
        prompt_embedding=[0.5] * 768
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)
    return journey

# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def test_check_similarity_hit(auth_client, dummy_journey_in_db):
    """
    Test that a prompt with an identical/high-similarity embedding
    returns the JourneySimilarityResponse (score >= 80).
    """
    payload = {"prompt": "Learn Java basics", "target_days": 5}
    
    with patch("app.api.routers.journeys.VertexAIEmbeddings") as mock_embeddings:
        mock_instance = mock_embeddings.return_value
        # Return the exact same embedding to force Cosine Sim = 1.0
        mock_instance.aembed_query = AsyncMock(return_value=[0.5] * 768)
        
        response = auth_client.post("/api/v1/journeys/check-similarity", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert data["score"] >= 80.0
        assert data["journey"]["id"] == dummy_journey_in_db.id

def test_check_similarity_miss(auth_client, dummy_journey_in_db):
    """
    Test that a dissimilar embedding or different duration penalty
    pushes the score below 80 and returns 204 NO CONTENT.
    """
    # High day difference (50) will apply a heavy penalty (100% loss on the 15% duration weight)
    # Also, we mock orthogonal embeddings to ensure 0.0 cosine similarity
    payload = {"prompt": "Learn cooking", "target_days": 55}
    
    with patch("app.api.routers.journeys.VertexAIEmbeddings") as mock_embeddings:
        mock_instance = mock_embeddings.return_value
        # Return orthogonal embedding so Cosine Sim = 0.0
        mock_instance.aembed_query = AsyncMock(return_value=[-0.5] * 768)
        
        response = auth_client.post("/api/v1/journeys/check-similarity", json=payload)
        
        # Should return 204 because score < 80
        assert response.status_code == 204

def test_generate_journey_cache_hit(auth_client, dummy_journey_in_db):
    """
    Test that requesting exactly the same prompt + days clones the existing
    journey via get_equivalent_journey, bypassing AI generation.
    """
    payload = {"prompt": "Learn Java basics", "target_days": 5}
    
    with patch("app.api.routers.journeys.generate_roadmap", new_callable=AsyncMock) as mock_generate:
        response = auth_client.post("/api/v1/journeys/generate", json=payload)
        
        assert response.status_code in (200, 201)
        data = response.json()
        print("RETURNED JOURNEY DATA:", data)
        print("DUMMY JOURNEY ID:", dummy_journey_in_db.id, "USER_ID:", dummy_journey_in_db.user_id)
        assert data["journey_title"] == "Java 101"
        assert data["id"] != dummy_journey_in_db.id  # It must be cloned
        # Verify AI was completely bypassed
        mock_generate.assert_not_called()

def test_generate_journey_cache_miss(auth_client):
    """
    Test that a completely new prompt properly falls back to calling
    the AI roadmap generation.
    """
    payload = {"prompt": "Learn Advanced Rust", "target_days": 2}
    
    with patch("app.api.routers.journeys.generate_roadmap", new_callable=AsyncMock) as mock_generate, \
         patch("app.api.routers.journeys.VertexAIEmbeddings") as mock_embeddings:
         
        mock_generate.return_value = JourneyRoadmap(
            journey_title="Rust Advanced",
            overview="Hardcore Rust",
            daily_plans=[DailyPlanItem(day_number=i+1, title=f"Day {i+1}", concepts_to_cover=["Lifetimes"], difficulty="Advanced", recommended_problem_tags=[]) for i in range(2)]
        )
        mock_instance = mock_embeddings.return_value
        mock_instance.aembed_query = AsyncMock(return_value=[0.9] * 768)
        
        response = auth_client.post("/api/v1/journeys/generate", json=payload)
        
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["journey_title"] == "Rust Advanced"
        # AI was invoked!
        mock_generate.assert_called_once()
