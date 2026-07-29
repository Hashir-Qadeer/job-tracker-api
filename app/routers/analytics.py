import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models.job import Job
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _jobs_dataframe(db: Session, user_id: int) -> pd.DataFrame:
    stmt = select(Job).where(Job.user_id == user_id, Job.is_deleted == False)
    jobs = db.scalars(stmt).all()
    data = [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "status": j.status.value,
            "match_score": j.match_score,
            "applied_date": j.applied_date,
        }
        for j in jobs
    ]
    return pd.DataFrame(data)


@router.get("/summary")
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = _jobs_dataframe(db, current_user.id)
    if df.empty:
        return {"total_applications": 0, "by_status": {}, "avg_match_score": 0}
    return {
        "total_applications": len(df),
        "by_status": df["status"].value_counts().to_dict(),
        "avg_match_score": round(df["match_score"].mean(skipna=True), 2) if df["match_score"].notna().any() else 0,
    }


@router.get("/funnel")
def funnel(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = _jobs_dataframe(db, current_user.id)
    if df.empty:
        return {"applied": 0, "interview": 0, "offer": 0, "conversion_to_interview": 0, "conversion_to_offer": 0}
    counts = df["status"].value_counts()
    applied = int(counts.get("applied", 0)) + int(counts.get("interview", 0)) + int(counts.get("offer", 0)) + int(counts.get("rejected", 0))
    interview = int(counts.get("interview", 0)) + int(counts.get("offer", 0))
    offer = int(counts.get("offer", 0))
    return {
        "applied": applied,
        "interview": interview,
        "offer": offer,
        "conversion_to_interview": round(interview / applied * 100, 1) if applied else 0,
        "conversion_to_offer": round(offer / applied * 100, 1) if applied else 0,
    }


@router.get("/top-matches")
def top_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = _jobs_dataframe(db, current_user.id)
    if df.empty or df["match_score"].isna().all():
        return {"top_matches": []}
    top = df.dropna(subset=["match_score"]).sort_values("match_score", ascending=False).head(5)
    return {"top_matches": top.to_dict(orient="records")}


@router.get("/timeline")
def timeline(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = _jobs_dataframe(db, current_user.id)
    if df.empty or df["applied_date"].isna().all():
        return {"timeline": []}
    df["applied_date"] = pd.to_datetime(df["applied_date"])
    weekly = df.groupby(pd.Grouper(key="applied_date", freq="W")).size()
    return {"timeline": [{"week": str(k.date()), "count": int(v)} for k, v in weekly.items()]}