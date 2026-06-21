"""Storage and persistence logic for job postings."""

import hashlib
import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict

logger = logging.getLogger(__name__)

DB_PATH = Path("jobs_db.json")


class JobPosting(TypedDict):
    """A job posting with metadata."""

    id: str
    company: str
    category: str
    title: str
    location: Optional[str]
    salary: Optional[str]
    url: str
    status: str
    first_seen: str
    last_seen: str
    closed_date: Optional[str]


def load_db() -> Dict[str, JobPosting]:
    """Load jobs database from JSON file. Returns {} if file doesn't exist."""
    if not DB_PATH.exists():
        logger.info("Database not found, starting fresh")
        return {}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        logger.info(f"Loaded {len(db)} jobs from {DB_PATH}")
        return db
    except Exception as e:
        logger.error(f"Failed to load database: {e}")
        return {}


def save_db(db: Dict[str, JobPosting]) -> None:
    """Save jobs database to JSON file atomically."""
    tmp_path = DB_PATH.with_suffix(".json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, DB_PATH)
        logger.info(f"Saved {len(db)} jobs to {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to save database: {e}")
        if tmp_path.exists():
            tmp_path.unlink()


def make_job_id(company: str, title: str, url: str) -> str:
    """Generate a stable job ID from company, title, and URL."""
    composite = f"{company.lower().strip()}|{title.lower().strip()}|{url.lower().strip()}"
    return hashlib.sha1(composite.encode()).hexdigest()[:16]


def diff_and_update(
    db: Dict[str, JobPosting],
    company: str,
    category: str,
    fetched_jobs: list[Dict[str, Any]],
    today: str,
) -> tuple[int, int, int]:
    """
    Diff fetched jobs against stored DB and update in-place.
    Returns (new_count, closed_count, unchanged_count).
    """
    # Build current job IDs from fetched jobs
    current_ids = set()
    for job in fetched_jobs:
        job_id = make_job_id(company, job["title"], job["url"])
        current_ids.add(job_id)

        if job_id not in db:
            # New job
            posting: JobPosting = {
                "id": job_id,
                "company": company,
                "category": category,
                "title": job["title"],
                "location": job.get("location"),
                "salary": job.get("salary"),
                "url": job["url"],
                "status": "open",
                "first_seen": today,
                "last_seen": today,
                "closed_date": None,
            }
            db[job_id] = posting
        else:
            # Existing job, update last_seen
            db[job_id]["last_seen"] = today
            if db[job_id]["status"] == "closed":
                db[job_id]["status"] = "open"
                db[job_id]["closed_date"] = None

    # Find jobs for this company that are no longer in the fetched list
    company_job_ids = {
        job_id for job_id, job in db.items() if job["company"] == company
    }
    stored_active_ids = {
        job_id for job_id in company_job_ids if db[job_id]["status"] == "open"
    }

    closed_ids = stored_active_ids - current_ids
    for job_id in closed_ids:
        db[job_id]["status"] = "closed"
        db[job_id]["closed_date"] = today

    new_ids = current_ids - stored_active_ids
    unchanged_ids = current_ids & stored_active_ids

    return len(new_ids), len(closed_ids), len(unchanged_ids)
