from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Politician(Base):
    __tablename__ = "politicians"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    title = Column(String)
    region = Column(String)
    color = Column(String)
    icp_score = Column(Float, default=0.0)
    sentinel_status = Column(String, default="Neutral")
    
    # Stores the 4-axis scores as a dict: {"Integritas": 5, ...}
    scores = Column(JSON)
    
    promises = relationship("Promise", back_populates="politician")
    news_articles = relationship("NewsArticle", back_populates="politician")
    scrape_runs = relationship("ScrapeRun", back_populates="politician")

class Promise(Base):
    __tablename__ = "promises"

    id = Column(String, primary_key=True)
    politician_id = Column(String, ForeignKey("politicians.id"))
    promise_text = Column(String, nullable=False)
    category = Column(String)
    status = Column(String, default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED, STALLED, CONTRADICTED
    analysis = Column(String)
    
    politician = relationship("Politician", back_populates="promises")

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(String, primary_key=True)
    politician_id = Column(String, ForeignKey("politicians.id"))
    title = Column(String, nullable=False)
    content = Column(Text)
    source = Column(String)
    source_owner = Column(String)
    url = Column(String, unique=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String, index=True)
    cluster_id = Column(String, index=True)
    consensus_group_count = Column(Integer, default=1)
    consensus_valid = Column(Boolean, default=False)
    raw_payload = Column(JSON)
    
    # AI Analysis results
    fact_extraction = Column(JSON) # Tahap 1 output
    scores_impact = Column(JSON)   # Tahap 2 output (array of axis impacts)
    promise_tracking = Column(JSON) # Tahap 3 output
    analysis_status = Column(String, default="PENDING")
    qdrant_point_id = Column(String)
    
    politician = relationship("Politician", back_populates="news_articles")


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(String, primary_key=True)
    celery_task_id = Column(String)
    politician_id = Column(String, ForeignKey("politicians.id"), nullable=False)
    status = Column(String, default="PENDING")
    source = Column(String, default="scrapy")
    requested_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    stats = Column(JSON)
    error = Column(Text)

    politician = relationship("Politician", back_populates="scrape_runs")
