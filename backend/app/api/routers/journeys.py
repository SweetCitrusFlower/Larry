from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
import markdown
import weasyprint
from app.api.deps import get_current_user
from app.models.user import User
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.models.task import Task
from app.agents.master_planner import generate_roadmap, modify_roadmap
from app.schemas.journey import JourneyResponse, JourneyGenerateRequest, JourneyModifyRequest, DailyPlanResponse, JourneySimilarityResponse
import os
import numpy as np
from langchain_google_vertexai import VertexAIEmbeddings
from pydantic import BaseModel

router = APIRouter()



# ── Endpoints ──────────────────────────────────────────────────────────────────

from sqlalchemy import select

@router.get("/", response_model=List[JourneyResponse])
def list_journeys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all journeys (with daily plans) for the current user.
    """
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(Journey.user_id == current_user.id)
        .order_by(Journey.created_at.desc())
    )
    journeys = db.execute(stmt).scalars().unique().all()
    return journeys

@router.get("/{journey_id}", response_model=JourneyResponse)
def get_journey(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return a single journey with its daily plans.
    """
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(Journey.id == journey_id, Journey.user_id == current_user.id)
    )
    journey = db.execute(stmt).scalars().unique().first()
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey

@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journey(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a journey and all of its associated data (DailyPlans, Tasks, Submissions, ChatMessages).
    """
    stmt = select(Journey).where(Journey.id == journey_id, Journey.user_id == current_user.id)
    journey = db.execute(stmt).scalars().unique().first()
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
        
    db.delete(journey)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/generate", status_code=status.HTTP_201_CREATED, response_model=JourneyResponse)
async def generate_new_journey(
    request: JourneyGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to generate a new learning journey using the Master Planner AI Agent.
    """
    if request.target_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Target days must be a positive integer."
        )

    try:
        roadmap = await generate_roadmap(request.prompt, request.target_days, db=db)
        
        # Compute prompt embedding
        embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
        embeddings = VertexAIEmbeddings(model=embedding_model_name)
        prompt_embedding = await embeddings.aembed_query(request.prompt)

        db_journey = Journey(
            user_id=current_user.id,
            original_prompt=request.prompt,
            target_days=request.target_days,
            journey_title=roadmap.journey_title,
            overview=roadmap.overview,
            prompt_embedding=prompt_embedding
        )
        db.add(db_journey)
        db.flush()
        
        for plan_item in roadmap.daily_plans:
            db_plan = DailyPlan(
                journey_id=db_journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty
            )
            db.add(db_plan)
        
        db.commit()

        # Re-query with eager load so daily_plans are included in response
        db.refresh(db_journey)
        journey = (
            db.query(Journey)
            .options(joinedload(Journey.daily_plans))
            .filter(Journey.id == db_journey.id)
            .first()
        )
        return journey

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"Error during journey generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during journey generation: {str(e)}"
        )



@router.post("/check-similarity")
async def check_similarity(
    request: JourneyGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a highly similar journey exists in the database.
    Returns the most similar journey if score >= 90.
    """
    embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
    embeddings = VertexAIEmbeddings(model=embedding_model_name)
    query_embedding = np.array(await embeddings.aembed_query(request.prompt))

    # Fetch all journeys with embeddings
    stmt = select(Journey).options(joinedload(Journey.daily_plans)).where(Journey.prompt_embedding.is_not(None))
    existing_journeys = db.execute(stmt).scalars().unique().all()

    best_match = None
    best_score = 0.0

    for existing in existing_journeys:
        existing_emb = np.array(existing.prompt_embedding)
        
        # Cosine similarity
        dot_product = np.dot(query_embedding, existing_emb)
        norm_q = np.linalg.norm(query_embedding)
        norm_e = np.linalg.norm(existing_emb)
        
        if norm_q == 0 or norm_e == 0:
            print(f"Skipping journey {existing.id} due to zero norm")
            continue
            
        cosine_sim = dot_product / (norm_q * norm_e)
        topic_score = max(0, cosine_sim) * 100
        
        # Duration compatibility: Softer flat penalty of 2% per day difference
        existing_days = int(existing.target_days)
        target_days = int(request.target_days)
        day_diff = abs(existing_days - target_days)
        duration_compatibility = max(0.0, 100.0 - (day_diff * 2.0))
        
        total_score = (topic_score * 0.85) + (duration_compatibility * 0.15)
        
        print(f"Journey ID: {existing.id} | Topic Score: {topic_score:.2f} | Duration Score: {duration_compatibility:.2f} | Total Score: {total_score:.2f}")
        if total_score >= 80 and total_score > best_score:
            best_score = total_score
            best_match = existing

    if best_match:
        print(f"Found best match: Journey {best_match.id} with score {best_score:.2f}")
        return JourneySimilarityResponse(score=best_score, journey=best_match)
    
    print("No matching journey found above threshold.")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

class CloneRequest(BaseModel):
    source_journey_id: int
    new_prompt: str

@router.post("/clone", status_code=status.HTTP_201_CREATED, response_model=JourneyResponse)
async def clone_journey(
    request: CloneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans).joinedload(DailyPlan.tasks))
        .where(Journey.id == request.source_journey_id)
    )
    source_journey = db.execute(stmt).scalars().unique().first()
    
    if not source_journey:
        raise HTTPException(status_code=404, detail="Source journey not found")
        
    db_journey = Journey(
        user_id=current_user.id,
        original_prompt=request.new_prompt,
        target_days=source_journey.target_days,
        journey_title=source_journey.journey_title,
        overview=source_journey.overview,
        prompt_embedding=source_journey.prompt_embedding
    )
    db.add(db_journey)
    db.flush()
    
    for old_plan in source_journey.daily_plans:
        new_plan = DailyPlan(
            journey_id=db_journey.id,
            day_number=old_plan.day_number,
            title=old_plan.title,
            concepts_to_cover=old_plan.concepts_to_cover,
            difficulty=old_plan.difficulty,
            theoretical_topic_content=old_plan.theoretical_topic_content,
            rag_context_payload=old_plan.rag_context_payload,
            content_status=old_plan.content_status,
            recommended_problem_tags=old_plan.recommended_problem_tags
        )
        db.add(new_plan)
        db.flush()
        
        for old_task in old_plan.tasks:
            new_task = Task(
                daily_plan_id=new_plan.id,
                title=old_task.title,
                problem_id=old_task.problem_id,
                description=old_task.description,
                starter_code=old_task.starter_code,
                hidden_solution=old_task.hidden_solution
            )
            db.add(new_task)
            
    db.commit()
    db.refresh(db_journey)
    
    journey = (
        db.query(Journey)
        .options(joinedload(Journey.daily_plans))
        .filter(Journey.id == db_journey.id)
        .first()
    )
    return journey

@router.post("/{journey_id}/modify", response_model=JourneyResponse)
async def modify_journey(
    journey_id: int,
    request: JourneyModifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to modify an existing learning journey using the Master Planner AI Agent.
    """
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(Journey.id == journey_id, Journey.user_id == current_user.id)
    )
    db_journey = db.execute(stmt).scalars().unique().first()
    
    if not db_journey:
        raise HTTPException(status_code=404, detail="Journey not found")
        
    try:
        # Separate completed vs uncompleted plans
        all_plans = sorted(db_journey.daily_plans, key=lambda p: p.day_number)
        completed_plans = [p for p in all_plans if p.completion_status or (p.theoretical_topic_content and p.theoretical_topic_content.strip())]
        uncompleted_plans = [p for p in all_plans if not p.completion_status and not (p.theoretical_topic_content and p.theoretical_topic_content.strip())]
        
        target_days = len(uncompleted_plans)
        if target_days == 0:
            raise ValueError("All days are already completed. Nothing to modify.")
            
        start_day_number = uncompleted_plans[0].day_number if uncompleted_plans else len(all_plans) + 1
        
        roadmap = await modify_roadmap(
            user_prompt=request.prompt,
            existing_title=db_journey.journey_title,
            existing_overview=db_journey.overview,
            completed_plans=completed_plans,
            target_days=target_days,
            start_day_number=start_day_number,
            db=db
        )
        
        # Update Journey metadata
        db_journey.journey_title = roadmap.journey_title
        db_journey.overview = roadmap.overview
        
        # Delete uncompleted plans
        for p in uncompleted_plans:
            db.delete(p)
            
        # Add new plans
        for plan_item in roadmap.daily_plans:
            db_plan = DailyPlan(
                journey_id=db_journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty
            )
            db.add(db_plan)
            
        db.commit()
        db.refresh(db_journey)
        
        journey = (
            db.query(Journey)
            .options(joinedload(Journey.daily_plans))
            .filter(Journey.id == db_journey.id)
            .first()
        )
        return journey

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"Error during journey modification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during journey modification: {str(e)}"
        )

@router.get("/{journey_id}/export-pdf")
def export_journey_pdf(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all completed theoretical lessons for a Journey to a PDF.
    """
    # Fetch journey and order daily plans by day_number
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(Journey.id == journey_id, Journey.user_id == current_user.id)
    )
    journey = db.execute(stmt).scalars().unique().first()
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
        
    # Sort plans by day number
    sorted_plans = sorted(journey.daily_plans, key=lambda p: p.day_number)
    
    # Filter only plans that have generated content
    completed_plans = [p for p in sorted_plans if p.theoretical_topic_content and p.theoretical_topic_content.strip()]
    
    if not completed_plans:
        raise HTTPException(status_code=400, detail="No lessons generated yet to export")
        
    # Compile Markdown
    markdown_content = f"# {journey.journey_title or 'Learning Journey'}\n\n"
    markdown_content += f"**Goal:** {journey.original_prompt}\n\n"
    markdown_content += "---\n\n"
    
    for plan in completed_plans:
        markdown_content += f"## Day {plan.day_number}: {plan.title}\n\n"
        markdown_content += f"{plan.theoretical_topic_content}\n\n"
        markdown_content += "---\n\n"
        
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
    
    # Add some premium CSS for WeasyPrint
    full_html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; padding: 2em; }}
                h1 {{ color: #2563eb; font-size: 28pt; border-bottom: 2px solid #2563eb; padding-bottom: 0.5em; }}
                h2 {{ color: #1e40af; font-size: 22pt; margin-top: 2em; }}
                h3 {{ color: #1e3a8a; font-size: 18pt; }}
                code {{ background-color: #f1f5f9; padding: 0.2em 0.4em; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
                pre {{ background-color: #1e293b; color: #f8fafc; padding: 1em; border-radius: 8px; overflow-x: auto; }}
                pre code {{ background-color: transparent; color: inherit; padding: 0; }}
                blockquote {{ border-left: 4px solid #cbd5e1; margin-left: 0; padding-left: 1em; color: #64748b; font-style: italic; }}
                hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 2em 0; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
    </html>
    """
    
    # Generate PDF
    pdf_bytes = weasyprint.HTML(string=full_html).write_pdf()
    
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Journey_{journey.id}_Export.pdf"}
    )