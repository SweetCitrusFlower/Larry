from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.schemas.journey import JourneyCreate, JourneyUpdate

def get_journey(db: Session, journey_id: int) -> Optional[Journey]:
    return db.execute(select(Journey).where(Journey.id == journey_id)).scalar_one_or_none()

def get_journeys_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Journey]:
    return list(db.execute(select(Journey).where(Journey.user_id == user_id).offset(skip).limit(limit)).scalars().all())

def create_journey(db: Session, journey: JourneyCreate) -> Journey:
    db_journey = Journey(**journey.model_dump())
    db.add(db_journey)
    db.commit()
    db.refresh(db_journey)
    return db_journey

def update_journey(db: Session, db_journey: Journey, journey_in: JourneyUpdate) -> Journey:
    update_data = journey_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_journey, field, value)
    db.commit()
    db.refresh(db_journey)
    return db_journey

def delete_journey(db: Session, db_journey: Journey) -> Journey:
    db.delete(db_journey)
    db.commit()
    return db_journey


def get_equivalent_journey(db: Session, prompt: str, target_days: int) -> Optional[Journey]:
    """
    Find an existing Journey whose normalized prompt matches the provided prompt
    (case-insensitive, leading/trailing whitespace ignored) and whose
    `target_days` matches. The returned Journey includes its DailyPlans via
    eager loading so it can be reused or cloned immediately.

    This lookup enables caching/reuse of previously AI-generated Journeys to
    avoid re-invoking the costly generation pipeline.
    """
    if prompt is None:
        return None

    normalized = prompt.strip().lower()

    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(func.lower(func.trim(Journey.original_prompt)) == normalized, Journey.target_days == target_days)
    )
    return db.execute(stmt).scalars().unique().first()


def clone_journey_for_user(db: Session, source_journey: Journey, user_id: int) -> Journey:
    """
    Clone an existing Journey and its DailyPlans for `user_id`, resetting
    completion statuses so the cloned Journey appears freshly-generated for
    the new user.

    Rationale: The application enforces ownership checks (many endpoints
    verify `journey.user_id == current_user.id`). To keep client behavior
    unchanged while avoiding re-running the AI pipeline, we persist a cloned
    Journey that the requesting user owns. We intentionally do NOT delete or
    modify the original template Journey.
    """
    # Double-check whether the user already has a matching journey. This
    # helps avoid creating duplicate clones in common concurrent cases.
    normalized = source_journey.original_prompt.strip().lower() if source_journey.original_prompt else ""
    user_stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(func.lower(func.trim(Journey.original_prompt)) == normalized,
               Journey.target_days == source_journey.target_days,
               Journey.user_id == user_id)
    )
    existing_for_user = db.execute(user_stmt).scalars().unique().first()
    if existing_for_user:
        return existing_for_user

    db_journey = Journey(
        user_id=user_id,
        original_prompt=source_journey.original_prompt,
        target_days=source_journey.target_days,
        journey_title=source_journey.journey_title,
        overview=source_journey.overview,
    )
    db.add(db_journey)
    db.flush()

    # Copy daily plans; reset `completion_status` so the user receives a
    # clean journey state. We preserve generated content and other metadata
    # (e.g. theoretical_topic_content, content_status) so users can benefit
    # from previously generated assets. Adjust if you prefer to reset those
    # fields as well.
    for plan in source_journey.daily_plans:
        db_plan = DailyPlan(
            journey_id=db_journey.id,
            day_number=plan.day_number,
            title=plan.title,
            concepts_to_cover=plan.concepts_to_cover,
            difficulty=plan.difficulty,
            theoretical_topic_content=plan.theoretical_topic_content,
            rag_context_payload=plan.rag_context_payload,
            completion_status=False,
            content_status=plan.content_status,
            recommended_problem_tags=plan.recommended_problem_tags,
        )
        db.add(db_plan)

    db.commit()
    db.refresh(db_journey)
    return db_journey
