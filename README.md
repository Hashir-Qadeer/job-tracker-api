# Smart Job Tracker API

A backend API for tracking job applications, with an NLP-powered resume-to-job match scorer, JWT authentication, analytics, and rate limiting.

## Tech Stack
- FastAPI, SQLAlchemy, Alembic
- PostgreSQL
- JWT auth (python-jose, passlib/bcrypt)
- scikit-learn (TF-IDF) + spaCy (keyword extraction)
- pandas (analytics aggregation)
- slowapi (rate limiting)
- pytest + pytest-cov (87%+ coverage)

## Features
- Full CRUD for job applications with pagination, search, and status filtering
- JWT-based registration/login, per-user data isolation
- NLP resume scorer: TF-IDF cosine similarity + missing-keyword extraction
- Analytics: summary stats, application funnel, top matches, weekly timeline
- Rate limiting, structured logging, centralized error handling

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register a new user |
| POST | /auth/login | Login, returns JWT (form-encoded) |
| POST | /jobs/ | Create a job application |
| GET | /jobs/ | List jobs (paginated, filterable) |
| GET | /jobs/{id} | Get a single job |
| PUT | /jobs/{id} | Update a job |
| DELETE | /jobs/{id} | Soft-delete a job |
| POST | /jobs/{id}/score | Score resume against a job description |
| GET | /analytics/summary | Application summary stats |
| GET | /analytics/funnel | Applied→Interview→Offer funnel |
| GET | /analytics/top-matches | Top 5 jobs by match score |
| GET | /analytics/timeline | Applications per week |
| GET | /health | Health check |

## Running Locally

\`\`\`bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# copy .env.example to .env and fill in your Postgres credentials
alembic upgrade head
uvicorn app.main:app --reload
\`\`\`

Visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Tests

\`\`\`bash
pytest --cov=app tests/ -v
\`\`\`