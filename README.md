# JobScraper

A Python web scraper for collecting job listings from various job boards.

## Features

- Scrapes job listings from multiple sources
- Stores results in Excel format
- Extensible architecture for adding new job board sources

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src tests
flake8 src tests

# Type checking
mypy src
```

## Usage

```bash
python -m jobscraper.main
```

## Project Structure

- `src/jobscraper/` - Main application code
- `tests/` - Test suite
- `companies.xlsx` - Target companies list for job scraping

## License

MIT
