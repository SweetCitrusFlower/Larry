from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud.crud_task import get_task, get_tasks_by_daily_plan, create_task, update_task, delete_task
from app.crud.crud_daily_plan import get_daily_plan
from app.api.routers.daily_plans import verify_journey_owner
from app.api.deps import get_current_user

router = APIRouter()

def verify_task_owner(db: Session, daily_plan_id: int, user_id: int):
    daily_plan = get_daily_plan(db, daily_plan_id=daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily Plan not found")
    verify_journey_owner(db, daily_plan.journey_id, user_id)
    return daily_plan

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user)
):
    verify_task_owner(db, task_in.daily_plan_id, current_user.id)
    return create_task(db, task=task_in)

@router.get("/daily-plan/{daily_plan_id}", response_model=List[TaskResponse])
def read_daily_plan_tasks(
    daily_plan_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    verify_task_owner(db, daily_plan_id, current_user.id)
    return get_tasks_by_daily_plan(db, daily_plan_id=daily_plan_id, skip=skip, limit=limit)

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    verify_task_owner(db, task.daily_plan_id, current_user.id)
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_existing_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    verify_task_owner(db, task.daily_plan_id, current_user.id)
    return update_task(db, db_task=task, task_in=task_in)

@router.delete("/{task_id}", response_model=TaskResponse)
def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    verify_task_owner(db, task.daily_plan_id, current_user.id)
    return delete_task(db, db_task=task)
