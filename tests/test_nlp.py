from app.services.nlp_service import compute_match_score, extract_missing_keywords

def test_identical_texts_high_score():
    text = "Experienced Python developer skilled in FastAPI and Docker"
    assert compute_match_score(text, text) > 90

def test_unrelated_texts_low_score():
    resume = "Experienced chef specializing in Italian cuisine"
    job = "Backend developer skilled in Python and FastAPI"
    assert compute_match_score(resume, job) < 20

def test_missing_keywords_detects_gap():
    resume = "Experienced Python developer"
    job = "Looking for a Python developer skilled in Docker and Kubernetes"
    missing = extract_missing_keywords(resume, job)
    assert "docker" in missing