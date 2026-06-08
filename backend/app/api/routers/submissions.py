from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user_submission import UserSubmissionCreate, UserSubmissionUpdate, UserSubmissionResponse, UserStatisticsResponse
from app.crud.crud_user_submission import (
    get_user_submission, 
    get_submissions_by_user, 
    get_submissions_by_task, 
    create_user_submission, 
    update_user_submission, 
    delete_user_submission,
    get_user_statistics
)
from app.crud.crud_task import get_task
from app.api.routers.tasks import verify_task_owner
from app.api.deps import get_current_user

router = APIRouter()

def _verify_user_can_access_task(db: Session, task_id: int, user_id: int):
    task = get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    verify_task_owner(db, daily_plan_id=task.daily_plan_id, user_id=user_id)
    return task

import asyncio
import json
from app.services.judge0 import execute_code

@router.post("/", response_model=UserSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: UserSubmissionCreate,
    current_user: User = Depends(get_current_user)
):
    if submission_in.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    task = _verify_user_can_access_task(db, task_id=submission_in.task_id, user_id=current_user.id)
    
    code_to_execute = submission_in.submitted_code
    
    try:
        if task.hidden_solution:
            hidden_data = json.loads(task.hidden_solution)
            test_cases = hidden_data.get("test_cases_asserts", [])
            if test_cases:
                assertions_str = "\n".join(test_cases)
                code_to_execute = f"{code_to_execute}\n\n# --- Test Cases ---\n{assertions_str}"
    except json.JSONDecodeError:
        pass # If JSON is invalid, just run the raw code
    
    # 1. Save pending submission
    submission_in.result_status = "pending"
    db_submission = await asyncio.to_thread(create_user_submission, db, submission=submission_in)
    
    try:
        # 2. Call Judge0
        result = await execute_code(
            source_code=code_to_execute,
            language_id=submission_in.language_id or 71,
        )
        
        # 3. Process Judge0 result
        status_dict = result.get("status")
        status_id = None
        if isinstance(status_dict, dict):
            status_id = status_dict.get("id")

        # 3 is Accepted, anything else is typically a failure (Wrong Answer, Time Limit Exceeded, Compile Error, etc.)
        result_status = "accepted" if status_id == 3 else "failed"
        
        stdout_val = result.get("stdout")
        stderr_val = result.get("stderr") or result.get("compile_output")
        time_val = result.get("time")
        mem_val = result.get("memory")

        update_data = UserSubmissionUpdate(
            result_status=result_status,
            stdout=str(stdout_val) if stdout_val is not None else None,
            stderr=str(stderr_val) if stderr_val is not None else None,
            execution_time=float(time_val) if time_val is not None else None,
            memory_usage=int(mem_val) if mem_val is not None else None
        )
        
        return await asyncio.to_thread(update_user_submission, db, db_submission=db_submission, submission_in=update_data)
        
    except Exception as e:
        update_data = UserSubmissionUpdate(
            result_status="error",
            stderr=str(e)
        )
        return await asyncio.to_thread(update_user_submission, db, db_submission=db_submission, submission_in=update_data)

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.user_submission import UserSubmission
from app.models.task import Task
from app.models.daily_plan import DailyPlan

@router.get("/user/statistics", response_model=UserStatisticsResponse)
def read_user_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_statistics(db, user_id=current_user.id)

@router.get("/user", response_model=List[UserSubmissionResponse])
def read_my_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(UserSubmission)
        .options(joinedload(UserSubmission.task).joinedload(Task.daily_plan))
        .where(UserSubmission.user_id == current_user.id)
        .order_by(UserSubmission.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    submissions = db.execute(stmt).scalars().all()
    
    # Decorate the submissions with titles
    results = []
    for sub in submissions:
        sub_dict = UserSubmissionResponse.model_validate(sub).model_dump()
        if sub.task:
            sub_dict["task_title"] = sub.task.title
            if sub.task.daily_plan:
                sub_dict["daily_plan_title"] = sub.task.daily_plan.title
        results.append(sub_dict)
        
    return results

@router.get("/task/{task_id}", response_model=List[UserSubmissionResponse])
def read_task_submissions(
    task_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    _verify_user_can_access_task(db, task_id=task_id, user_id=current_user.id)
    return get_submissions_by_task(db, task_id=task_id, skip=skip, limit=limit)

@router.get("/{submission_id}", response_model=UserSubmissionResponse)
def read_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = get_user_submission(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return submission

@router.put("/{submission_id}", response_model=UserSubmissionResponse)
def update_existing_submission(
    submission_id: int,
    submission_in: UserSubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = get_user_submission(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return update_user_submission(db, db_submission=submission, submission_in=submission_in)

@router.delete("/{submission_id}", response_model=UserSubmissionResponse)
def delete_existing_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = get_user_submission(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return delete_user_submission(db, db_submission=submission)
