"""Tests for the scraper module."""

from jobscraper.scraper import JobScraper


def test_scraper_init():
    """Test JobScraper initialization."""
    scraper = JobScraper()
    assert scraper.jobs == []


def test_fetch_jobs():
    """Test fetching jobs."""
    scraper = JobScraper()
    jobs = scraper.fetch_jobs()
    assert isinstance(jobs, list)
