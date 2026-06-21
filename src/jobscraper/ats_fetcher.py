"""ATS (Applicant Tracking System) API integrations for direct job fetching."""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class ATSFetcher:
    """Base class for ATS API fetchers."""

    def fetch_jobs(self, url: str) -> List[Dict[str, Any]]:
        """Fetch jobs from ATS API. Returns list of job dicts."""
        raise NotImplementedError


class GreenhouseAPI(ATSFetcher):
    """Greenhouse job board API."""

    @staticmethod
    def extract_board_token(url: str) -> Optional[str]:
        """Extract Greenhouse board token from URL."""
        # URLs like: https://boards.greenhouse.io/api/v1/boards/company/jobs
        if "boards.greenhouse.io" in url:
            parts = url.split("/")
            if "boards" in parts and "jobs" in parts:
                board_idx = parts.index("boards")
                if board_idx + 1 < len(parts):
                    return parts[board_idx + 1]
        return None

    def fetch_jobs(self, url: str) -> List[Dict[str, Any]]:
        """Fetch jobs from Greenhouse API."""
        try:
            # If given a standard Greenhouse URL, extract the board token
            if "boards.greenhouse.io" not in url:
                # Try to infer: check if company name is in the companies.xlsx
                logger.debug(f"URL doesn't look like Greenhouse API: {url}")
                return []

            # Use the URL as-is if it's already an API endpoint
            if "/api/v1/" in url:
                api_url = url if url.endswith("/jobs") else f"{url}/jobs"
            else:
                board = self.extract_board_token(url)
                if not board:
                    return []
                api_url = f"https://boards.greenhouse.io/api/v1/boards/{board}/jobs"

            resp = requests.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            jobs = []
            for job in data.get("jobs", []):
                jobs.append(
                    {
                        "title": job.get("title", ""),
                        "location": job.get("location", {}).get("name") if job.get("location") else None,
                        "salary": None,
                        "url": job.get("absolute_url", ""),
                    }
                )

            logger.info(f"Greenhouse API: fetched {len(jobs)} jobs")
            return jobs

        except requests.RequestException as e:
            logger.debug(f"Greenhouse API error: {e}")
            return []
        except Exception as e:
            logger.debug(f"Greenhouse parsing error: {e}")
            return []


class LeverAPI(ATSFetcher):
    """Lever job board API."""

    @staticmethod
    def extract_company_id(url: str) -> Optional[str]:
        """Extract Lever company ID from URL."""
        # URLs like: https://api.lever.co/v1/postings/company or
        # https://company.lever.co/jobs or similar
        if "lever" in url.lower():
            # Try parsing domain
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # lever.co domain: extract subdomain
            if "lever.co" in domain:
                subdomain = domain.split(".")[0]
                if subdomain and subdomain not in ["api", "www"]:
                    return subdomain

            # API path: extract from path
            if "/postings/" in url:
                parts = url.split("/postings/")
                if len(parts) > 1:
                    return parts[1].split("/")[0]

        return None

    def fetch_jobs(self, url: str) -> List[Dict[str, Any]]:
        """Fetch jobs from Lever API."""
        try:
            company = self.extract_company_id(url)
            if not company:
                logger.debug(f"Could not extract Lever company ID from: {url}")
                return []

            api_url = f"https://api.lever.co/v1/postings/{company}?include=content"

            resp = requests.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            jobs = []
            for job in data.get("data", []):
                location_parts = []
                if job.get("location"):
                    location_parts.append(job["location"])
                if job.get("locationPlain"):
                    location_parts.append(job["locationPlain"])

                jobs.append(
                    {
                        "title": job.get("text", ""),
                        "location": ", ".join(location_parts) if location_parts else None,
                        "salary": None,
                        "url": job.get("links", {}).get("show", "") if job.get("links") else "",
                    }
                )

            logger.info(f"Lever API: fetched {len(jobs)} jobs")
            return jobs

        except requests.RequestException as e:
            logger.debug(f"Lever API error: {e}")
            return []
        except Exception as e:
            logger.debug(f"Lever parsing error: {e}")
            return []


class WorkdayAPI(ATSFetcher):
    """Workday job board API."""

    @staticmethod
    def extract_workday_id(url: str) -> Optional[tuple]:
        """Extract Workday instance and organization ID from URL."""
        # URLs like: https://company.wd1.myworkdayjobs.com/en-US/External?...
        # or https://company.wd5.myworkdayjobs.com/en/jobs?...
        if "myworkdayjobs.com" in url:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Extract company and instance (wd1, wd5, etc.)
            if ".wd" in domain:
                parts = domain.split(".wd")
                company = parts[0]
                instance = "wd" + parts[1].split(".")[0]
                return (company, instance)
        return None

    def fetch_jobs(self, url: str) -> List[Dict[str, Any]]:
        """Fetch jobs from Workday.

        Note: Workday doesn't have a simple public JSON API for jobs.
        This attempts to extract from the job listing page or use
        Workday's undocumented API endpoint.
        """
        try:
            ids = self.extract_workday_id(url)
            if not ids:
                logger.debug(f"Could not parse Workday URL: {url}")
                return []

            company, instance = ids

            # Workday's unofficial JSON API endpoint
            # This may break in future updates
            api_url = (
                f"https://{company}.{instance}.myworkdayjobs.com/wday/cxs/"
                f"{company}/en-US/jobs"
            )

            resp = requests.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            jobs = []
            for job in data.get("jobPostings", []):
                jobs.append(
                    {
                        "title": job.get("title", ""),
                        "location": job.get("location", ""),
                        "salary": None,
                        "url": job.get("externalJobPostingUrl", ""),
                    }
                )

            logger.info(f"Workday API: fetched {len(jobs)} jobs")
            return jobs

        except requests.RequestException as e:
            logger.debug(f"Workday API error: {e}")
            return []
        except Exception as e:
            logger.debug(f"Workday parsing error: {e}")
            return []


def detect_and_fetch_from_ats(url: str) -> Optional[List[Dict[str, Any]]]:
    """
    Detect ATS type from URL and fetch jobs using the appropriate API.
    Returns None if no ATS API is available (fallback to HTML fetching).
    Returns empty list if ATS detected but no jobs found.
    """
    if not url:
        return None

    url_lower = url.lower()

    # Detect Greenhouse
    if "greenhouse" in url_lower:
        fetcher = GreenhouseAPI()
        jobs = fetcher.fetch_jobs(url)
        if jobs is not None:
            return jobs

    # Detect Lever
    if "lever" in url_lower:
        fetcher = LeverAPI()
        jobs = fetcher.fetch_jobs(url)
        if jobs is not None:
            return jobs

    # Detect Workday
    if "myworkdayjobs.com" in url_lower or "wd5.myworkday" in url_lower or "wd1.myworkday" in url_lower:
        fetcher = WorkdayAPI()
        jobs = fetcher.fetch_jobs(url)
        if jobs is not None:
            return jobs

    # No recognized ATS - return None to trigger HTML fallback
    return None
