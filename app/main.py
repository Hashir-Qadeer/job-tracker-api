from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import time

from app.routers import jobs, auth, analytics
from app.core.exceptions import (
    JobNotFoundException,
    UnauthorizedException,
    DuplicateEmailException,
    InvalidCredentialsException
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Tracker API")

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(analytics.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration}ms")
    return response


@app.exception_handler(JobNotFoundException)
def job_not_found_handler(request: Request, exc: JobNotFoundException):
    logger.warning(f"Job not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UnauthorizedException)
def unauthorized_handler(request: Request, exc: UnauthorizedException):
    logger.warning(f"Unauthorized access attempt: {exc}")
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})


@app.exception_handler(DuplicateEmailException)
def duplicate_email_handler(request: Request, exc: DuplicateEmailException):
    logger.warning(f"Duplicate email registration attempt: {exc}")
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsException)
def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    logger.warning(f"Invalid login attempt: {exc}")
    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})


@app.get("/")
def root():
    return {"message": "Job Tracker API"}