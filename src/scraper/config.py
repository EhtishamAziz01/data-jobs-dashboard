"""
Configuration for the Ireland Jobs Dashboard project.
Contains search terms, skill dictionaries, and scraper settings.
"""

import json
import os

# ============================================================
# Paths
# ============================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_RAW = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
DATA_REFERENCE = os.path.join(PROJECT_ROOT, "data", "reference")
DATABASE_PATH = os.path.join(PROJECT_ROOT, "data", "ireland_jobs.duckdb")

# ============================================================
# Search Configuration
# ============================================================
SEARCH_QUERIES = [
    "data analyst",
    "junior data analyst",
    "data scientist",
    "junior data scientist",
    "data engineer",
    "junior data engineer",
    "business analyst data",
    "BI analyst",
    "analytics engineer",
    "business intelligence analyst",
]

LOCATIONS = [
    "Ireland",
    "Dublin",
    "Cork",
    "Galway",
    "Limerick",
]

# ============================================================
# Indeed Scraper Settings
# ============================================================
INDEED_BASE_URL = "https://ie.indeed.com"
RESULTS_PER_PAGE = 15
MAX_PAGES_PER_QUERY = 3  # 3 pages × 15 results = ~45 per query
REQUEST_DELAY = (2, 5)  # Random delay range in seconds between requests

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ============================================================
# Title Standardization
# ============================================================
TITLE_CATEGORIES = {
    "Data Analyst": ["data analyst", "analyst data", "analytics analyst", "reporting analyst"],
    "Data Scientist": ["data scientist", "data science", "machine learning engineer", "ml engineer"],
    "Data Engineer": ["data engineer", "etl developer", "data pipeline", "big data engineer"],
    "BI Analyst": ["bi analyst", "business intelligence analyst", "bi developer", "power bi analyst", "tableau analyst"],
    "Business Analyst": ["business analyst", "business data analyst"],
    "Analytics Engineer": ["analytics engineer", "analytical engineer"],
    "ML Engineer": ["machine learning engineer", "ml engineer", "mlops engineer", "ai engineer"],
}

# ============================================================
# Location Standardization
# ============================================================
CITY_MAPPINGS = {
    "dublin": "Dublin",
    "cork": "Cork",
    "galway": "Galway",
    "limerick": "Limerick",
    "waterford": "Waterford",
    "belfast": "Belfast",
    "kilkenny": "Kilkenny",
    "athlone": "Athlone",
    "dundalk": "Dundalk",
    "drogheda": "Drogheda",
    "wexford": "Wexford",
    "sligo": "Sligo",
    "letterkenny": "Letterkenny",
    "ennis": "Ennis",
    "tralee": "Tralee",
    "carlow": "Carlow",
    "remote": "Remote",
    "hybrid": "Hybrid",
}

# ============================================================
# Skill Keywords
# ============================================================
def load_skill_keywords():
    """Load skill keywords from the reference JSON file."""
    path = os.path.join(DATA_REFERENCE, "skill_keywords.json")
    with open(path, "r") as f:
        return json.load(f)
