"""Main entry point for the job scraper application."""

from .scraper import JobScraper


def main():
    """Run the job scraper."""
    scraper = JobScraper()
    scraper.run()


if __name__ == "__main__":
    main()
