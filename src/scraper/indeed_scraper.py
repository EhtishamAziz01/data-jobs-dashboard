"""
Indeed.ie job scraper using BeautifulSoup.

Scrapes job listings from Indeed Ireland for data-related roles.
Handles pagination, rate limiting, and anti-bot protections gracefully.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from .config import INDEED_BASE_URL, RESULTS_PER_PAGE, MAX_PAGES_PER_QUERY
from .utils import get_random_headers, rate_limit, logger


def build_search_url(query: str, location: str, start: int = 0) -> str:
    """Build an Indeed search URL with the given parameters."""
    params = {
        "q": query,
        "l": location,
        "start": start,
        "sort": "date",
    }
    return f"{INDEED_BASE_URL}/jobs?{urlencode(params)}"


def parse_salary(salary_text: str) -> tuple[float | None, float | None]:
    """
    Extract min and max salary from text like '€35,000 - €45,000 a year'.
    Returns (salary_min, salary_max) or (None, None) if unparseable.
    """
    if not salary_text:
        return None, None

    salary_text = salary_text.lower().replace(",", "").replace("€", "").replace("eur", "")

    # Annualize hourly/daily/monthly rates
    multiplier = 1
    if "hour" in salary_text:
        multiplier = 2080  # 40hrs × 52 weeks
    elif "day" in salary_text:
        multiplier = 260  # 5 days × 52 weeks
    elif "month" in salary_text:
        multiplier = 12
    elif "week" in salary_text:
        multiplier = 52

    numbers = re.findall(r"[\d.]+", salary_text)
    numbers = [float(n) * multiplier for n in numbers]

    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    elif len(numbers) == 1:
        return numbers[0], numbers[0]
    return None, None


def scrape_indeed_page(url: str) -> list[dict]:
    """
    Scrape a single Indeed search results page.
    Returns a list of job dictionaries.
    """
    jobs = []

    try:
        response = requests.get(url, headers=get_random_headers(), timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return jobs

    soup = BeautifulSoup(response.text, "html.parser")

    # Indeed uses various card containers — try multiple selectors
    job_cards = soup.select("div.job_seen_beacon") or soup.select("div.jobsearch-ResultsList > div")

    if not job_cards:
        logger.warning(f"No job cards found on page: {url}")
        return jobs

    for card in job_cards:
        try:
            # Title
            title_elem = card.select_one("h2.jobTitle a") or card.select_one("a[data-jk]")
            title = title_elem.get_text(strip=True) if title_elem else None

            # Job URL
            job_url = None
            if title_elem and title_elem.get("href"):
                href = title_elem["href"]
                job_url = href if href.startswith("http") else f"{INDEED_BASE_URL}{href}"

            # Company
            company_elem = card.select_one("span.css-63koeb") or card.select_one("[data-testid='company-name']")
            company = company_elem.get_text(strip=True) if company_elem else None

            # Location
            location_elem = card.select_one("div.css-1p0sjhy") or card.select_one("[data-testid='text-location']")
            location = location_elem.get_text(strip=True) if location_elem else None

            # Salary
            salary_elem = card.select_one("div.salary-snippet-container") or card.select_one("[data-testid='attribute_snippet_testid']")
            salary_text = salary_elem.get_text(strip=True) if salary_elem else None
            salary_min, salary_max = parse_salary(salary_text)

            # Description snippet
            desc_elem = card.select_one("div.css-9446fg") or card.select_one("ul")
            description = desc_elem.get_text(strip=True) if desc_elem else None

            if title:  # Only add if we at least have a title
                jobs.append({
                    "job_title": title,
                    "company": company,
                    "location": location,
                    "salary_text": salary_text,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "description": description,
                    "url": job_url,
                    "source": "indeed.ie",
                })
        except Exception as e:
            logger.debug(f"Error parsing job card: {e}")
            continue

    logger.info(f"Scraped {len(jobs)} jobs from {url}")
    return jobs


def scrape_indeed(query: str, location: str = "Ireland") -> list[dict]:
    """
    Scrape multiple pages of Indeed results for a given query and location.
    """
    all_jobs = []

    for page in range(MAX_PAGES_PER_QUERY):
        start = page * RESULTS_PER_PAGE
        url = build_search_url(query, location, start)
        logger.info(f"Scraping: query='{query}', location='{location}', page={page + 1}")

        page_jobs = scrape_indeed_page(url)

        if not page_jobs:
            logger.info(f"No more results for '{query}' at page {page + 1}. Stopping.")
            break

        all_jobs.extend(page_jobs)
        rate_limit()

    logger.info(f"Total for '{query}' in '{location}': {len(all_jobs)} jobs")
    return all_jobs
