import json
import subprocess
import sys
import tempfile
from hashlib import sha1
from pathlib import Path
from urllib.parse import urlparse

import scrapy

from config import settings


MEDIA_OWNER_MAP = {
    "antara": "LKBN Antara",
    "kompas": "Kompas Gramedia",
    "metro tv": "Media Group",
    "metrotv": "Media Group",
    "okezone": "MNC Group",
    "tempo": "Tempo Media Group",
    "detik": "CT Corp",
    "cnn indonesia": "Trans Media",
    "cnbc indonesia": "Trans Media",
    "tribun": "Kompas Gramedia",
    "babel insight": "Babel Insight",
}


def source_owner(source: str | None) -> str:
    normalized = (source or "").lower()
    for key, owner in MEDIA_OWNER_MAP.items():
        if key in normalized:
            return owner
    return source or "Unknown"


class RaporPejabatSpider(scrapy.Spider):
    name = "rapor_pejabat_news"

    custom_settings = {
        "LOG_LEVEL": "INFO",
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_TIMEOUT": 20,
        "USER_AGENT": settings.SCRAPER_USER_AGENT,
    }

    def __init__(
        self,
        politician_name: str = "",
        seed_path: str = "",
        start_urls_csv: str = "",
        allowed_domains_csv: str = "",
        limit: str = "25",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.politician_name = politician_name
        self.seed_path = seed_path
        self.limit = int(limit or 25)
        self._seen = 0

        urls = [url.strip() for url in start_urls_csv.split(",") if url.strip()]
        if seed_path:
            urls.insert(0, Path(seed_path).resolve().as_uri())
        self.start_urls = urls

        allowed_domains = [domain.strip() for domain in allowed_domains_csv.split(",") if domain.strip()]
        if allowed_domains:
            self.allowed_domains = allowed_domains

    def parse(self, response):
        if response.url.startswith("file://"):
            yield from self.parse_seed(response)
            return
        yield self.parse_article(response)

    def parse_seed(self, response):
        try:
            records = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.warning("Seed file is not valid JSON: %s", response.url)
            return

        for record in records:
            if self._seen >= self.limit:
                break
            if self.politician_name and record.get("politician") != self.politician_name:
                continue
            self._seen += 1
            title = record.get("title") or ""
            content = record.get("content") or ""
            source = record.get("source") or "Seed Data"
            yield {
                "id": record.get("id") or sha1(f"{title}{content}".encode("utf-8")).hexdigest(),
                "politician_name": record.get("politician") or self.politician_name,
                "title": title,
                "content": content,
                "source": source,
                "source_owner": source_owner(source),
                "url": record.get("url"),
                "published_at": record.get("published_at") or record.get("date"),
                "raw_payload": record,
            }

    def parse_article(self, response):
        title = (
            response.css("meta[property='og:title']::attr(content)").get()
            or response.css("h1::text").get()
            or response.css("title::text").get()
            or ""
        ).strip()
        paragraphs = [part.strip() for part in response.css("article p::text, main p::text, p::text").getall()]
        content = " ".join(part for part in paragraphs if part)
        source = (
            response.css("meta[property='og:site_name']::attr(content)").get()
            or urlparse(response.url).netloc.replace("www.", "")
        )
        published_at = (
            response.css("meta[property='article:published_time']::attr(content)").get()
            or response.css("time::attr(datetime)").get()
        )
        haystack = f"{title} {content}".lower()
        if self.politician_name and self.politician_name.lower() not in haystack:
            return None

        return {
            "id": sha1(response.url.encode("utf-8")).hexdigest(),
            "politician_name": self.politician_name,
            "title": title,
            "content": content,
            "source": source,
            "source_owner": source_owner(source),
            "url": response.url,
            "published_at": published_at,
            "raw_payload": {"status": response.status},
        }


def run_scrapy_job(
    politician_name: str,
    seed_path: str | None = None,
    urls: list[str] | None = None,
    allowed_domains: list[str] | None = None,
    limit: int | None = None,
) -> list[dict]:
    urls = urls or []
    allowed_domains = allowed_domains or [
        domain.strip() for domain in settings.SCRAPER_ALLOWED_DOMAINS.split(",") if domain.strip()
    ]
    limit = limit or settings.SCRAPER_LIMIT

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as output_file:
        output_path = Path(output_file.name)

    cmd = [
        sys.executable,
        "-m",
        "scrapy",
        "runspider",
        str(Path(__file__).resolve()),
        "-a",
        f"politician_name={politician_name}",
        "-a",
        f"limit={limit}",
        "-O",
        str(output_path),
    ]
    if seed_path:
        cmd.extend(["-a", f"seed_path={seed_path}"])
    if urls:
        cmd.extend(["-a", f"start_urls_csv={','.join(urls)}"])
    if allowed_domains:
        cmd.extend(["-a", f"allowed_domains_csv={','.join(allowed_domains)}"])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=Path(__file__).resolve().parent)
        if not output_path.exists() or output_path.stat().st_size == 0:
            return []
        with output_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    finally:
        output_path.unlink(missing_ok=True)
