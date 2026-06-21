"""Core scraper module for fetching job listings."""

import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import markdownify
import pandas as pd
import requests

from .ai_extractor import extract_jobs_from_markdown
from .ats_fetcher import detect_and_fetch_from_ats
from .storage import JobPosting, diff_and_update, load_db, save_db

logger = logging.getLogger(__name__)


class JobScraper:
    """Main job scraper class."""

    def __init__(self):
        """Initialize the job scraper."""
        self.companies_file = Path("companies.xlsx")
        self.db: Dict[str, JobPosting] = load_db()
        self.jobs: List[Dict[str, Any]] = []

    def run(self):
        """Run the scraper and fetch job listings."""
        logger.info("Starting job scraper...")
        companies = self._load_companies()
        today = date.today().isoformat()
        total_new = total_closed = total_unchanged = 0

        for row in companies:
            company = row["Company"]
            careerpage = row["Job / Career Pagina"]
            category = row["Category"]

            if not careerpage or pd.isna(careerpage):
                logger.warning(f"No career page for {company}, skipping")
                continue

            logger.info(f"Scraping {company} — {careerpage}")

            # Try ATS API first (faster and more reliable)
            fetched_jobs = detect_and_fetch_from_ats(careerpage)
            method = "ATS API"

            if fetched_jobs is None:
                # Fall back to HTML fetching + AI extraction
                html = self._fetch_html(careerpage)
                if html is None:
                    continue

                markdown = self._html_to_markdown(html)
                fetched_jobs = extract_jobs_from_markdown(markdown, company, careerpage)
                method = "HTML + AI"

            logger.info(f"  [{method}] returned {len(fetched_jobs)} job(s)")

            new, closed, unchanged = diff_and_update(
                self.db, company, category, fetched_jobs, today
            )
            logger.info(f"  +{new} new, -{closed} closed, {unchanged} unchanged")
            total_new += new
            total_closed += closed
            total_unchanged += unchanged

        save_db(self.db)
        self._export_excel(today)
        logger.info(f"Done. Total: +{total_new} new, -{total_closed} closed")

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Fetch job listings from configured sources."""
        return list(self.db.values())

    def _load_companies(self) -> list[Dict[str, Any]]:
        """Load companies from Excel file."""
        try:
            df = pd.read_excel(self.companies_file)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Failed to load companies file: {e}")
            return []

    def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML from URL, with Playwright fallback for JS-heavy pages."""
        html = self._fetch_with_requests(url)
        if html is None:
            return None

        md_preview = markdownify.markdownify(html, strip=["script", "style"])
        content_length = len(md_preview.replace(" ", "").replace("\n", ""))

        if content_length < 500:
            logger.info("  Sparse HTML detected, retrying with Playwright...")
            html = self._fetch_with_playwright(url)

        return html

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch HTML using requests library."""
        try:
            resp = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch HTML using Playwright for JavaScript-rendered pages."""
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30_000)
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Playwright failed for {url}: {e}")
            return None

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown, truncating to control token cost."""
        md = markdownify.markdownify(
            html, strip=["script", "style", "head"], heading_style="ATX"
        )
        return md[:50_000]

    def _export_excel(self, today: str) -> None:
        """Export all jobs to dated Excel file."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        rows = list(self.db.values())
        if not rows:
            logger.info("No jobs to export")
            return

        df = pd.DataFrame(rows)
        output_file = output_dir / f"jobs_{today}.xlsx"
        df.to_excel(output_file, index=False)
        logger.info(f"Exported {len(rows)} jobs to {output_file}")
