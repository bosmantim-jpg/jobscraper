# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JobScraper is a Python web scraper that reads a list of companies from `companies.xlsx`, visits their career pages, converts the HTML to Markdown, and uses Claude AI to extract structured job listing data. Results are persisted in a JSON database (`jobs_db.json`) for tracking changes across runs.

## Setup & Configuration

### Initial Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate

# Install dependencies (includes dev tools)
pip install -r requirements.txt

# Install Playwright browsers (one-time)
playwright install chromium
```

### API Key Setup
Create a `.env` file at the repo root:
```
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```
This file is gitignored and not tracked in git.

## Common Development Tasks

**Run the scraper:**
```bash
python -m jobscraper.main
```
Produces `output/jobs_YYYY-MM-DD.xlsx` and updates `jobs_db.json`.

**Run all tests:**
```bash
pytest
```

**Run tests with coverage report:**
```bash
pytest --cov=src --cov-report=html
```

**Run a single test:**
```bash
pytest tests/test_scraper.py::test_scraper_init -v
```

**Code formatting & linting:**
```bash
black src tests
flake8 src tests
```

## Architecture

### Core Modules

- **`scraper.py`** — Main orchestrator (JobScraper class)
  - Loads `companies.xlsx`
  - Fetches each career page HTML (with Playwright fallback for JS-rendered pages)
  - Converts HTML → Markdown via `markdownify`
  - Calls Claude API to extract job data
  - Exports results to Excel

- **`storage.py`** — Persistence layer
  - `load_db()` / `save_db()` — JSON database operations
  - `JobPosting` TypedDict — Structured job data model
  - `diff_and_update()` — Detects new/closed jobs across runs
  - `make_job_id()` — Generates stable IDs using SHA1(company + title + url)

- **`ai_extractor.py`** — Claude API integration
  - `extract_jobs_from_markdown()` — Calls Claude with `tool_use` for structured extraction
  - Tool schema enforces consistent job data format
  - Returns: title, location, salary, url per job
  - Resolves relative URLs against the career page base URL

- **`main.py`** — Entry point
  - Loads `.env` via `python-dotenv`
  - Configures logging
  - Instantiates and runs JobScraper

### Data Flow

1. Read companies from Excel → Fetch HTML → Markdown → Claude extraction
2. Diff new jobs against persistent DB → Mark closed jobs → Update timestamps
3. Export all jobs (open + closed) to dated Excel file

### Database Schema (`jobs_db.json`)

```json
{
  "a3f9c1e2b5": {
    "id": "a3f9c1e2b5",
    "company": "Acme Corp",
    "category": "Technology",
    "title": "Senior Engineer",
    "location": "Remote",
    "salary": "$150k-$180k",
    "url": "https://jobs.acme.com/senior-engineer",
    "status": "open",
    "first_seen": "2026-06-21",
    "last_seen": "2026-06-21",
    "closed_date": null
  }
}
```

## ATS API Support

The scraper supports direct API integration with major Applicant Tracking Systems (ATS):

**Supported ATS Systems:**
- **Greenhouse** — URLs containing `greenhouse` or `boards.greenhouse.io`
  - API: `https://boards.greenhouse.io/api/v1/boards/{company}/jobs`
  - Fastest extraction (direct JSON API)

- **Lever** — URLs containing `lever` (e.g., `company.lever.co`)
  - API: `https://api.lever.co/v1/postings/{company}`
  - Includes full job details and application URLs

- **Workday** — URLs with `myworkdayjobs.com` (e.g., `company.wd5.myworkdayjobs.com`)
  - API: `https://company.wd{instance}.myworkdayjobs.com/wday/cxs/{company}/en-US/jobs`
  - Extracts jobs without browser rendering

**Extraction Strategy:**
1. **Check for ATS** — If URL matches known ATS pattern, use API directly
2. **Use HTML+AI** — For custom career pages, fetch HTML and use Claude for extraction
3. **Fallback** — If HTML too sparse, retry with Playwright browser rendering

**Benefits of ATS APIs:**
- No AI token usage (saves cost)
- Faster extraction (direct JSON, no markdown conversion)
- More reliable location/title parsing (structured data)
- Works for hidden/JavaScript-rendered jobs

**Current Analysis (companies.xlsx):**
- 2 Workday companies
- 1 Lever company
- 153 custom career pages (use HTML+AI method)

## Important Notes

- **Atomic writes**: Database writes to `.tmp` file then atomically replaced to prevent corruption
- **companies.xlsx** is tracked in git — it's the source data
- **jobs_db.json** should be tracked to see diff history across runs
- **output/** directory is gitignored; contains dated Excel exports
- **Markdown truncation**: Limited to 50,000 chars before API call to control token cost
- **Model**: Uses `claude-haiku-4-5-20251001` (cheapest tier, suitable for structured extraction)

## Key Files for Modifications

- **src/jobscraper/scraper.py** — Add new fetch strategies or HTML preprocessing
- **src/jobscraper/ai_extractor.py** — Modify the Claude prompt or tool schema
- **src/jobscraper/storage.py** — Adjust job fields or diffing logic
- **companies.xlsx** — Add/remove companies or fix career page URLs
