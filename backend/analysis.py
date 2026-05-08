import hashlib
import re
from collections import defaultdict
from datetime import datetime
from typing import Iterable

import models


AXIS_TO_SCORE_KEY = {
    "Integritas": "Integritas",
    "Realisasi Janji": "Janji",
    "Efisiensi Anggaran": "Efisiensi",
    "Stabilitas Sosial": "Sosial",
}

WEIGHTS = {
    "Integritas": 0.30,
    "Janji": 0.30,
    "Efisiensi": 0.20,
    "Sosial": 0.20,
}

STOPWORDS = {
    "yang",
    "dan",
    "atau",
    "dari",
    "untuk",
    "dengan",
    "pada",
    "dalam",
    "akan",
    "telah",
    "para",
    "oleh",
    "ini",
    "itu",
    "ke",
    "di",
    "sebagai",
}


def normalize_text(value: str | None) -> str:
    value = (value or "").lower()
    value = re.sub(r"https?://\S+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def content_hash(title: str | None, content: str | None) -> str:
    normalized = normalize_text(f"{title or ''} {content or ''}")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def token_set(text: str | None) -> set[str]:
    return {token for token in normalize_text(text).split() if len(token) > 3 and token not in STOPWORDS}


def similarity(left: str | None, right: str | None) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return datetime.utcnow()


def extract_budget(text: str) -> str | None:
    matches = re.findall(r"Rp\s?[\d.,]+(?:\s?(?:miliar|triliun|juta|ribu))?", text, flags=re.IGNORECASE)
    return ", ".join(dict.fromkeys(matches)) or None


def split_facts(text: str) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    return sentences[:4] if sentences else [text[:240]]


def _impact(axis: str, score: int, justification: str, evidence: str) -> dict:
    return {
        "axis": axis,
        "impact_score": score,
        "justification": justification,
        "confidence_level": 0.62,
        "evidence_citation": evidence[:280],
    }


def analyze_article(article: dict, politician: models.Politician) -> tuple[dict, list[dict], dict | None]:
    title = article.get("title") or "Berita tanpa judul"
    content = article.get("content") or ""
    combined = f"{title}. {content}"
    normalized = normalize_text(combined)
    facts = split_facts(content or title)
    budget = extract_budget(combined)

    fact_extraction = {
        "politician_name": politician.name,
        "event_summary": title,
        "key_facts": facts,
        "involved_institutions": article.get("institutions") or [],
        "budget_mentioned": budget,
        "source_bias_check": "Neutral",
    }

    impacts: list[dict] = []
    evidence = facts[0] if facts else title

    if any(keyword in normalized for keyword in ["hak angket", "dugaan", "nepotisme", "korupsi", "audit", "etik"]):
        impacts.append(
            _impact(
                "Integritas",
                -6,
                "Berita memuat proses pemeriksaan, dugaan pelanggaran, atau isu etik yang perlu diverifikasi lintas sumber.",
                evidence,
            )
        )
    elif any(keyword in normalized for keyword in ["transparansi", "lapor", "klarifikasi", "membatalkan"]):
        impacts.append(
            _impact(
                "Integritas",
                3,
                "Berita memuat tindakan klarifikasi, pelaporan, atau pembatalan kebijakan setelah masukan publik.",
                evidence,
            )
        )

    if any(keyword in normalized for keyword in ["program", "bantuan", "target", "gratis", "insentif", "pembangunan", "rumah layak"]):
        impacts.append(
            _impact(
                "Realisasi Janji",
                4,
                "Berita menunjukkan kegiatan, target, atau alokasi program yang dapat dicocokkan dengan daftar janji.",
                evidence,
            )
        )

    if any(keyword in normalized for keyword in ["rumah dinas", "mobil dinas", "renovasi", "land rover", "pengadaan"]):
        impacts.append(
            _impact(
                "Efisiensi Anggaran",
                -5,
                "Berita menyebut alokasi atau pengadaan fasilitas pemerintah yang perlu dibandingkan dengan prioritas layanan publik.",
                evidence,
            )
        )
    elif budget:
        impacts.append(
            _impact(
                "Efisiensi Anggaran",
                2,
                "Berita menyertakan nilai anggaran yang dapat diaudit terhadap sasaran program.",
                evidence,
            )
        )

    if any(keyword in normalized for keyword in ["warga", "petani", "sekolah", "kesehatan", "banjir", "longsor", "polusi", "kemacetan"]):
        impacts.append(
            _impact(
                "Stabilitas Sosial",
                3,
                "Berita menyebut dampak langsung pada warga, layanan dasar, lingkungan, atau mobilitas publik.",
                evidence,
            )
        )

    if not impacts:
        impacts.append(
            _impact(
                "Integritas",
                0,
                "Berita belum memuat dampak yang cukup spesifik untuk mengubah skor sumbu.",
                evidence,
            )
        )

    promise_tracking = None
    promise_keywords = ["janji", "program", "gratis", "insentif", "pembangunan", "bantuan", "rumah", "sekolah"]
    if any(keyword in normalized for keyword in promise_keywords):
        promise_tracking = {
            "promise_id": None,
            "alignment_score": 0.5,
            "current_status": "IN_PROGRESS",
            "analysis": "Berita memuat aktivitas program dan perlu dicocokkan dengan janji spesifik dalam basis data.",
        }

    return fact_extraction, impacts, promise_tracking


def refresh_consensus(db, politician_id: str) -> None:
    articles = db.query(models.NewsArticle).filter(models.NewsArticle.politician_id == politician_id).all()
    clusters: dict[str, list[models.NewsArticle]] = {}

    for article in articles:
        article_text = f"{article.title} {article.content or ''}"
        cluster_key = None
        for existing_key, members in clusters.items():
            representative = members[0]
            representative_text = f"{representative.title} {representative.content or ''}"
            if similarity(article_text, representative_text) >= 0.42:
                cluster_key = existing_key
                break
        if not cluster_key:
            cluster_key = hashlib.sha1(article_text.encode("utf-8")).hexdigest()[:16]
            clusters[cluster_key] = []
        clusters[cluster_key].append(article)

    for cluster_key, members in clusters.items():
        owners = {
            (member.source_owner or member.source or "Unknown").strip()
            for member in members
            if member.source_owner or member.source
        }
        for member in members:
            member.cluster_id = cluster_key
            member.consensus_group_count = len(owners)
            member.consensus_valid = len(owners) >= 3


def update_politician_scores(db, politician_id: str) -> None:
    politician = db.query(models.Politician).filter(models.Politician.id == politician_id).first()
    if not politician:
        return

    articles = db.query(models.NewsArticle).filter(models.NewsArticle.politician_id == politician_id).all()
    axis_impacts: dict[str, list[float]] = defaultdict(list)

    for article in articles:
        multiplier = 1.0 if article.consensus_valid else 0.55
        for impact in article.scores_impact or []:
            score_key = AXIS_TO_SCORE_KEY.get(impact.get("axis"))
            if not score_key:
                continue
            axis_impacts[score_key].append(float(impact.get("impact_score", 0)) * multiplier)

    current = politician.scores or {}
    next_scores = {}
    for score_key in WEIGHTS:
        values = axis_impacts.get(score_key)
        if values:
            average_impact = sum(values) / len(values)
            next_scores[score_key] = round(max(0.0, min(10.0, 5.0 + average_impact / 2.0)), 1)
        else:
            next_scores[score_key] = float(current.get(score_key, 5.0))

    politician.scores = next_scores
    politician.icp_score = round(sum(next_scores[key] * weight for key, weight in WEIGHTS.items()), 1)
    if politician.icp_score < 4.5:
        politician.sentinel_status = "Warning"
    elif politician.icp_score >= 7.0:
        politician.sentinel_status = "Safe"
    else:
        politician.sentinel_status = "Neutral"
