"""AI extraction of job postings using Claude API."""

import json
import logging
from typing import Any, Dict
from urllib.parse import urljoin, urlparse

import anthropic

logger = logging.getLogger(__name__)

TOOL_DEFINITION = {
    "name": "extract_jobs",
    "description": "Extract all job postings found on the careers page.",
    "input_schema": {
        "type": "object",
        "properties": {
            "jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "location": {"type": ["string", "null"]},
                        "salary": {"type": ["string", "null"]},
                        "url": {"type": "string"},
                    },
                    "required": ["title", "url"],
                },
            }
        },
        "required": ["jobs"],
    },
}


def extract_jobs_from_markdown(
    markdown: str,
    company_name: str,
    career_page_url: str,
) -> list[Dict[str, Any]]:
    """
    Call Claude to extract structured job postings from markdown content.
    Returns a list of dicts with keys: title, location, salary, url.
    Returns [] on failure.
    """
    client = anthropic.Anthropic()

    system_prompt = (
        "You are a job posting extractor. Your task is to find and extract ALL job "
        "postings from the provided career page content. \n\n"
        "IMPORTANT: Look for ANY of these patterns:\n"
        "- Job titles followed by location or 'Apply now' links\n"
        "- Tables or lists with role names\n"
        "- Job postings that mention responsibilities or requirements\n"
        "- Positions marked with tags like [Open], [Hiring], or similar\n"
        "- Even brief job listings (just title + link)\n\n"
        "Extract ALL job postings you can find. Do not be conservative - include "
        "any role that appears to be a job opening, even if incomplete details are "
        "provided. Use the extract_jobs tool to return the data. Return an empty "
        "list only if there are clearly NO job postings on the page."
    )

    user_prompt = (
        f"Company: {company_name}\n"
        f"Career page URL: {career_page_url}\n"
        f"(Resolve relative URLs using this base URL)\n\n"
        f"Extract all job postings from this content:\n"
        f"{markdown}"
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            tools=[TOOL_DEFINITION],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "extract_jobs":
                jobs = block.input.get("jobs", [])
                # Resolve relative URLs
                jobs = [
                    {
                        **job,
                        "url": _resolve_url(job.get("url", ""), career_page_url),
                    }
                    for job in jobs
                ]
                logger.debug(f"Extracted {len(jobs)} jobs for {company_name}")
                return jobs

        logger.warning(f"No tool_use response from Claude for {company_name}")
        return []

    except anthropic.APIError as e:
        logger.error(f"API error extracting jobs for {company_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error extracting jobs for {company_name}: {e}")
        return []


def _resolve_url(url: str, base_url: str) -> str:
    """Resolve relative URLs against a base URL."""
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    try:
        return urljoin(base_url, url)
    except Exception:
        return url
