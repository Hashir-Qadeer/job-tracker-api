from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.services import nlp_service
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobUpdate
from app.core.exceptions import JobNotFoundException
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger("job-tracker")

def create_job(db: Session, job: JobCreate, user_id: int) -> Job:
    """
    Create a new job application record.

    Args:
        db: Active database session.
        job: The job data to create.
        user_id: The ID of the user creating this job.

    Returns:
        The newly created Job object (match_score will be None if
        scoring hasn't run yet — see background task in the router).
    """
    db_job = Job(**job.model_dump(), user_id=user_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


# job_service.py

def get_job(db: Session, job_id: int) -> Job:
    stmt = select(Job).where(Job.id == job_id, Job.is_deleted == False)
    job = db.scalars(stmt).first()
    if not job:
        raise JobNotFoundException(job_id)
    return job

def get_jobs(
    db: Session,
    user_id: int,
    status: JobStatus | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10
) -> tuple[list[Job], int]:
    stmt = select(Job).where(
        Job.is_deleted == False,
        Job.user_id == user_id
    )

    if status:
        stmt = stmt.where(Job.status == status)

    if search:
        stmt = stmt.where(Job.title.ilike(f"%{search}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt)

    stmt = stmt.offset((page - 1) * limit).limit(limit)
    jobs = db.scalars(stmt).all()

    return jobs, total




def update_job(db: Session, job_id: int, job_update: JobUpdate) -> Job:
    db_job = get_job(db, job_id)
    old_status = db_job.status
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    db.commit()
    db.refresh(db_job)

    if job_update.status and job_update.status != old_status and job_update.status in (JobStatus.offer, JobStatus.rejected):
        logger.info(f"NOTIFICATION: '{db_job.title}' at '{db_job.company}' status changed to {job_update.status.value}")

    return db_job


def delete_job(db: Session, job_id: int) -> None:
    db_job = get_job(db, job_id)  # raises JobNotFoundException if missing
    db_job.is_deleted = True
    db.commit()



async def check_job_staleness(job: Job) -> dict | None:
    """
    Check if a single job is stale (applied 30+ days ago, no status change).

    Args:
        job: The Job object to check.

    Returns:
        A dict with job details if stale, otherwise None.
    """
    if not job.applied_date:
        return None

    days_since_applied = (datetime.utcnow() - job.applied_date.replace(tzinfo=None)).days

    if days_since_applied >= 30 and job.status == JobStatus.applied:
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "days_since_applied": days_since_applied
        }
    return None