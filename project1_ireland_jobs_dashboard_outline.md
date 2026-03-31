# 🇮🇪 Project 1: Ireland Jobs & Skills Market Dashboard

> **Role Target:** Junior Data Analyst
> **Estimated Duration:** 1–2 weeks
> **Difficulty:** Beginner–Intermediate

---

## 1. Project Overview

**Goal:** Build an end-to-end data analytics project that scrapes Irish job listings, cleans and structures the data, and delivers an interactive Power BI dashboard with actionable insights about the Irish data job market.

**Business Question:** *What skills, tools, and qualifications are Irish employers looking for in data roles — and how do I position myself to get hired?*

**Why It Stands Out:**
- Shows initiative and market research relevant to your relocation
- Proves Power BI proficiency (aligns with your PBI certification)
- Demonstrates the full DA workflow: collection → cleaning → modeling → visualization → insight
- Instant interview conversation starter

---

## 2. Data Sources

| Source | Method | Data Available |
|---|---|---|
| **LinkedIn Jobs** (primary) | Manual export / `linkedin-jobs-scraper` Python lib | Title, company, location, description, seniority, date |
| **Indeed.ie** | BeautifulSoup / Selenium scraping | Title, company, salary (sometimes), description |
| **IrishJobs.ie** | BeautifulSoup scraping | Title, company, location, description |
| **Glassdoor** | Glassdoor API or scraping | Salary estimates, company ratings |
| **Kaggle fallback** | Download CSV | Pre-scraped job posting datasets (e.g., "Data Scientist Jobs" dataset) |

> **Recommended approach:** Start with a Kaggle dataset to prototype fast, then layer in your own scraped Irish data for authenticity.

---

## 3. Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA COLLECTION                       │
│  Python scripts (BeautifulSoup / Selenium / API calls)  │
│  → Raw JSON/CSV files                                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA CLEANING & WRANGLING               │
│  Python (Pandas)                                        │
│  → Deduplicate, parse skills from descriptions,         │
│    standardize titles, extract salary ranges             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA STORAGE                           │
│  PostgreSQL or DuckDB                                   │
│  → Structured tables: jobs, skills, companies, salaries │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 ANALYSIS & VISUALIZATION                 │
│  Power BI (.pbix) + Python notebooks for EDA            │
│  → Interactive dashboard with filters and drill-downs   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   DELIVERABLES                           │
│  Power BI Dashboard (published or .pbix)                │
│  Analysis Report (PDF/Markdown)                         │
│  GitHub Repository with professional README             │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Folder Structure

```
ireland-jobs-dashboard/
├── README.md                   # Project overview, screenshots, setup
├── requirements.txt            # Python dependencies
├── .gitignore
│
├── data/
│   ├── raw/                    # Raw scraped data (CSV/JSON)
│   ├── processed/              # Cleaned, transformed data
│   └── reference/              # Lookup tables (skill categories, city mappings)
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   └── 04_skill_extraction.ipynb
│
├── src/
│   ├── scraper/
│   │   ├── indeed_scraper.py
│   │   ├── linkedin_scraper.py
│   │   └── utils.py
│   ├── cleaning/
│   │   ├── clean_jobs.py
│   │   └── extract_skills.py
│   └── database/
│       ├── schema.sql
│       └── load_data.py
│
├── dashboard/
│   ├── ireland_jobs_dashboard.pbix    # Power BI file
│   └── screenshots/                   # Dashboard screenshots for README
│
├── reports/
│   └── ireland_data_jobs_analysis.md  # Written analysis report
│
└── docs/
    └── data_dictionary.md             # Column descriptions, data sources
```

---

## 5. Phase-by-Phase Breakdown

### Phase 1: Data Collection (Days 1–2)

**Tasks:**
- [ ] Research and select 2–3 data sources
- [ ] Write Python scraper scripts (or download Kaggle dataset)
- [ ] Collect a minimum of **500–1,000 job listings** focused on:
  - "Data Analyst Ireland"
  - "Data Scientist Ireland"
  - "Data Engineer Ireland"
  - "Business Analyst Ireland"
  - "BI Analyst Ireland"
- [ ] Save raw data as CSV/JSON with timestamps
- [ ] Document data source and collection method

**Key Fields to Collect:**

| Field | Type | Example |
|---|---|---|
| `job_title` | string | "Junior Data Analyst" |
| `company` | string | "Accenture" |
| `location` | string | "Dublin, Ireland" |
| `salary_min` | float | 35000 |
| `salary_max` | float | 45000 |
| `description` | text | Full job description |
| `date_posted` | date | 2026-03-15 |
| `seniority` | string | "Entry Level" |
| `source` | string | "indeed.ie" |
| `url` | string | Link to original posting |

---

### Phase 2: Data Cleaning & Skill Extraction (Days 3–4)

**Tasks:**
- [ ] Deduplicate listings (same job posted on multiple boards)
- [ ] Standardize job titles into categories:
  - Data Analyst, Data Scientist, Data Engineer, BI Analyst, Analytics Engineer, etc.
- [ ] Parse and standardize locations:
  - Dublin, Cork, Galway, Limerick, Remote, Hybrid
- [ ] Extract salary ranges (handle "€35k–€45k", "Competitive", missing values)
- [ ] **Skill Extraction** — parse job descriptions to identify mentioned tools/skills:

**Skill Keyword Dictionary:**

```python
SKILL_CATEGORIES = {
    "Programming": ["python", "r", "sql", "java", "scala", "bash"],
    "Visualization": ["power bi", "tableau", "looker", "matplotlib", "plotly"],
    "Data Engineering": ["airflow", "dbt", "spark", "kafka", "etl", "elt"],
    "Cloud": ["aws", "azure", "gcp", "bigquery", "redshift", "snowflake"],
    "ML/AI": ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit"],
    "Databases": ["postgresql", "mysql", "mongodb", "redis", "duckdb"],
    "Tools": ["excel", "git", "docker", "kubernetes", "jira", "confluence"],
    "Soft Skills": ["communication", "stakeholder", "agile", "problem-solving"]
}
```

- [ ] Create a `job_skills` junction table (many-to-many)
- [ ] Validate data quality — check for nulls, outliers, data types

---

### Phase 3: Database Loading (Day 4)

**Tasks:**
- [ ] Design the database schema (star schema recommended):

```sql
-- Fact Table
CREATE TABLE fact_jobs (
    job_id          SERIAL PRIMARY KEY,
    job_title_raw   TEXT,
    job_category    VARCHAR(50),    -- standardized category
    company         VARCHAR(200),
    location        VARCHAR(100),
    city            VARCHAR(50),
    salary_min      DECIMAL,
    salary_max      DECIMAL,
    salary_avg      DECIMAL,
    seniority       VARCHAR(30),
    date_posted     DATE,
    source          VARCHAR(50),
    description     TEXT,
    url             TEXT
);

-- Dimension Table
CREATE TABLE dim_skills (
    skill_id        SERIAL PRIMARY KEY,
    skill_name      VARCHAR(100),
    skill_category  VARCHAR(50)
);

-- Junction Table
CREATE TABLE job_skills (
    job_id          INT REFERENCES fact_jobs(job_id),
    skill_id        INT REFERENCES dim_skills(skill_id),
    PRIMARY KEY (job_id, skill_id)
);
```

- [ ] Write and run the data loading script
- [ ] Verify row counts and data integrity with SQL queries

---

### Phase 4: Exploratory Data Analysis (Days 5–6)

**Tasks:**
- [ ] Create a Jupyter notebook with visualizations covering:

**Key Analysis Questions:**

1. **Market Overview**
   - How many data roles are currently open in Ireland?
   - What's the split between Analyst / Scientist / Engineer roles?
   - Which cities have the most openings?

2. **Skills Demand**
   - What are the top 15 most requested skills overall?
   - How does skill demand differ by role type?
   - Which skill *combinations* appear most frequently?

3. **Salary Analysis**
   - What are the salary ranges by role type?
   - How do salaries differ by city (Dublin vs. rest)?
   - Is there a salary premium for specific skills?

4. **Company Landscape**
   - Which companies are hiring the most?
   - Top industries for data roles (tech, finance, pharma, consulting)

5. **Your Personal Fit**
   - Which of your skills are most in demand?
   - Which skills gaps should you close?
   - What's your estimated market value?

- [ ] Use `seaborn`, `plotly`, and `matplotlib` for visualizations
- [ ] Export key charts as images for the README

---

### Phase 5: Power BI Dashboard (Days 7–9)

**Tasks:**
- [ ] Connect Power BI to your database (PostgreSQL/DuckDB) or load the CSV
- [ ] Build a **data model** in Power BI (relationships between tables)
- [ ] Create **DAX measures**:

```
Total Jobs = COUNTROWS(fact_jobs)
Avg Salary = AVERAGE(fact_jobs[salary_avg])
Top Skill = TOPN(1, dim_skills, [Skill Count], DESC)
Skill Count = COUNTROWS(job_skills)
```

**Dashboard Pages:**

#### Page 1: Market Overview
- KPI cards: Total jobs, Avg salary, Top city, Top role
- Bar chart: Jobs by role category
- Map visual: Jobs by city/county
- Line chart: Posting trend over time
- Slicer filters: City, Role, Seniority, Date range

#### Page 2: Skills Demand
- Horizontal bar chart: Top 15 skills overall
- Stacked bar: Skills by role type (Analyst vs. Scientist vs. Engineer)
- Treemap: Skill categories breakdown
- Word cloud: Most common keywords in descriptions
- Matrix: Skill co-occurrence heatmap

#### Page 3: Salary Insights
- Box plots: Salary distribution by role
- Bar chart: Salary by city
- Scatter plot: Salary vs. number of required skills
- Table: Highest-paying companies with filters

#### Page 4: Your Fit Score ⭐
- Gauge visual: % of jobs you qualify for based on your skills
- Gap analysis: Skills you have vs. skills most in demand
- Recommended skills to learn (based on highest demand you're missing)
- Filtered list: "Jobs You Could Apply To Today"

- [ ] Apply consistent formatting and color theme
- [ ] Add navigation buttons between pages
- [ ] Test all slicers and cross-filtering
- [ ] Take screenshots for README and portfolio

---

### Phase 6: Analysis Report (Day 9–10)

**Tasks:**
- [ ] Write a 2–3 page summary report including:
  - Executive summary (key findings in 3 bullet points)
  - Methodology (data sources, collection period, sample size)
  - Key findings with supporting visualizations
  - Recommendations (for your own job search + general market insights)
  - Limitations and future work
- [ ] Save as Markdown and PDF

---

### Phase 7: GitHub Repo & README (Day 10)

**Tasks:**
- [ ] Initialize Git repository
- [ ] Write a professional README.md:

```markdown
# 🇮🇪 Ireland Data Jobs Market Dashboard

## Overview
An end-to-end data analytics project analyzing 1,000+ job listings
to uncover trends in Ireland's data job market.

## Key Findings
- Python and SQL are required in 85% of data roles
- Power BI demand grew 40% year-over-year
- Dublin accounts for 68% of all data roles
- Median salary for Junior Data Analyst: €38,000

## Dashboard Preview
[Screenshots here]

## Tech Stack
Python · Pandas · SQL · PostgreSQL · Power BI · BeautifulSoup

## How to Run
[Setup instructions]

## Project Structure
[Folder tree]

## Data Sources
[List with links]

## Author
Ehtisham Aziz — [LinkedIn] — [GitHub]
```

- [ ] Add a `.gitignore` (exclude `.pbix` binary if too large, or use Git LFS)
- [ ] Push to GitHub
- [ ] Pin the repo on your GitHub profile

---

## 6. Key Python Libraries

```
pandas>=2.0
numpy
beautifulsoup4
selenium
requests
sqlalchemy
psycopg2-binary  # or duckdb
plotly
seaborn
matplotlib
jupyter
python-dotenv
```

---

## 7. SQL Queries to Prepare for Interviews

These are queries you should be ready to explain — they double as interview prep:

```sql
-- Top 10 most in-demand skills
SELECT s.skill_name, COUNT(*) AS job_count
FROM job_skills js
JOIN dim_skills s ON js.skill_id = s.skill_id
GROUP BY s.skill_name
ORDER BY job_count DESC
LIMIT 10;

-- Average salary by role category
SELECT job_category,
       ROUND(AVG(salary_avg), 0) AS avg_salary,
       COUNT(*) AS job_count
FROM fact_jobs
WHERE salary_avg IS NOT NULL
GROUP BY job_category
ORDER BY avg_salary DESC;

-- Skills gap analysis: most demanded skills I don't have
WITH my_skills AS (
    SELECT skill_name FROM dim_skills
    WHERE skill_name IN ('python', 'sql', 'pandas', 'power bi',
                         'docker', 'fastapi', 'dbt', 'bigquery')
)
SELECT s.skill_name, COUNT(*) AS demand
FROM job_skills js
JOIN dim_skills s ON js.skill_id = s.skill_id
WHERE s.skill_name NOT IN (SELECT skill_name FROM my_skills)
GROUP BY s.skill_name
ORDER BY demand DESC
LIMIT 10;

-- Companies hiring the most for entry-level roles
SELECT company, COUNT(*) AS openings
FROM fact_jobs
WHERE seniority IN ('Entry Level', 'Junior', 'Associate')
GROUP BY company
ORDER BY openings DESC
LIMIT 15;
```

---

## 8. Tips for Maximum Impact

1. **Publish the dashboard** to Power BI Service (free tier) so interviewers can interact with it via a link — no download needed
2. **Add the project URL** to your CV under the Projects section
3. **Write a LinkedIn post** about your findings — tag it #DataAnalytics #IrelandJobs #PowerBI
4. **Mention specific numbers** in interviews: *"I analyzed 1,200 job postings and found that SQL + Power BI appears in 73% of Data Analyst listings in Dublin"*
5. **Keep the data fresh** — rerun the scraper monthly to show the dashboard is a living project

---

## 9. Stretch Goals (If Time Permits)

- [ ] Add a **Streamlit web app** version of the dashboard
- [ ] Implement **automated daily scraping** with GitHub Actions
- [ ] Build a **job recommendation engine** that matches your CV to listings
- [ ] Add **NLP topic modeling** on job descriptions to find hidden role clusters
- [ ] Create a **salary prediction model** based on required skills and location
