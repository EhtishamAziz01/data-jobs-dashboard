"""
Utility functions for scrapers: rate limiting, headers, CSV I/O, logging.
"""

import csv
import os
import random
import time
import logging
from datetime import datetime

from .config import USER_AGENTS, REQUEST_DELAY, DATA_RAW

# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_random_headers():
    """Return HTTP headers with a random user agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def rate_limit():
    """Sleep for a random duration to avoid being blocked."""
    delay = random.uniform(*REQUEST_DELAY)
    logger.debug(f"Rate limiting: sleeping {delay:.1f}s")
    time.sleep(delay)


def save_jobs_to_csv(jobs: list[dict], filename: str = None) -> str:
    """
    Save a list of job dictionaries to a CSV file in data/raw/.

    Args:
        jobs: List of job dictionaries with consistent keys.
        filename: Optional filename. If None, generates a timestamped name.

    Returns:
        Path to the saved CSV file.
    """
    if not jobs:
        logger.warning("No jobs to save.")
        return ""

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jobs_raw_{timestamp}.csv"

    filepath = os.path.join(DATA_RAW, filename)
    os.makedirs(DATA_RAW, exist_ok=True)

    fieldnames = jobs[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

    logger.info(f"Saved {len(jobs)} jobs to {filepath}")
    return filepath
