import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://rapor:rapor@localhost:5432/raporpejabat",
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "raporpejabat_articles")
    DATA_DIR: str = os.getenv("DATA_DIR", str(ROOT_DIR / "data"))
    RAW_NEWS_PATH: str = os.getenv("RAW_NEWS_PATH", str(ROOT_DIR / "data" / "raw_news.json"))
    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "RaporPejabatBot/0.1 (+https://raporpejabat.local; civic accountability research)",
    )
    SCRAPER_ALLOWED_DOMAINS: str = os.getenv("SCRAPER_ALLOWED_DOMAINS", "")
    SCRAPER_LIMIT: int = int(os.getenv("SCRAPER_LIMIT", "25"))


settings = Settings()
