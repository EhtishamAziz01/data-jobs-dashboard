#!/usr/bin/env python3
"""
Main entry point for the job scraper.

Runs the Indeed.ie scraper across all configured search queries and locations,
then saves the combined results to a CSV file in data/raw/.

If scraping fails (e.g., anti-bot protection), falls back to generating
realistic sample data for pipeline development.

Usage:
    python -m src.scraper.run_scraper                # Try live scraping
    python -m src.scraper.run_scraper --sample        # Generate sample data
    python -m src.scraper.run_scraper --sample --n 500  # Generate 500 sample rows
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.config import SEARCH_QUERIES, LOCATIONS
from src.scraper.indeed_scraper import scrape_indeed
from src.scraper.sample_data import generate_sample_jobs
from src.scraper.utils import save_jobs_to_csv, logger


def run_live_scraper() -> list[dict]:
    """Run the live Indeed.ie scraper."""
    all_jobs = []

    for query in SEARCH_QUERIES:
        for location in LOCATIONS[:2]:  # Start with Ireland + Dublin
            try:
                jobs = scrape_indeed(query, location)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Scraping failed for '{query}' in '{location}': {e}")

    return all_jobs


def main():
    parser = argparse.ArgumentParser(description="Ireland Jobs Data Collector")
    parser.add_argument("--sample", action="store_true", help="Generate sample data instead of scraping")
    parser.add_argument("--n", type=int, default=800, help="Number of sample jobs to generate (default: 800)")
    args = parser.parse_args()

    if args.sample:
        logger.info(f"Generating {args.n} sample job listings...")
        jobs = generate_sample_jobs(n=args.n)
    else:
        logger.info("Starting live scrape of Indeed.ie...")
        jobs = run_live_scraper()

        if len(jobs) < 50:
            logger.warning(f"Only scraped {len(jobs)} jobs. Falling back to sample data.")
            jobs = generate_sample_jobs(n=args.n)

    if jobs:
        filepath = save_jobs_to_csv(jobs, "jobs_raw.csv")
        logger.info(f"✅ Data collection complete: {len(jobs)} jobs saved to {filepath}")
    else:
        logger.error("❌ No jobs collected. Check your connection and try again.")


if __name__ == "__main__":
    main()
