#!/usr/bin/env python3
"""
Kaggle dataset ingestion adapter.

Loads real job data from Kaggle datasets and converts it to our pipeline's
expected format (matching the columns from the scraper output).

Supports two datasets:
1. LinkedIn Job Postings (arshkon/linkedin-job-postings) — full descriptions + skills
2. Jobs in Data (hummaamqaasim/jobs-in-data) — structured salary data

Usage:
    python -m src.scraper.kaggle_adapter
    python -m src.scraper.kaggle_adapter --source linkedin --limit 2000
    python -m src.scraper.kaggle_adapter --source salary
"""

import argparse
import os
import sys
import re

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.config import DATA_RAW
from src.scraper.utils import logger

# ============================================================
# Kaggle Dataset Paths (via kagglehub)
# ============================================================
LINKEDIN_BASE = os.path.expanduser(
    "~/.cache/kagglehub/datasets/arshkon/linkedin-job-postings/versions/13"
)
SALARY_BASE = os.path.expanduser(
    "~/.cache/kagglehub/datasets/hummaamqaasim/jobs-in-data/versions/6"
)

# Data role keywords for filtering the LinkedIn dataset
DATA_ROLE_KEYWORDS = [
    "data analyst", "data scientist", "data engineer", "business intelligence",
    "bi analyst", "bi developer", "analytics engineer", "machine learning",
    "ml engineer", "etl", "data pipeline", "business analyst data",
    "reporting analyst", "power bi", "tableau", "analytics", "data",
]


def load_linkedin_data(limit: int = 2000) -> pd.DataFrame:
    """
    Load and filter LinkedIn job postings for data-related roles.

    Filters 3.3M postings down to data roles, enriches with salary data,
    and converts to our pipeline format.
    """
    logger.info("Loading LinkedIn Job Postings dataset...")

    postings_path = os.path.join(LINKEDIN_BASE, "postings.csv")
    salaries_path = os.path.join(LINKEDIN_BASE, "jobs", "salaries.csv")

    if not os.path.exists(postings_path):
        raise FileNotFoundError(
            f"LinkedIn dataset not found at {postings_path}. "
            "Run: python -c \"import kagglehub; kagglehub.dataset_download('arshkon/linkedin-job-postings')\""
        )

    # Load postings in chunks to handle large file, filtering for data roles
    logger.info("Filtering 3.3M postings for data-related roles (this takes ~30s)...")

    data_jobs = []
    chunk_size = 50000

    for chunk in pd.read_csv(postings_path, chunksize=chunk_size,
                              usecols=["job_id", "title", "company_name", "location",
                                       "description", "max_salary", "min_salary",
                                       "med_salary", "pay_period", "formatted_work_type",
                                       "listed_time"],
                              dtype={"job_id": str}):
        # Filter for data-related roles by title
        mask = chunk["title"].str.lower().str.contains(
            "|".join(DATA_ROLE_KEYWORDS), na=False
        )
        filtered = chunk[mask]
        data_jobs.append(filtered)

        total = sum(len(d) for d in data_jobs)
        if total >= limit * 2:  # Get extra for dedup buffer
            break

    df = pd.concat(data_jobs, ignore_index=True)
    logger.info(f"Found {len(df)} data-related job postings")

    # Merge salary data from separate table
    if os.path.exists(salaries_path):
        sal_df = pd.read_csv(salaries_path, dtype={"job_id": str})
        sal_df = sal_df[sal_df["compensation_type"] == "BASE_SALARY"]
        df = df.merge(
            sal_df[["job_id", "max_salary", "min_salary", "med_salary", "pay_period", "currency"]].rename(
                columns={"max_salary": "sal_max", "min_salary": "sal_min",
                         "med_salary": "sal_med", "pay_period": "sal_period",
                         "currency": "sal_currency"}
            ),
            on="job_id", how="left"
        )
        # Use salary table values when postings salary is missing
        df["min_salary"] = df["min_salary"].fillna(df["sal_min"])
        df["max_salary"] = df["max_salary"].fillna(df["sal_max"])
        df["pay_period"] = df["pay_period"].fillna(df["sal_period"])
        df.drop(columns=["sal_max", "sal_min", "sal_med", "sal_period", "sal_currency"],
                inplace=True, errors="ignore")

    # Annualize salaries
    def annualize(row):
        min_sal = row.get("min_salary")
        max_sal = row.get("max_salary")
        period = str(row.get("pay_period", "")).upper()

        if pd.isna(min_sal) and pd.isna(max_sal):
            return None, None

        multiplier = 1
        if "HOUR" in period:
            multiplier = 2080
        elif "MONTH" in period:
            multiplier = 12
        elif "WEEK" in period:
            multiplier = 52

        min_val = float(min_sal) * multiplier if pd.notna(min_sal) else None
        max_val = float(max_sal) * multiplier if pd.notna(max_sal) else None
        return min_val, max_val

    salary_data = df.apply(annualize, axis=1, result_type="expand")
    df["salary_min"] = salary_data[0]
    df["salary_max"] = salary_data[1]

    # Convert listing timestamp to date
    if "listed_time" in df.columns:
        df["date_posted"] = pd.to_datetime(df["listed_time"], unit="ms", errors="coerce").dt.strftime("%Y-%m-%d")

    # Truncate descriptions (some are very long)
    df["description"] = df["description"].astype(str).str[:2000]

    # Sample down to limit
    if len(df) > limit:
        df = df.sample(n=limit, random_state=42).reset_index(drop=True)

    # Map to our pipeline format
    output = pd.DataFrame({
        "job_title": df["title"],
        "company": df["company_name"],
        "location": df["location"],
        "salary_text": df.apply(
            lambda r: f"${r['salary_min']:,.0f} - ${r['salary_max']:,.0f}/year"
            if pd.notna(r.get("salary_min")) and pd.notna(r.get("salary_max")) else None,
            axis=1
        ),
        "salary_min": df["salary_min"],
        "salary_max": df["salary_max"],
        "seniority": None,
        "description": df["description"],
        "date_posted": df.get("date_posted"),
        "url": df["job_id"].apply(lambda x: f"https://linkedin.com/jobs/view/{x}"),
        "source": "linkedin",
    })

    logger.info(f"Prepared {len(output)} jobs for pipeline")
    return output


def load_salary_data() -> pd.DataFrame:
    """
    Load the 'Jobs in Data' salary dataset.

    This dataset has structured salary info but no descriptions.
    Useful as supplementary data for salary analysis.
    """
    logger.info("Loading Jobs in Data (salary) dataset...")

    csv_path = os.path.join(SALARY_BASE, "jobs_in_data.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Salary dataset not found at {csv_path}. "
            "Run: python -c \"import kagglehub; kagglehub.dataset_download('hummaamqaasim/jobs-in-data')\""
        )

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} salary records")

    # Convert EUR salaries to approximate values (keep USD as-is)
    # Map to our pipeline format
    output = pd.DataFrame({
        "job_title": df["job_title"],
        "company": None,  # Not available in this dataset
        "location": df["company_location"],
        "salary_text": df.apply(
            lambda r: f"${r['salary_in_usd']:,}/year (USD)", axis=1
        ),
        "salary_min": df["salary_in_usd"] * 0.9,  # Estimate range from single value
        "salary_max": df["salary_in_usd"] * 1.1,
        "seniority": df["experience_level"],
        "description": df.apply(
            lambda r: f"{r['job_title']} position. Category: {r['job_category']}. "
                      f"{r['employment_type']} role, {r['work_setting']} setting. "
                      f"Company size: {r['company_size']}.",
            axis=1
        ),
        "date_posted": df["work_year"].astype(str) + "-06-15",
        "url": None,
        "source": "kaggle_salary_survey",
    })

    return output


def main():
    parser = argparse.ArgumentParser(description="Load Kaggle dataset into pipeline format")
    parser.add_argument("--source", choices=["linkedin", "salary", "both"], default="linkedin",
                        help="Which dataset to use (default: linkedin)")
    parser.add_argument("--limit", type=int, default=2000,
                        help="Max number of LinkedIn postings to include (default: 2000)")
    args = parser.parse_args()

    os.makedirs(DATA_RAW, exist_ok=True)
    all_jobs = []

    if args.source in ("linkedin", "both"):
        linkedin_jobs = load_linkedin_data(limit=args.limit)
        all_jobs.append(linkedin_jobs)

    if args.source in ("salary", "both"):
        salary_jobs = load_salary_data()
        all_jobs.append(salary_jobs)

    combined = pd.concat(all_jobs, ignore_index=True)

    output_path = os.path.join(DATA_RAW, "jobs_raw.csv")
    combined.to_csv(output_path, index=False, encoding="utf-8")

    logger.info(f"✅ Saved {len(combined)} real job listings to {output_path}")
    logger.info(f"   Source breakdown:")
    logger.info(f"   {combined['source'].value_counts().to_string()}")

    has_salary = combined["salary_min"].notna().sum()
    has_desc = combined["description"].notna().sum()
    logger.info(f"   With salary: {has_salary}/{len(combined)} ({has_salary/len(combined)*100:.0f}%)")
    logger.info(f"   With description: {has_desc}/{len(combined)} ({has_desc/len(combined)*100:.0f}%)")


if __name__ == "__main__":
    main()
