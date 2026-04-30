from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user_submission import UserSubmission
from app.schemas.user_submission import UserSubmissionCreate, UserSubmissionUpdate

def get_user_submission(db: Session, submission_id: int) -> Optional[UserSubmission]:
    return db.execute(select(UserSubmission).where(UserSubmission.id == submission_id)).scalar_one_or_none()

def get_submissions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[UserSubmission]:
    return list(db.execute(select(UserSubmission).where(UserSubmission.user_id == user_id).offset(skip).limit(limit)).scalars().all())

def get_submissions_by_task(db: Session, task_id: int, skip: int = 0, limit: int = 100) -> List[UserSubmission]:
    return list(db.execute(select(UserSubmission).where(UserSubmission.task_id == task_id).offset(skip).limit(limit)).scalars().all())

def create_user_submission(db: Session, submission: UserSubmissionCreate) -> UserSubmission:
    db_submission = UserSubmission(**submission.model_dump())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def update_user_submission(db: Session, db_submission: UserSubmission, submission_in: UserSubmissionUpdate) -> UserSubmission:
    update_data = submission_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_submission, field, value)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def delete_user_submission(db: Session, db_submission: UserSubmission) -> UserSubmission:
    db.delete(db_submission)
    db.commit()
    return db_submission
