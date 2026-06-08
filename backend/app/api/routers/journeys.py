from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
import markdown
import weasyprint
from pydantic import BaseModel, ConfigDict
from app.api.deps import get_current_user
from app.models.user import User
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.agents.master_planner import generate_roadmap
from app.schemas.journey import JourneyResponse, JourneyGenerateRequest, DailyPlanResponse

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
        .options(joinedload(Journey.daily_plans).joinedload(DailyPlan.tasks))
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
        .options(joinedload(Journey.daily_plans).joinedload(DailyPlan.tasks))
        .where(Journey.id == journey_id, Journey.user_id == current_user.id)
    )
    journey = db.execute(stmt).scalars().unique().first()
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey

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
        
        db_journey = Journey(
            user_id=current_user.id,
            original_prompt=request.prompt,
            target_days=request.target_days,
            journey_title=roadmap.journey_title,
            overview=roadmap.overview
        )
        db.add(db_journey)
        db.flush()
        
        for plan_item in roadmap.daily_plans:
            db_plan = DailyPlan(
                journey_id=db_journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty,
                theoretical_topic_content=plan_item.theoretical_topic_content,
                completion_status=plan_item.completion_status,
                content_status=plan_item.content_status
            )
            
            db.add(db_plan)
            db.flush()

            db_task = Task(
                daily_plan_id=db_plan.id,
                title=plan_item.task.problem_title,
                problem_id="ai_generated",
                description=plan_item.task.problem_description,
                starter_code=plan_item.task.starter_code,
                hidden_solution=plan_item.task.hidden_solution
            )
            db.add(db_task)
        
        db.commit()

        # Re-query with eager load so daily_plans are included in response
        db.refresh(db_journey)
        
        journey = (
            db.query(Journey)
            .options(joinedload(Journey.daily_plans).joinedload(DailyPlan.tasks))
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

@router.put("/{journey_id}/difficulty", response_model=JourneyResponse)
async def update_journey_difficulty(
    journey_id: int,
    request: JourneyDifficultyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to regenerate a journey roadmap with a new minimum difficulty.
    """
    db_journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not db_journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    try:
        roadmap = await regenerate_roadmap(
            original_prompt=db_journey.original_prompt,
            target_days=db_journey.target_days,
            min_difficulty=request.difficulty,
            db=db
        )

        # Delete existing daily plans (which cascades to tasks)
        db.query(DailyPlan).filter(DailyPlan.journey_id == journey_id).delete()
        db.flush()

        for plan_item in roadmap.daily_plans:
            db_plan = DailyPlan(
                journey_id=db_journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty,
                theoretical_topic_content=plan_item.theoretical_topic_content
            )
            db.add(db_plan)
            db.flush()

            db_task = Task(
                daily_plan_id=db_plan.id,
                title=plan_item.task.problem_title,
                problem_id="ai_generated",
                description=plan_item.task.problem_description,
                starter_code=plan_item.task.starter_code,
                hidden_solution=plan_item.task.hidden_solution
            )
            db.add(db_task)
        
        db.commit()

        # Re-query with eager load so daily_plans are included in response
        db.refresh(db_journey)
        journey = (
            db.query(Journey)
            .options(joinedload(Journey.daily_plans).joinedload(DailyPlan.tasks))
            .filter(Journey.id == db_journey.id)
            .first()
        )
        return journey

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"Error during journey regeneration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during journey regeneration: {str(e)}"
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
