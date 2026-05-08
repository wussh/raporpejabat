from uuid import uuid4

import redis
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
from config import settings
from database import SessionLocal, init_db
from qdrant_store import get_client, search_evidence
from seed import seed_data
from tasks import run_scrape_pipeline, scrape_politician_task


app = FastAPI(title="RaporPejabat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    urls: list[str] = Field(default_factory=list)
    sync: bool = False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root():
    return {"message": "Welcome to RaporPejabat API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    status = {"api": "healthy", "database": "unknown", "redis": "unknown", "qdrant": "unknown"}
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "healthy"
    except Exception as exc:
        status["database"] = f"unhealthy: {exc}"

    try:
        redis.from_url(settings.REDIS_URL).ping()
        status["redis"] = "healthy"
    except Exception as exc:
        status["redis"] = f"unhealthy: {exc}"

    try:
        get_client().get_collections()
        status["qdrant"] = "healthy"
    except Exception as exc:
        status["qdrant"] = f"unhealthy: {exc}"

    return status


@app.post("/seed")
def seed_database():
    seed_data()
    return {"status": "seeded"}


@app.get("/politicians")
def list_politicians(db: Session = Depends(get_db)):
    return db.query(models.Politician).order_by(models.Politician.name.asc()).all()


@app.get("/politicians/{p_id}")
def get_politician(p_id: str, db: Session = Depends(get_db)):
    politician = db.query(models.Politician).filter(models.Politician.id == p_id).first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    return politician


@app.get("/politicians/{p_id}/promises")
def list_promises(p_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Promise)
        .filter(models.Promise.politician_id == p_id)
        .order_by(models.Promise.id.asc())
        .all()
    )


@app.get("/politicians/{p_id}/news")
def list_news(p_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.NewsArticle)
        .filter(models.NewsArticle.politician_id == p_id)
        .order_by(models.NewsArticle.published_at.desc())
        .all()
    )


@app.post("/politicians/{p_id}/scrape")
def scrape_politician(p_id: str, payload: ScrapeRequest, db: Session = Depends(get_db)):
    politician = db.query(models.Politician).filter(models.Politician.id == p_id).first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")

    run_id = uuid4().hex
    run = models.ScrapeRun(id=run_id, politician_id=p_id, status="PENDING")
    db.add(run)
    db.commit()

    if payload.sync:
        result = run_scrape_pipeline(politician_id=p_id, run_id=run_id, urls=payload.urls)
        return {"mode": "sync", **result}

    try:
        task = scrape_politician_task.delay(p_id, run_id, payload.urls)
    except Exception as exc:
        run.status = "FAILED"
        run.error = str(exc)
        db.commit()
        raise HTTPException(status_code=503, detail=f"Unable to enqueue scrape task: {exc}") from exc

    run.celery_task_id = task.id
    db.commit()
    return {"mode": "async", "run_id": run_id, "task_id": task.id, "status": "PENDING"}


@app.get("/jobs/{run_id}")
def get_scrape_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(models.ScrapeRun).filter(models.ScrapeRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Job not found")
    return run


@app.get("/evidence/search")
def evidence_search(q: str = Query(..., min_length=2), limit: int = Query(5, ge=1, le=20)):
    try:
        return search_evidence(q, limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Qdrant search unavailable: {exc}") from exc
