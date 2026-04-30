from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

def get_tasks_by_daily_plan(db: Session, daily_plan_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    return list(db.execute(select(Task).where(Task.daily_plan_id == daily_plan_id).offset(skip).limit(limit)).scalars().all())

def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, db_task: Task, task_in: TaskUpdate) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: Task) -> Task:
    db.delete(db_task)
    db.commit()
    return db_task
