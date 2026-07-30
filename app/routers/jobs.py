from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
import asyncio
from sqlalchemy import select
from app.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobList
from app.models.job import JobStatus
from app.services import job_service, nlp_service
from app.core.security import get_current_user
from app.core.limiter import limiter
from app.models.user import User
from fastapi import BackgroundTasks
from app.models.job import Job
from app.services.job_service import check_job_staleness


router = APIRouter(prefix="/jobs", tags=["jobs"])



@router.post("/", response_model=JobResponse, status_code=201)
@limiter.limit("60/minute")
def create_job(
    request: Request,
    job: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_job = job_service.create_job(db, job, current_user.id)
    if job.resume_text and job.description:
        background_tasks.add_task(nlp_service.score_and_save, db, new_job.id)
    return new_job


@router.get("/", response_model=JobList)
@limiter.limit("60/minute")
def get_jobs(
    request: Request,
    job_status: JobStatus | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs, total = job_service.get_jobs(
        db=db, user_id=current_user.id, status=job_status,
        search=search, page=page, limit=limit
    )
    return JobList(jobs=jobs, total=total)

@router.get("/stale")
async def get_stale_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check all of the user's jobs concurrently and flag stale ones
    (applied 30+ days ago with no status update).
    """
    stmt = select(Job).where(Job.user_id == current_user.id, Job.is_deleted == False)
    jobs = db.scalars(stmt).all()

    results = await asyncio.gather(*[check_job_staleness(job) for job in jobs])

    stale_jobs = [r for r in results if r is not None]
    return {"stale_jobs": stale_jobs, "count": len(stale_jobs)}

@router.get("/{job_id}", response_model=JobResponse)
@limiter.limit("60/minute")
def get_job(request: Request, job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.get_job(db=db, job_id=job_id)


@router.put("/{job_id}", response_model=JobResponse)
@limiter.limit("60/minute")
def update_job(request: Request, job_id: int, job: JobUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.update_job(db=db, job_id=job_id, job_update=job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("60/minute")
def delete_job(request: Request, job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job_service.delete_job(db=db, job_id=job_id)



