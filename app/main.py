from fastapi import FastAPI
from app.routers import jobs

app = FastAPI(title="Job Tracker API")

app.include_router(jobs.router)


@app.get("/")
def root():
    return {"message": "Job Tracker API"}