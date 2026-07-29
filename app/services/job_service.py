from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.services import nlp_service
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobUpdate
from app.core.exceptions import JobNotFoundException


def create_job(db: Session, job: JobCreate, user_id: int) -> Job:
    db_job = Job(**job.model_dump(), user_id=user_id)
    if db_job.resume_text and db_job.description:
        db_job.match_score = nlp_service.compute_match_score(db_job.resume_text, db_job.description)
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
    db_job = get_job(db, job_id)  # raises JobNotFoundException if missing

    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)

    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job(db: Session, job_id: int) -> None:
    db_job = get_job(db, job_id)  # raises JobNotFoundException if missing
    db_job.is_deleted = True
    db.commit()