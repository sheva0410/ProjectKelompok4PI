from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Submission
from app.schemas import SubmissionCreate, SubmissionOut
from app.services.url_utils import hash_url, normalize_url
from app.services.scraper import ScrapeError, extract_article

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionOut, status_code=201)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    try:
        article = extract_article(payload.url)
    except ScrapeError as e:
        raise HTTPException(status_code=422, detail=str(e))

    normalized = normalize_url(payload.url)
    sub = Submission(
        url=payload.url,
        normalized_url=normalized,
        url_hash=hash_url(normalized),
        title=article.title,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Submission)
        .options(selectinload(Submission.result))
        .where(Submission.id == submission_id)
    )
    sub = db.scalar(stmt)
    if sub is None:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan")
    return sub


@router.get("", response_model=list[SubmissionOut])
def list_submissions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Submission)
        .options(selectinload(Submission.result))
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()