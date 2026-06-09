"""
Idle Hint Generation Service

Generates context-aware hints for students who have been idle for 4+ minutes.
Uses the Socratic Tutor approach to guide students without revealing solutions.
"""
import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.task import Task
from app.models.daily_plan import DailyPlan
from app.services.socratic_tutor import detect_code_leakage
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

# Fallback response when code leakage is detected
FALLBACK_HINT = "Consider reviewing the concepts to cover and the problem statement. What is the first step you should take?"


async def generate_idle_hint(
    db: Session,
    task_id: int,
    current_code: Optional[str] = None
) -> str:
    """
    Generate a context-aware hint for a student who has been idle.
    
    Args:
        db: Database session
        task_id: ID of the task the student is working on
        current_code: Optional current code state for context
    
    Returns:
        A concise hint (1-3 sentences) to guide the student
    """
    try:
        # Fetch task and related context
        task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
        if not task:
            return FALLBACK_HINT
        
        # Fetch daily plan for additional context
        daily_plan = db.execute(
            select(DailyPlan).where(DailyPlan.id == task.daily_plan_id)
        ).scalar_one_or_none()
        
        # Build context string
        context_parts = []
        
        # Add problem description
        if task.description:
            context_parts.append(f"Problem: {task.description}")
        
        # Add daily plan concepts
        if daily_plan and daily_plan.concepts_to_cover:
            concepts_str = ", ".join(daily_plan.concepts_to_cover)
            context_parts.append(f"Concepts to cover: {concepts_str}")
        
        # Add difficulty level
        if daily_plan and daily_plan.difficulty:
            context_parts.append(f"Difficulty: {daily_plan.difficulty}")
        
        # Add current progress
        if current_code:
            lines_written = len([l for l in current_code.split('\n') if l.strip()])
            context_parts.append(f"Current progress: {lines_written} lines of code written")
        
        rag_context = "\n".join(context_parts)
        
        # Generate hint using LLM
        hint = await _generate_hint_with_llm(
            task_description=task.description,
            concepts=daily_plan.concepts_to_cover if daily_plan else [],
            difficulty=daily_plan.difficulty if daily_plan else "medium",
            rag_context=rag_context,
            current_code=current_code
        )
        
        # Verify hint doesn't contain code
        if detect_code_leakage(hint):
            logger.warning(f"Code leakage detected in hint for task {task_id}, using fallback")
            return FALLBACK_HINT
        
        return hint
        
    except Exception as e:
        logger.error(f"Error generating idle hint for task {task_id}: {str(e)}")
        return FALLBACK_HINT


async def _generate_hint_with_llm(
    task_description: str,
    concepts: list,
    difficulty: str,
    rag_context: str,
    current_code: Optional[str] = None
) -> str:
    """
    Use Gemini LLM to generate a Socratic hint.
    """
    llm = ChatVertexAI(
        model="gemini-2.5-pro",
        temperature=0.3  # Slightly higher for variety in hints
    )
    
    system_prompt = """You are a patient coding tutor guiding a student who appears to be stuck.
The student has been idle for 4+ minutes without making progress on their task.

Your task is to generate a SHORT, encouraging hint (1-3 sentences max) that:
1. Does NOT provide code or complete solutions
2. References the specific concepts they should be learning
3. Guides them toward the NEXT logical step
4. Is encouraging and supportive

The student can see: the problem description, the starter code, and the concepts to learn.
Help them connect the dots without giving away the answer.

Context about the task:
{rag_context}

Remember: NO CODE in your response. Just a guiding question or direction."""
    
    user_message = """The student has been idle on this coding task. 
Generate a brief, encouraging hint to help them get unstuck.
Focus on the next logical step they should take."""
    
    if current_code:
        user_message += f"\n\nTheir current code state suggests they've started but may be unsure how to proceed."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_message)
    ])
    
    chain = prompt | llm
    
    # Run async
    def run_chain():
        return chain.invoke({"rag_context": rag_context})
    
    response = await asyncio.to_thread(run_chain)
    
    # Extract text from response
    hint_text = response.content if hasattr(response, 'content') else str(response)
    
    # Ensure it's concise (max 300 chars for 1-3 sentences)
    if len(hint_text) > 300:
        # Try to keep just first 1-2 sentences
        sentences = hint_text.split('.')
        hint_text = '.'.join(sentences[:2]) + '.'
    
    return hint_text.strip()
