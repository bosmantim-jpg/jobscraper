"""Main entry point for the job scraper application."""

import logging

from dotenv import load_dotenv

from .scraper import JobScraper


def main():
    """Run the job scraper."""
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    scraper = JobScraper()
    scraper.run()


if __name__ == "__main__":
    main()
