from datetime import datetime
from uuid import uuid4

from celery import Celery
from sqlalchemy import or_

import models
from analysis import analyze_article, content_hash, parse_datetime, refresh_consensus, update_politician_scores
from config import settings
from database import SessionLocal, init_db
from qdrant_store import upsert_article
from scraper import run_scrapy_job


celery_app = Celery(
    "rapor_pejabat",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.update(
    accept_content=["json"],
    result_serializer="json",
    task_serializer="json",
    task_track_started=True,
    worker_max_tasks_per_child=1,
)


def _find_existing_article(db, item: dict):
    article_id = item.get("id")
    url = item.get("url")
    filters = []
    if article_id:
        filters.append(models.NewsArticle.id == article_id)
    if url:
        filters.append(models.NewsArticle.url == url)
    if not filters:
        return None
    return db.query(models.NewsArticle).filter(or_(*filters)).first()


def _store_article(db, politician: models.Politician, item: dict) -> tuple[models.NewsArticle, bool]:
    title = item.get("title") or "Berita tanpa judul"
    content = item.get("content") or ""
    article_id = item.get("id") or uuid4().hex
    facts, impacts, promise_tracking = analyze_article(item, politician)

    article = _find_existing_article(db, item)
    created = article is None
    if article is None:
        article = models.NewsArticle(id=article_id, politician_id=politician.id)
        db.add(article)

    article.title = title
    article.content = content
    article.source = item.get("source") or "Unknown"
    article.source_owner = item.get("source_owner") or item.get("source") or "Unknown"
    article.url = item.get("url")
    article.published_at = parse_datetime(item.get("published_at"))
    article.scraped_at = datetime.utcnow()
    article.content_hash = content_hash(title, content)
    article.raw_payload = item.get("raw_payload") or item
    article.fact_extraction = facts
    article.scores_impact = impacts
    article.promise_tracking = promise_tracking
    article.analysis_status = "ANALYZED"
    return article, created


def run_scrape_pipeline(politician_id: str, run_id: str | None = None, urls: list[str] | None = None) -> dict:
    init_db()
    db = SessionLocal()
    run = None
    try:
        politician = db.query(models.Politician).filter(models.Politician.id == politician_id).first()
        if not politician:
            raise ValueError(f"Politician not found: {politician_id}")

        if run_id:
            run = db.query(models.ScrapeRun).filter(models.ScrapeRun.id == run_id).first()
        if run is None:
            run = models.ScrapeRun(id=run_id or uuid4().hex, politician_id=politician_id)
            db.add(run)

        run.status = "RUNNING"
        run.started_at = datetime.utcnow()
        run.error = None
        db.commit()

        items = run_scrapy_job(
            politician_name=politician.name,
            seed_path=settings.RAW_NEWS_PATH,
            urls=urls or [],
        )

        created_count = 0
        updated_count = 0
        stored_articles = []
        for item in items:
            article, created = _store_article(db, politician, item)
            stored_articles.append(article)
            created_count += int(created)
            updated_count += int(not created)

        db.flush()
        refresh_consensus(db, politician_id)
        update_politician_scores(db, politician_id)

        for article in stored_articles:
            try:
                article.qdrant_point_id = upsert_article(article)
            except Exception as exc:
                article.raw_payload = {
                    **(article.raw_payload or {}),
                    "qdrant_error": str(exc),
                }

        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.stats = {
            "scraped": len(items),
            "created": created_count,
            "updated": updated_count,
            "qdrant_attempted": len(stored_articles),
        }
        db.commit()
        return {"run_id": run.id, **run.stats}
    except Exception as exc:
        db.rollback()
        if run is not None:
            run.status = "FAILED"
            run.finished_at = datetime.utcnow()
            run.error = str(exc)
            db.add(run)
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="scrape_politician")
def scrape_politician_task(self, politician_id: str, run_id: str | None = None, urls: list[str] | None = None) -> dict:
    return run_scrape_pipeline(politician_id=politician_id, run_id=run_id, urls=urls or [])
