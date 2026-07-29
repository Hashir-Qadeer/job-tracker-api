from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobList
from app.models.job import JobStatus
from app.services import job_service
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.create_job(db=db, job=job, user_id=current_user.id)


@router.get("/", response_model=JobList)
def get_jobs(
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


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.get_job(db=db, job_id=job_id)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.update_job(db=db, job_id=job_id, job_update=job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job_service.delete_job(db=db, job_id=job_id)