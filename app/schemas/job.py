from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from app.models.job import JobStatus
from typing import Optional, List

class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    resume_text: str | None = None
    applied_date: datetime | None = None
    status: JobStatus = JobStatus.applied

class JobUpdate(BaseModel):
    title:str | None=None
    company: str | None=None
    location: str | None=None    
    description: str | None = None
    resume_text: str | None = None
    applied_date: datetime | None = None
    status: JobStatus | None = None

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    resume_text: str | None = None
    applied_date: datetime | None = None
    status: JobStatus
    match_score: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class JobList(BaseModel):
    jobs: list[JobResponse]
    total: int



class ScoreRequest(BaseModel):
    resume_text: str

class ScoreResponse(BaseModel):
    match_score: float
    missing_keywords: List[str]    