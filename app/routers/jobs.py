from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobList
from app.models.job import JobStatus
from app.services import job_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.job import ScoreRequest, ScoreResponse
from app.services import nlp_service


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
def get_job(job_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    updated = job_service.update_job(db=db, job_id=job_id, job_update=job)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return updated


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    deleted = job_service.delete_job(db=db, job_id=job_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )




@router.post("/{job_id}/score", response_model=ScoreResponse)
def score_job(
    job_id: int,
    score_data: ScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = job_service.get_job(db, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(404, "Job not found")

    match_score = nlp_service.compute_match_score(score_data.resume_text, job.description or "")
    missing = nlp_service.extract_missing_keywords(score_data.resume_text, job.description or "")

    job.match_score = match_score
    job.resume_text = score_data.resume_text
    db.commit()

    return {"match_score": match_score, "missing_keywords": missing}