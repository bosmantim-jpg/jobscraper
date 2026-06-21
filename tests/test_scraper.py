"""Tests for the scraper module."""

from jobscraper.scraper import JobScraper
from jobscraper.storage import make_job_id


def test_scraper_init():
    """Test JobScraper initialization."""
    scraper = JobScraper()
    assert isinstance(scraper.db, dict)
    assert isinstance(scraper.jobs, list)


def test_fetch_jobs():
    """Test fetching jobs."""
    scraper = JobScraper()
    jobs = scraper.fetch_jobs()
    assert isinstance(jobs, list)


def test_make_job_id():
    """Test job ID generation is consistent."""
    id1 = make_job_id("Acme Corp", "Software Engineer", "https://acme.com/job/123")
    id2 = make_job_id("acme corp", "software engineer", "https://acme.com/job/123")
    assert id1 == id2
    assert len(id1) == 16
