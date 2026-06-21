# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JobScraper is a Python web scraper application for collecting job listings. The project uses a modular architecture with separate concerns for scraping, data processing, and output.

## Setup & Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Common Development Tasks

**Run the scraper:**
```bash
python -m jobscraper.main
```

**Run all tests:**
```bash
pytest
```

**Run tests with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Run a single test:**
```bash
pytest tests/test_scraper.py::test_scraper_init -v
```

**Code formatting:**
```bash
black src tests
```

**Linting:**
```bash
flake8 src tests
```

**Type checking:**
```bash
mypy src
```

## Architecture

### Directory Structure
- **src/jobscraper/** - Main application package
  - `main.py` - Entry point that orchestrates scraping
  - `scraper.py` - Core JobScraper class responsible for fetching and processing jobs
- **tests/** - Test suite (mirrors src/ structure)
- **companies.xlsx** - Input file containing target companies

### Design Patterns

The project follows a simple, single-responsibility architecture:
- **JobScraper class** - Handles job fetching and storage logic
- Extensible for adding multiple source scrapers as methods or separate classes
- Output is stored as a list of dictionaries, ready for export to Excel or other formats

### Key Technologies
- **requests** - HTTP requests for web scraping
- **BeautifulSoup4** - HTML parsing
- **pandas** - Data manipulation and Excel export
- **pytest** - Testing framework

## Important Notes

- The `companies.xlsx` file is tracked in git (not in .gitignore) as it's project data
- The `.gitignore` ignores any generated output files in `output/` directory
- All scrapers should follow consistent job object structure (dict with keys: title, company, url, etc.)
- Virtual environment (`venv/`) is gitignored

## Test Patterns

- Tests are located in `tests/` with filenames matching `test_*.py`
- Use pytest fixtures for setup/teardown
- Aim for coverage of core JobScraper methods and individual scraper implementations
