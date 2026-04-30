from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user_submission import UserSubmissionCreate, UserSubmissionUpdate, UserSubmissionResponse
from app.crud.crud_user_submission import get_user_submission, get_submissions_by_user, get_submissions_by_task, create_user_submission, update_user_submission, delete_user_submission
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=UserSubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_new_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: UserSubmissionCreate,
    current_user: User = Depends(get_current_user)
):
    if submission_in.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return create_user_submission(db, submission=submission_in)

@router.get("/user", response_model=List[UserSubmissionResponse])
def read_my_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    return get_submissions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/task/{task_id}", response_model=List[UserSubmissionResponse])
def read_task_submissions(
    task_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
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
