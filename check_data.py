from app.database import SessionLocal
from app.models.user import User
from app.models.job import Job

db = SessionLocal()

print("--- Users ---")
users = db.query(User).all()
for u in users:
    print(u.id, u.username, u.email)

print("--- Jobs ---")
jobs = db.query(Job).all()
for j in jobs:
    print(j.id, j.title, j.company, j.status)

db.close()