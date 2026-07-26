from datetime import date
from app.database import SessionLocal
from app.models.user import User
from app.models.job import Job, JobStatus

db = SessionLocal()

user = db.query(User).filter(User.email == "hashir@test.com").first()
if not user:
    user = User(
        username="hashir",
        email="hashir@test.com",
        hashed_password="fakehashedpassword123",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

jobs = [
    Job(
        title="Backend Developer",
        company="TechNova Solutions",
        location="Lahore, Pakistan",
        status=JobStatus.applied,
        description="Looking for a backend developer skilled in Python, FastAPI, and SQL databases.",
        resume_text="Experienced backend developer with .NET and Python background.",
        applied_date=date(2026, 7, 1),
        user_id=user.id,
    ),
    Job(
        title="AI Engineer Intern",
        company="Magnetar Solutions",
        location="Remote",
        status=JobStatus.interview,
        description="Seeking an AI engineer intern to build agent-based automation tools.",
        resume_text="Built job tracker API with NLP resume scoring.",
        applied_date=date(2026, 7, 5),
        user_id=user.id,
    ),
    Job(
        title="Python Developer",
        company="CodeCraft Inc",
        location="Karachi, Pakistan",
        status=JobStatus.rejected,
        description="Python developer needed for backend microservices.",
        resume_text="Strong Python fundamentals, learning FastAPI and SQLAlchemy.",
        applied_date=date(2026, 6, 20),
        user_id=user.id,
    ),
    Job(
        title="Software Engineer",
        company="Innotech Labs",
        location="Islamabad, Pakistan",
        status=JobStatus.offer,
        description="Full stack engineer role with focus on API development.",
        resume_text="Full stack developer with ASP.NET and React experience.",
        applied_date=date(2026, 7, 10),
        user_id=user.id,
    ),
    Job(
        title="Junior Data/AI Engineer",
        company="NexGen AI",
        location="Lahore, Pakistan",
        status=JobStatus.applied,
        description="Entry-level AI engineer role working on NLP pipelines and REST APIs.",
        resume_text="Personal project: job tracker API with TF-IDF resume matching.",
        applied_date=date(2026, 7, 15),
        user_id=user.id,
    ),
]

db.add_all(jobs)
db.commit()
db.close()

print("Seeded successfully! 5 jobs created.")