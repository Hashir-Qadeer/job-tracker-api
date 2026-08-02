import hashlib
import json

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.core.cache import redis_client
from app.models.job import Job

nlp = spacy.load("en_core_web_sm")


def compute_match_score(resume: str, job_desc: str) -> float:
    if not resume.strip() or not job_desc.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([resume, job_desc])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(score) * 100, 2)


def extract_missing_keywords(resume: str, job_desc: str) -> list[str]:
    resume_doc = nlp(resume)      # no .lower() here
    job_doc = nlp(job_desc)       # no .lower() here

    resume_tokens = {
        token.lemma_.lower() for token in resume_doc
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and not token.is_punct
    }
    job_tokens = {
        token.lemma_.lower() for token in job_doc
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and not token.is_punct
    }

    missing = job_tokens - resume_tokens
    return sorted(missing)

def get_cached_score(resume: str, job_desc: str) -> tuple[float, bool]:
    """Returns (score, was_cache_hit)."""
    key = "score:" + hashlib.md5(f"{resume}{job_desc}".encode()).hexdigest()
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached), True
    result = compute_match_score(resume, job_desc)
    redis_client.set(key, json.dumps(result), ex=86400)
    return result, False  
 
def score_and_save(db: Session, job_id: int):
    job = db.get(Job, job_id)
    if not job or not job.resume_text or not job.description:
        return
    score, _ = get_cached_score(job.resume_text, job.description)
    job.match_score = score
    db.commit()


 

