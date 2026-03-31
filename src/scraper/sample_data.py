"""
Generate realistic sample job listing data for pipeline development.

This creates realistic-looking Irish data job listings so you can develop
the full pipeline without depending on live scraping. The data mirrors
the structure and variety of real Indeed.ie listings.
"""

import random
from datetime import datetime, timedelta


# ============================================================
# Realistic data pools for Ireland's data job market
# ============================================================

COMPANIES = [
    # Big Tech
    "Google", "Meta", "Apple", "Microsoft", "Amazon", "Salesforce", "LinkedIn",
    "Stripe", "Intercom", "HubSpot", "Workday", "ServiceNow", "Oracle",
    # Consulting
    "Accenture", "Deloitte", "PwC", "EY", "KPMG", "McKinsey", "BCG",
    # Finance / Fintech
    "JP Morgan", "Citi", "Bank of Ireland", "AIB", "Fidelity Investments",
    "Mastercard", "Visa", "Revolut", "Coinbase", "Susquehanna (SIG)",
    # Pharma / Health
    "Pfizer", "Johnson & Johnson", "Medtronic", "Abbott", "Boston Scientific",
    "ICON plc", "Jazz Pharmaceuticals",
    # Irish / EU Companies
    "Kerry Group", "Ryanair", "CRH", "Paddy Power Betfair", "Flutter",
    "Eircom / eir", "An Post", "ESB", "Aer Lingus", "Primark (Penneys)",
    # Agencies & Startups
    "Version 1", "Ergo", "Teamwork", "Workhuman", "Flipdish", "Wayflyer",
    "Swrve", "Glofox", "LearnUpon", "Frankli",
]

TITLES_BY_CATEGORY = {
    "Data Analyst": [
        "Data Analyst", "Junior Data Analyst", "Graduate Data Analyst",
        "Data Analyst - Marketing", "Data Analyst - Finance",
        "Data Analyst (Entry Level)", "Reporting Analyst",
        "Data Analytics Analyst", "Customer Data Analyst",
    ],
    "Data Scientist": [
        "Data Scientist", "Junior Data Scientist", "Graduate Data Scientist",
        "Data Scientist - NLP", "Machine Learning Scientist",
        "Applied Data Scientist", "Data Scientist (Entry Level)",
    ],
    "Data Engineer": [
        "Data Engineer", "Junior Data Engineer", "Graduate Data Engineer",
        "ETL Developer", "Data Pipeline Engineer", "Big Data Engineer",
        "Cloud Data Engineer", "Analytics Engineer",
    ],
    "BI Analyst": [
        "BI Analyst", "Business Intelligence Analyst", "BI Developer",
        "Power BI Analyst", "Tableau Developer", "BI Reporting Analyst",
    ],
    "Business Analyst": [
        "Business Analyst", "Business Data Analyst", "Product Analyst",
        "Strategy Analyst", "Operations Analyst",
    ],
}

LOCATIONS = [
    "Dublin, Ireland", "Dublin 2, Ireland", "Dublin 4, Ireland",
    "Dublin, Co. Dublin", "Dublin (Hybrid)", "Dublin - Remote",
    "Cork, Ireland", "Cork (Hybrid)", "Galway, Ireland",
    "Limerick, Ireland", "Waterford, Ireland",
    "Remote - Ireland", "Hybrid - Dublin", "Hybrid - Cork",
    "Ireland", "Dublin / Remote",
]

SENIORITY_LEVELS = [
    "Entry Level", "Junior", "Associate", "Mid-Level", "Graduate",
    None,  # Sometimes not specified
]

# Skill phrases that appear naturally in job descriptions
DESCRIPTION_TEMPLATES = [
    # Data Analyst descriptions
    "We are looking for a {title} to join our {dept} team. You will work with large datasets using {tool1} and {tool2} to deliver insights that drive business decisions. Requirements: {skill1}, {skill2}, {skill3}. Experience with {tool3} is a plus. Strong {soft1} skills required.",
    "As a {title}, you'll analyse data from multiple sources to support our {dept} function. You'll create dashboards and reports using {tool1}, run SQL queries against our {tool3} database, and present findings to stakeholders. Must have: {skill1}, {skill2}, proficiency in {tool2}. Nice to have: {skill3}, experience with {tool4}.",
    "Join our growing analytics team as a {title}. Day-to-day you'll work with {tool1} and {tool2} to provide actionable insights. You'll collaborate with cross-functional teams to identify trends and opportunities. Required: {skill1}, {skill2}, {skill3}. {soft1} and {soft2} skills are essential.",
    "{title} needed for our {dept} team in our Dublin office. Responsibilities include building reports in {tool1}, writing complex {tool2} queries, and conducting {skill1}. We value {soft1} and {soft2}. Bachelor's degree in a quantitative field preferred. Experience with {tool3} or {tool4} a bonus.",
    "We're hiring a {title} to help us turn data into decisions. You'll use {tool1}, {tool2}, and {tool3} daily. Strong {skill1} and {skill2} skills required. This role requires excellent {soft1} skills as you'll regularly present to senior leadership. {skill3} knowledge is advantageous.",
]

TOOLS_POOL = [
    "Python", "SQL", "Power BI", "Tableau", "Excel", "R", "Pandas",
    "NumPy", "Scikit-learn", "TensorFlow", "PySpark", "Spark",
    "Airflow", "dbt", "Docker", "Kubernetes", "Git",
    "AWS", "Azure", "GCP", "BigQuery", "Snowflake", "Redshift",
    "PostgreSQL", "MySQL", "MongoDB", "DuckDB",
    "Looker", "Grafana", "Metabase", "Jupyter",
    "FastAPI", "Streamlit", "MLflow", "Databricks",
    "Kafka", "Terraform", "GitHub Actions", "JIRA",
    "Google Analytics", "Mixpanel", "Segment",
]

SKILLS_POOL = [
    "data analysis", "statistical analysis", "machine learning",
    "data visualization", "data cleaning", "data modeling",
    "ETL", "data pipeline development", "feature engineering",
    "A/B testing", "hypothesis testing", "predictive modeling",
    "NLP", "deep learning", "regression analysis",
    "exploratory data analysis", "data warehousing",
    "business intelligence", "reporting", "dashboard development",
    "data quality", "data governance", "agile methodology",
]

SOFT_SKILLS = [
    "communication", "stakeholder management", "problem-solving",
    "teamwork", "presentation", "critical thinking",
    "collaboration", "analytical thinking", "attention to detail",
]

DEPARTMENTS = [
    "Analytics", "Data", "Engineering", "Product", "Marketing",
    "Finance", "Operations", "Risk", "Commercial", "Technology",
]

SALARY_RANGES = {
    "Data Analyst":     [(28000, 35000), (32000, 40000), (35000, 45000), (38000, 48000), (40000, 50000)],
    "Data Scientist":   [(35000, 45000), (40000, 52000), (45000, 58000), (48000, 62000), (50000, 65000)],
    "Data Engineer":    [(35000, 45000), (40000, 55000), (45000, 60000), (50000, 65000), (52000, 70000)],
    "BI Analyst":       [(30000, 38000), (33000, 42000), (36000, 46000), (38000, 48000), (40000, 52000)],
    "Business Analyst": [(30000, 38000), (32000, 42000), (35000, 45000), (38000, 50000), (40000, 52000)],
}


def _generate_description(title: str) -> str:
    """Generate a realistic job description using templates and random skills."""
    template = random.choice(DESCRIPTION_TEMPLATES)
    tools = random.sample(TOOLS_POOL, min(6, len(TOOLS_POOL)))
    skills = random.sample(SKILLS_POOL, min(4, len(SKILLS_POOL)))
    softs = random.sample(SOFT_SKILLS, min(3, len(SOFT_SKILLS)))

    return template.format(
        title=title,
        dept=random.choice(DEPARTMENTS),
        tool1=tools[0], tool2=tools[1], tool3=tools[2], tool4=tools[3],
        skill1=skills[0], skill2=skills[1], skill3=skills[2],
        soft1=softs[0], soft2=softs[1],
    )


def generate_sample_jobs(n: int = 800) -> list[dict]:
    """
    Generate n realistic sample job listings.

    Distribution mimics real market:
    - ~40% Data Analyst
    - ~20% Data Scientist
    - ~15% Data Engineer
    - ~15% BI Analyst
    - ~10% Business Analyst
    """
    category_weights = {
        "Data Analyst": 0.40,
        "Data Scientist": 0.20,
        "Data Engineer": 0.15,
        "BI Analyst": 0.15,
        "Business Analyst": 0.10,
    }

    jobs = []
    base_date = datetime(2026, 3, 1)

    for i in range(n):
        # Pick category based on weighted distribution
        category = random.choices(
            list(category_weights.keys()),
            weights=list(category_weights.values()),
            k=1
        )[0]

        title = random.choice(TITLES_BY_CATEGORY[category])
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)

        # 60% of listings show salary
        if random.random() < 0.60:
            salary_range = random.choice(SALARY_RANGES[category])
            salary_min = salary_range[0]
            salary_max = salary_range[1]
            salary_text = f"€{salary_min:,} - €{salary_max:,} a year"
        else:
            salary_min = None
            salary_max = None
            salary_text = None

        seniority = random.choice(SENIORITY_LEVELS)
        date_posted = base_date + timedelta(days=random.randint(0, 30))
        description = _generate_description(title)

        jobs.append({
            "job_title": title,
            "company": company,
            "location": location,
            "salary_text": salary_text,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "seniority": seniority,
            "description": description,
            "date_posted": date_posted.strftime("%Y-%m-%d"),
            "url": f"https://ie.indeed.com/viewjob?jk={random.randint(100000, 999999):x}",
            "source": "indeed.ie",
        })

    random.shuffle(jobs)
    return jobs
