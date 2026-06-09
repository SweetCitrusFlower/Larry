import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.daily_plan import DailyPlan
from app.models.coding_problem import CodingProblem
from app.agents.content_creator import generate_daily_lesson
from app.db.database import Base

# Setup in-memory SQLite for testing
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
@patch('app.agents.content_creator.ChatVertexAI')
@patch('app.agents.content_creator.Chroma')
@patch('app.agents.content_creator.VertexAIEmbeddings')
@patch('app.agents.content_creator.chromadb.HttpClient')
async def test_generate_daily_lesson_saves_rag_context(
    mock_http_client,
    mock_embeddings,
    mock_chroma,
    mock_chat_vertex_ai,
    db_session
):
    """
    Verify that the `rag_context_payload` field in the database exactly matches 
    the chunks returned by the ChromaDB mock before the session commits.
    """
    from app.models.journey import Journey
    
    # Need a journey first
    journey = Journey(
        user_id=1,
        journey_title="Test Journey",
        target_days=1,
        original_prompt="Test"
    )
    db_session.add(journey)
    db_session.commit()
    db_session.refresh(journey)

    # 1. Setup Mock DB data
    plan = DailyPlan(
        journey_id=journey.id,
        day_number=1,
        title="Test Lesson",
        concepts_to_cover=["Binary Trees", "Traversal"],
        difficulty="Intermediate",
        content_status="PENDING"
    )
    db_session.add(plan)
    
    # Need a coding problem to satisfy the task creation logic
    problem = CodingProblem(
        problem_id="test_problem_1",
        title="Test Problem",
        description="Test Desc",
        difficulty="Intermediate",
        starter_code="print('hi')",
        hidden_solution="print('hi')",
        tags=["Binary Trees"]
    )
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(plan)

    # 2. Setup Mock RAG Chunks
    mock_doc1 = type('Document', (), {'page_content': "Mock RAG Chunk 1: Binary trees are trees."})()
    mock_doc2 = type('Document', (), {'page_content': "Mock RAG Chunk 2: Traversal is important."})()
    
    mock_vectorstore_instance = mock_chroma.return_value
    mock_vectorstore_instance.similarity_search.return_value = [mock_doc1, mock_doc2]

    # 3. Setup Mock LLM Response
    # The chain structure is prompt | llm, so we need to mock the invoke chain.
    # Since content_creator uses chain.ainvoke directly, we can mock it by patching the ChatPromptTemplate __or__ operator
    with patch('app.agents.content_creator.ChatPromptTemplate') as mock_prompt:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = type('Response', (), {'content': "## Teorie\nGenerated Mock Content."})()
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain
        
        # 4. Call the function
        await generate_daily_lesson(plan.id, db_session)

    # 5. Assertions
    db_session.refresh(plan)
    
    expected_payload = "Mock RAG Chunk 1: Binary trees are trees.\n\n---\n\nMock RAG Chunk 2: Traversal is important."
    
    assert plan.content_status == "COMPLETED"
    assert plan.theoretical_topic_content == "## Teorie\nGenerated Mock Content."
    assert plan.rag_context_payload == expected_payload, "RAG Context payload did not match the mocked ChromaDB chunks."
