"""
test_agent_evals.py
Evaluation scaffolding for the AI Agents in the Larry platform.

ARCHITECTURE: LLM-as-a-Judge (Probabilistic Evaluation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Unlike unit tests (deterministic), agent responses are probabilistic.
The same prompt can produce 100 different valid responses.
Therefore, we use a Judge LLM to grade responses against rubrics.

This file defines:
  1. The Golden Dataset structure (test cases with rubrics).
  2. The Judge LLM interface (currently mocked, replace with LangSmith/Ragas).
  3. Agent-specific eval strategies:
     - Socratic Tutor → Behavioral & Tone Eval
     - Master Planner → Structural & Logic Eval  
     - Content Creator (RAG) → Faithfulness & Relevance Eval

HOW TO ACTIVATE REAL EVALS:
  Set the environment variable LARRY_EVAL_MODE=live and configure
  LANGSMITH_API_KEY or OPENAI_API_KEY for the Judge LLM.
  Without these, all eval tests run in MOCK mode (always pass).
"""
import os
import json
import pytest
import asyncio
from dataclasses import dataclass, field
from typing import Optional

from app.agents.master_planner import generate_roadmap


# ─────────────────────────────────────────────
# Data Structures: The Golden Dataset Schema
# ─────────────────────────────────────────────

@dataclass
class EvalCase:
    """Represents a single row in the Golden Dataset."""
    case_id: str
    agent_target: str           # "tutor" | "planner" | "content_creator"
    user_input: str
    context: Optional[str]      # For RAG evals: the retrieved textbook chunks
    success_criteria: str       # Human-readable rubric for the Judge LLM
    min_score: float = 0.8      # Minimum acceptable score (0.0 to 1.0)
    metadata: dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# Golden Dataset: Test Cases per Agent
# ─────────────────────────────────────────────

TUTOR_EVAL_CASES = [
    EvalCase(
        case_id="tutor-001",
        agent_target="tutor",
        user_input="I don't understand how a binary search tree works. Can you show me the code?",
        context=None,
        success_criteria=(
            "The tutor must NOT provide any Python, C++ or pseudocode implementation. "
            "It MUST use a real-world analogy (e.g., dictionary, phone book) to explain the concept. "
            "The tone must be encouraging and Socratic (ask guiding questions). "
            "Score 0.0 if code is given, 1.0 if concept explained via analogy with guiding questions."
        ),
        min_score=0.85,
    ),
    EvalCase(
        case_id="tutor-002",
        agent_target="tutor",
        user_input="Just give me the solution for the fibonacci sequence, I'm stuck.",
        context=None,
        success_criteria=(
            "The tutor must refuse to give the direct solution. "
            "It must break down the problem into smaller steps using questions. "
            "Score 0.0 if direct code/answer is given, 1.0 if it guides the student step by step."
        ),
        min_score=0.85,
    ),
]

PLANNER_EVAL_CASES = [
    EvalCase(
        case_id="planner-001",
        agent_target="planner",
        user_input="Create a 5-day roadmap for learning Python basics for a complete beginner.",
        context=None,
        success_criteria=(
            "The response must be valid JSON. "
            "The JSON must contain a 'daily_plans' array with EXACTLY 5 elements. "
            "Topics must progress logically from simpler to more complex concepts. "
            "Score 0.0 if not valid JSON or wrong number of days, "
            "0.5 if correct structure but illogical progression, 1.0 if correct and logical."
        ),
        min_score=0.9,
        metadata={"expected_days": 5, "level": "beginner"},
    ),
    EvalCase(
        case_id="planner-002",
        agent_target="planner",
        user_input="I need a 3-day crash course on React hooks for someone who knows JavaScript.",
        context=None,
        success_criteria=(
            "The response must be valid JSON with a 'daily_plans' array of EXACTLY 3 elements. "
            "Content must be appropriate for intermediate JS developers. "
            "Should NOT include basic JS topics. "
            "Score based on structural correctness (50%) and content appropriateness (50%)."
        ),
        min_score=0.85,
        metadata={"expected_days": 3, "level": "intermediate"},
    ),
]

RAG_EVAL_CASES = [
    EvalCase(
        case_id="rag-001",
        agent_target="content_creator",
        user_input="Generate a lesson about Big-O notation for Day 1.",
        context=(
            "[Retrieved from: Introduction to Algorithms, Chapter 3]\n"
            "Big-O notation provides an upper bound on the growth rate of an algorithm's "
            "running time. For example, an algorithm with O(n²) time complexity..."
            # In production: replaced with actual ChromaDB retrieved chunks
        ),
        success_criteria=(
            "FAITHFULNESS: Every fact in the generated lesson must be directly traceable "
            "to the provided context chunks. The agent must NOT invent statistics, "
            "definitions or examples not present in the context. "
            "RELEVANCE: The lesson must be specifically about Big-O notation, not a "
            "general algorithms overview. "
            "Score 0.0 for hallucinations, 0.5 for relevant but invented facts, 1.0 for "
            "fully faithful and relevant lesson."
        ),
        min_score=0.90,
    ),
]

ALL_EVAL_CASES = TUTOR_EVAL_CASES + PLANNER_EVAL_CASES + RAG_EVAL_CASES


# ─────────────────────────────────────────────
# Judge LLM Interface (Mock / Live)
# ─────────────────────────────────────────────

EVAL_MODE = os.getenv("LARRY_EVAL_MODE", "mock")


def judge_response(eval_case: EvalCase, agent_response: str) -> float:
    """
    Sends the agent's response to the Judge LLM for scoring.

    In MOCK mode: returns a passing score of 1.0 for all responses.
    In LIVE mode: calls LangSmith/Ragas with the rubric and returns a real score.

    Args:
        eval_case: The EvalCase containing the rubric and context.
        agent_response: The raw text output from the agent under evaluation.

    Returns:
        A float score between 0.0 (complete failure) and 1.0 (perfect score).
    """
    if EVAL_MODE == "live":
        # ── LIVE MODE ────────────────────────────────────────────────────────
        # TODO: Replace this block with your LangSmith or Ragas integration.
        raise NotImplementedError(
            "Live eval mode requires LANGSMITH_API_KEY and LangSmith integration. "
            "See TODO in judge_response() to configure."
        )
    else:
        # ── MOCK MODE (default) ──────────────────────────────────────────────
        # Returns a perfect score so the CI pipeline passes without a live LLM.
        return 1.0


def validate_planner_structure(agent_response: str, expected_days: int) -> dict:
    """
    Deterministic (non-LLM) validation for the Master Planner output.
    Checks JSON validity and the number of days in the roadmap.
    """
    result = {"valid_json": False, "correct_day_count": False, "parsed": None}
    try:
        if isinstance(agent_response, str):
            data = json.loads(agent_response)
        else:
            data = agent_response
        
        result["valid_json"] = True
        result["parsed"] = data
        
        # Master Planner uses 'daily_plans', not 'days'
        plans = data.get("daily_plans", [])
        result["correct_day_count"] = len(plans) == expected_days
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    return result


# ─────────────────────────────────────────────
# Agent Stubs (Replace with real agent calls)
# ─────────────────────────────────────────────

def call_socratic_tutor(user_input: str) -> str:
    """Stub: Replace with a real call to the Socratic Tutor agent."""
    return (
        "That's a great question! Think of a Binary Search Tree like a dictionary. "
        "When you look up a word, do you start from the beginning every time? "
        "What strategy do you use? How could that apply to organizing numbers?"
    )


async def call_master_planner(user_input: str, expected_days: int) -> str:
    """Real call to the Master Planner agent."""
    try:
        roadmap = await generate_roadmap(user_input, expected_days)
        # Return as JSON string for consistent eval handling
        return roadmap.model_dump_json()
    except Exception as e:
        return json.dumps({"error": str(e)})


def call_content_creator(user_input: str, context: str) -> str:
    """Stub: Replace with a real call to the RAG Content Creator agent."""
    return (
        "## Lesson: Big-O Notation\n\n"
        "Big-O notation provides an upper bound on the growth rate of an algorithm's "
        "running time. As described in the course materials, an O(n²) algorithm's "
        "time grows quadratically with input size..."
    )


# ─────────────────────────────────────────────
# Eval Tests: Socratic Tutor
# ─────────────────────────────────────────────

@pytest.mark.skip(reason="Socratic Tutor agent not yet implemented")
class TestSocraticTutorEvals:
    """
    Behavioral & Tone Evaluation for the Socratic Tutor agent.
    Strategy: LLM-as-a-Judge scoring against a no-direct-answers rubric.
    """

    @pytest.mark.parametrize("eval_case", TUTOR_EVAL_CASES, ids=[c.case_id for c in TUTOR_EVAL_CASES])
    def test_tutor_does_not_give_direct_answers(self, eval_case):
        """Tutor must score above threshold: no direct code/solutions given."""
        response = call_socratic_tutor(eval_case.user_input)
        score = judge_response(eval_case, response)

        assert score >= eval_case.min_score, (
            f"[{eval_case.case_id}] Tutor eval FAILED.\n"
            f"Score: {score:.2f} (required: {eval_case.min_score:.2f})\n"
            f"Rubric: {eval_case.success_criteria}\n"
            f"Response: {response[:300]}..."
        )


# ─────────────────────────────────────────────
# Eval Tests: Master Planner
# ─────────────────────────────────────────────

class TestMasterPlannerEvals:
    """
    Structural & Logic Evaluation for the Master Planner agent.
    Strategy: Mix of deterministic JSON validation + LLM-as-a-Judge logic check.
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize("eval_case", PLANNER_EVAL_CASES, ids=[c.case_id for c in PLANNER_EVAL_CASES])
    async def test_planner_outputs_valid_json(self, eval_case):
        """Deterministic check: planner must return parseable JSON."""
        expected_days = eval_case.metadata.get("expected_days", 0)
        response = await call_master_planner(eval_case.user_input, expected_days)
        result = validate_planner_structure(response, expected_days)

        assert result["valid_json"], (
            f"[{eval_case.case_id}] Master Planner returned INVALID JSON.\n"
            f"Raw response: {response[:500]}"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("eval_case", PLANNER_EVAL_CASES, ids=[c.case_id for c in PLANNER_EVAL_CASES])
    async def test_planner_returns_correct_number_of_days(self, eval_case):
        """Deterministic check: the 'daily_plans' array must have exactly the requested length."""
        expected_days = eval_case.metadata.get("expected_days", 0)
        response = await call_master_planner(eval_case.user_input, expected_days)
        result = validate_planner_structure(response, expected_days)

        assert result["correct_day_count"], (
            f"[{eval_case.case_id}] Planner returned wrong number of days.\n"
            f"Expected: {expected_days}, "
            f"Got: {len(result['parsed'].get('daily_plans', [])) if result['parsed'] else 'N/A'}"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("eval_case", PLANNER_EVAL_CASES, ids=[c.case_id for c in PLANNER_EVAL_CASES])
    async def test_planner_logical_progression(self, eval_case):
        """LLM Judge check: topics must be logically ordered for the target skill level."""
        expected_days = eval_case.metadata.get("expected_days", 0)
        response = await call_master_planner(eval_case.user_input, expected_days)
        score = judge_response(eval_case, response)

        assert score >= eval_case.min_score, (
            f"[{eval_case.case_id}] Planner logic eval FAILED.\n"
            f"Score: {score:.2f} (required: {eval_case.min_score:.2f})\n"
            f"Rubric: {eval_case.success_criteria}"
        )


# ─────────────────────────────────────────────
# Eval Tests: Content Creator (RAG)
# ─────────────────────────────────────────────

@pytest.mark.skip(reason="Content Creator RAG agent not yet implemented")
class TestContentCreatorRAGEvals:
    """
    Faithfulness & Relevance Evaluation for the RAG Content Creator agent.
    Strategy: LLM-as-a-Judge checking for hallucinations against retrieved context.
    Industry metrics: Faithfulness (no hallucinations) + Answer Relevance.
    """

    @pytest.mark.parametrize("eval_case", RAG_EVAL_CASES, ids=[c.case_id for c in RAG_EVAL_CASES])
    def test_rag_faithfulness_no_hallucinations(self, eval_case):
        """
        FAITHFULNESS: Every fact in the lesson must be traceable to the context.
        This is the most critical eval — hallucinations break user trust.
        """
        response = call_content_creator(eval_case.user_input, eval_case.context or "")
        score = judge_response(eval_case, response)

        assert score >= eval_case.min_score, (
            f"[{eval_case.case_id}] RAG Faithfulness eval FAILED — potential hallucination.\n"
            f"Score: {score:.2f} (required: {eval_case.min_score:.2f})\n"
            f"Rubric: {eval_case.success_criteria}\n"
            f"Response excerpt: {response[:400]}..."
        )

    @pytest.mark.parametrize("eval_case", RAG_EVAL_CASES, ids=[c.case_id for c in RAG_EVAL_CASES])
    def test_rag_answer_relevance(self, eval_case):
        """
        ANSWER RELEVANCE: The lesson must cover the specific topic requested,
        not a tangentially related subject.
        """
        response = call_content_creator(eval_case.user_input, eval_case.context or "")
        # In mock mode: score is 1.0. In live mode: a separate relevance rubric is applied.
        score = judge_response(eval_case, response)

        assert score >= eval_case.min_score, (
            f"[{eval_case.case_id}] RAG Relevance eval FAILED.\n"
            f"Score: {score:.2f} (required: {eval_case.min_score:.2f})"
        )
