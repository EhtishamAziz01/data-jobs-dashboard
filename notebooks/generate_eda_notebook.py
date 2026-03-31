#!/usr/bin/env python3
"""
Generate the EDA Jupyter Notebook for the Ireland Jobs Dashboard.

Creates a comprehensive .ipynb with all analysis sections:
1. Setup & Data Loading
2. Market Overview
3. Skills Demand Analysis
4. Salary Analysis
5. Company Landscape
6. Your Personal Fit Analysis

Usage:
    python notebooks/generate_eda_notebook.py
    jupyter notebook notebooks/03_eda_analysis.ipynb
"""

import json
import os


def md(source: str) -> dict:
    """Create a markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.strip().split("\n")]
    }


def code(source: str) -> dict:
    """Create a code cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.strip().split("\n")]
    }


def build_notebook() -> dict:
    cells = []

    # ============================================================
    # HEADER
    # ============================================================
    cells.append(md("""# 🇮🇪 Ireland Data Jobs Market — Exploratory Data Analysis

**Project:** Ireland Jobs & Skills Market Dashboard
**Author:** Ehtisham Aziz
**Data Source:** LinkedIn Job Postings (Kaggle) — 2,000 real job listings
**Date:** March 2026

---

## Table of Contents
1. [Setup & Data Loading](#1-setup)
2. [Market Overview](#2-market-overview)
3. [Skills Demand Analysis](#3-skills-demand)
4. [Salary Analysis](#4-salary-analysis)
5. [Company Landscape](#5-company-landscape)
6. [Your Personal Fit](#6-your-fit)
7. [Key Takeaways](#7-takeaways)"""))

    # ============================================================
    # 1. SETUP
    # ============================================================
    cells.append(md("""## 1. Setup & Data Loading <a id="1-setup"></a>"""))

    cells.append(code("""# Core libraries
import pandas as pd
import numpy as np
import duckdb
import json

# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_colwidth', 80)
pio.templates.default = "plotly_white"

# Color palette — professional dark theme
COLORS = {
    'primary': '#4361EE',
    'secondary': '#3A0CA3',
    'accent': '#F72585',
    'success': '#4CC9F0',
    'warning': '#F9C74F',
    'dark': '#1A1A2E',
}
PALETTE = ['#4361EE', '#3A0CA3', '#F72585', '#4CC9F0', '#F9C74F', '#90BE6D', '#F94144', '#577590']

print("✅ Libraries loaded")"""))

    cells.append(code("""# Connect to DuckDB
conn = duckdb.connect('../data/ireland_jobs.duckdb', read_only=True)

# Load tables
jobs = conn.execute("SELECT * FROM fact_jobs").fetchdf()
skills = conn.execute("SELECT * FROM dim_skills").fetchdf()
job_skills = conn.execute("SELECT * FROM job_skills").fetchdf()

print(f"📊 Loaded: {len(jobs)} jobs | {len(skills)} skills | {len(job_skills)} job-skill pairs")
print(f"📅 Date range: {jobs['date_posted'].min()} to {jobs['date_posted'].max()}")
print(f"💰 Jobs with salary: {jobs['salary_avg'].notna().sum()} ({jobs['salary_avg'].notna().mean()*100:.0f}%)")
jobs.head(3)"""))

    # ============================================================
    # 2. MARKET OVERVIEW
    # ============================================================
    cells.append(md("""---
## 2. Market Overview <a id="2-market-overview"></a>

Let's start with the big picture: how many data roles are out there, what types, and where?"""))

    cells.append(code("""# KPI Summary
total_jobs = len(jobs)
total_companies = jobs['company'].nunique()
avg_salary = jobs['salary_avg'].mean()
median_salary = jobs['salary_avg'].median()
pct_with_salary = jobs['salary_avg'].notna().mean() * 100
top_category = jobs['job_category'].value_counts().index[0]

print("=" * 60)
print("📊 MARKET OVERVIEW")
print("=" * 60)
print(f"  Total job postings:    {total_jobs:,}")
print(f"  Unique companies:      {total_companies:,}")
print(f"  Top category:          {top_category}")
print(f"  Avg salary (annual):   ${avg_salary:,.0f}")
print(f"  Median salary:         ${median_salary:,.0f}")
print(f"  % with salary data:    {pct_with_salary:.0f}%")
print("=" * 60)"""))

    cells.append(code("""# Jobs by Category — Horizontal Bar
category_counts = jobs['job_category'].value_counts().reset_index()
category_counts.columns = ['Category', 'Count']
category_counts['Percentage'] = (category_counts['Count'] / total_jobs * 100).round(1)

fig = px.bar(
    category_counts,
    x='Count', y='Category',
    orientation='h',
    text=category_counts.apply(lambda r: f"{r['Count']} ({r['Percentage']}%)", axis=1),
    color='Count',
    color_continuous_scale='Blues',
    title='📊 Job Postings by Category',
)
fig.update_layout(
    height=400,
    showlegend=False,
    coloraxis_showscale=False,
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title='Number of Postings',
    yaxis_title='',
)
fig.update_traces(textposition='outside')
fig.show()"""))

    cells.append(code("""# Seniority Distribution — Donut Chart
seniority_counts = jobs['seniority'].value_counts().reset_index()
seniority_counts.columns = ['Seniority', 'Count']

fig = px.pie(
    seniority_counts,
    values='Count', names='Seniority',
    hole=0.5,
    color_discrete_sequence=PALETTE,
    title='🎯 Seniority Level Distribution',
)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(height=400)
fig.show()"""))

    cells.append(code("""# Work Model Distribution
work_counts = jobs['work_model'].value_counts().reset_index()
work_counts.columns = ['Work Model', 'Count']

fig = px.bar(
    work_counts,
    x='Work Model', y='Count',
    color='Work Model',
    color_discrete_sequence=PALETTE,
    title='🏢 Work Model Distribution (On-site / Remote / Hybrid)',
    text='Count',
)
fig.update_layout(height=350, showlegend=False, xaxis_title='', yaxis_title='Number of Postings')
fig.update_traces(textposition='outside')
fig.show()"""))

    # ============================================================
    # 3. SKILLS DEMAND
    # ============================================================
    cells.append(md("""---
## 3. Skills Demand Analysis <a id="3-skills-demand"></a>

The most critical section — what tools and skills do employers actually want?"""))

    cells.append(code("""# Top 20 Most In-Demand Skills
skill_demand = (
    job_skills
    .merge(skills, on='skill_id')
    .groupby(['skill_name', 'skill_category'])
    .size()
    .reset_index(name='job_count')
    .sort_values('job_count', ascending=False)
)
skill_demand['pct'] = (skill_demand['job_count'] / total_jobs * 100).round(1)

top_20 = skill_demand.head(20)

fig = px.bar(
    top_20,
    x='job_count', y='skill_name',
    orientation='h',
    color='skill_category',
    color_discrete_sequence=PALETTE,
    text=top_20.apply(lambda r: f"{r['job_count']} ({r['pct']}%)", axis=1),
    title='🏆 Top 20 Most In-Demand Skills',
)
fig.update_layout(
    height=600,
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title='Number of Job Postings',
    yaxis_title='',
    legend_title='Category',
)
fig.update_traces(textposition='outside')
fig.show()"""))

    cells.append(code("""# Skills by Category — Treemap
category_skill_counts = (
    job_skills
    .merge(skills, on='skill_id')
    .groupby('skill_category')
    .agg(total_mentions=('skill_id', 'count'), unique_skills=('skill_name', 'nunique'))
    .reset_index()
    .sort_values('total_mentions', ascending=False)
)

fig = px.treemap(
    job_skills.merge(skills, on='skill_id')
    .groupby(['skill_category', 'skill_name']).size().reset_index(name='count')
    .sort_values('count', ascending=False),
    path=['skill_category', 'skill_name'],
    values='count',
    color='count',
    color_continuous_scale='Blues',
    title='🗂️ Skills Treemap by Category',
)
fig.update_layout(height=600)
fig.show()"""))

    cells.append(code("""# Skills Demand by Job Category — Heatmap
# Get top 15 skills and main job categories (excluding 'Other')
top_skills_list = skill_demand.head(15)['skill_name'].tolist()
main_categories = [c for c in jobs['job_category'].value_counts().head(5).index if c != 'Other']

# Build skill-per-category matrix
skill_by_cat = (
    job_skills
    .merge(skills, on='skill_id')
    .merge(jobs[['job_id', 'job_category']], on='job_id')
    .query("job_category in @main_categories and skill_name in @top_skills_list")
    .groupby(['job_category', 'skill_name'])
    .size()
    .reset_index(name='count')
)

# Pivot for heatmap
pivot = skill_by_cat.pivot(index='skill_name', columns='job_category', values='count').fillna(0)

# Normalize to percentages within each category
for col in pivot.columns:
    cat_total = len(jobs[jobs['job_category'] == col])
    pivot[col] = (pivot[col] / cat_total * 100).round(1)

# Sort by total demand
pivot['total'] = pivot.sum(axis=1)
pivot = pivot.sort_values('total', ascending=True).drop('total', axis=1)

fig = px.imshow(
    pivot,
    text_auto=True,
    color_continuous_scale='Blues',
    title='🔥 Skills Demand by Job Category (% of postings)',
    labels={'color': '% of jobs'},
    aspect='auto',
)
fig.update_layout(height=500, xaxis_title='Job Category', yaxis_title='Skill')
fig.show()"""))

    cells.append(code("""# Skill Co-occurrence — What skills appear together?
from itertools import combinations

# Get top 10 skills for co-occurrence analysis
top_10_skills = skill_demand.head(10)['skill_name'].tolist()

# Build co-occurrence matrix
job_skill_names = (
    job_skills
    .merge(skills, on='skill_id')
    .query("skill_name in @top_10_skills")
    .groupby('job_id')['skill_name']
    .apply(set)
)

cooccurrence = pd.DataFrame(0, index=top_10_skills, columns=top_10_skills)
for skill_set in job_skill_names:
    for s1, s2 in combinations(skill_set, 2):
        if s1 in top_10_skills and s2 in top_10_skills:
            cooccurrence.loc[s1, s2] += 1
            cooccurrence.loc[s2, s1] += 1

fig = px.imshow(
    cooccurrence,
    text_auto=True,
    color_continuous_scale='Purples',
    title='🔗 Skill Co-occurrence Matrix (Top 10 Skills)',
    labels={'color': 'Co-occurrences'},
)
fig.update_layout(height=500, width=600)
fig.show()"""))

    # ============================================================
    # 4. SALARY ANALYSIS
    # ============================================================
    cells.append(md("""---
## 4. Salary Analysis <a id="4-salary-analysis"></a>

Understanding compensation across roles, seniority, and skills."""))

    cells.append(code("""# Filter to jobs with salary data
salary_jobs = jobs[jobs['salary_avg'].notna()].copy()
print(f"📊 Analyzing {len(salary_jobs)} jobs with salary data ({len(salary_jobs)/total_jobs*100:.0f}% of total)")

# Salary by Category — Box Plot
fig = px.box(
    salary_jobs[salary_jobs['job_category'] != 'Other'],
    x='job_category', y='salary_avg',
    color='job_category',
    color_discrete_sequence=PALETTE,
    title='💰 Salary Distribution by Job Category',
    labels={'salary_avg': 'Annual Salary (USD)', 'job_category': 'Category'},
)
fig.update_layout(height=450, showlegend=False, xaxis_title='')
fig.show()"""))

    cells.append(code("""# Salary by Seniority — Violin Plot
fig = px.violin(
    salary_jobs[salary_jobs['seniority'] != 'Not Specified'],
    x='seniority', y='salary_avg',
    color='seniority',
    box=True, points='outliers',
    color_discrete_sequence=PALETTE,
    title='📈 Salary Distribution by Seniority Level',
    labels={'salary_avg': 'Annual Salary (USD)', 'seniority': 'Seniority'},
    category_orders={'seniority': ['Junior', 'Mid-Level', 'Senior']},
)
fig.update_layout(height=450, showlegend=False, xaxis_title='')
fig.show()"""))

    cells.append(code("""# Salary Summary Table
salary_summary = (
    salary_jobs
    .groupby('job_category')
    .agg(
        count=('salary_avg', 'count'),
        mean=('salary_avg', 'mean'),
        median=('salary_avg', 'median'),
        min=('salary_avg', 'min'),
        max=('salary_avg', 'max'),
        std=('salary_avg', 'std'),
    )
    .round(0)
    .sort_values('median', ascending=False)
)
salary_summary.columns = ['# Jobs', 'Mean ($)', 'Median ($)', 'Min ($)', 'Max ($)', 'Std Dev ($)']
print("💰 Salary Summary by Category (USD)")
salary_summary.style.format("{:,.0f}")"""))

    cells.append(code("""# Salary Premium by Skill — Which skills pay the most?
skill_salary = (
    job_skills
    .merge(skills, on='skill_id')
    .merge(salary_jobs[['job_id', 'salary_avg']], on='job_id')
    .groupby('skill_name')
    .agg(avg_salary=('salary_avg', 'mean'), job_count=('salary_avg', 'count'))
    .query("job_count >= 10")  # Minimum sample size
    .sort_values('avg_salary', ascending=False)
    .head(20)
    .reset_index()
)

fig = px.bar(
    skill_salary,
    x='avg_salary', y='skill_name',
    orientation='h',
    color='avg_salary',
    color_continuous_scale='Greens',
    text=skill_salary['avg_salary'].apply(lambda x: f"${x:,.0f}"),
    title='💎 Highest Paying Skills (min 10 jobs with salary data)',
    labels={'avg_salary': 'Average Salary (USD)', 'skill_name': ''},
)
fig.update_layout(
    height=550,
    yaxis={'categoryorder': 'total ascending'},
    coloraxis_showscale=False,
)
fig.update_traces(textposition='outside')
fig.show()"""))

    # ============================================================
    # 5. COMPANY LANDSCAPE
    # ============================================================
    cells.append(md("""---
## 5. Company Landscape <a id="5-company-landscape"></a>

Which companies are hiring the most for data roles?"""))

    cells.append(code("""# Top 20 Companies by Number of Postings
top_companies = (
    jobs
    .groupby('company')
    .agg(job_count=('job_id', 'count'), avg_salary=('salary_avg', 'mean'))
    .sort_values('job_count', ascending=False)
    .head(20)
    .reset_index()
)

fig = px.bar(
    top_companies,
    x='job_count', y='company',
    orientation='h',
    color='avg_salary',
    color_continuous_scale='Viridis',
    text='job_count',
    title='🏢 Top 20 Hiring Companies (color = avg salary)',
    labels={'job_count': 'Number of Postings', 'company': '', 'avg_salary': 'Avg Salary ($)'},
)
fig.update_layout(
    height=550,
    yaxis={'categoryorder': 'total ascending'},
)
fig.update_traces(textposition='outside')
fig.show()"""))

    cells.append(code("""# Company Size Distribution (by number of postings)
company_posting_dist = (
    jobs.groupby('company').size().reset_index(name='postings')
)
company_posting_dist['tier'] = pd.cut(
    company_posting_dist['postings'],
    bins=[0, 1, 3, 10, 50, 1000],
    labels=['1 posting', '2-3 postings', '4-10 postings', '11-50 postings', '50+ postings']
)

tier_counts = company_posting_dist['tier'].value_counts().sort_index().reset_index()
tier_counts.columns = ['Tier', 'Companies']

fig = px.bar(
    tier_counts,
    x='Tier', y='Companies',
    color='Tier',
    color_discrete_sequence=PALETTE,
    text='Companies',
    title='📊 Company Distribution by Number of Data Job Postings',
)
fig.update_layout(height=350, showlegend=False, xaxis_title='', yaxis_title='Number of Companies')
fig.update_traces(textposition='outside')
fig.show()"""))

    # ============================================================
    # 6. YOUR FIT
    # ============================================================
    cells.append(md("""---
## 6. Your Personal Fit Analysis <a id="6-your-fit"></a>

How well do **your skills** match the market demand? What should you learn next?"""))

    cells.append(code("""# === YOUR SKILLS — UPDATE THIS LIST ===
MY_SKILLS = [
    'python', 'sql', 'pandas', 'numpy', 'docker', 'fastapi', 'git', 'github',
    'machine learning', 'scikit-learn', 'nlp', 'feature engineering',
    'data cleaning', 'data pipeline', 'etl', 'bigquery', 'gcp', 'google cloud',
    'streamlit', 'mlflow', 'dbt', 'excel', 'data quality',
    'exploratory data analysis', 'data visualization', 'github actions',
    'communication', 'collaboration', 'teamwork', 'power bi',
]

# Categorize all skills into "Have" vs "Don't Have"
all_skill_demand = skill_demand.copy()
all_skill_demand['you_have'] = all_skill_demand['skill_name'].isin(MY_SKILLS)

# Your fit score
demanded_skills = set(all_skill_demand['skill_name'])
your_demanded = set(MY_SKILLS) & demanded_skills
fit_score = len(your_demanded) / len(demanded_skills) * 100

print("=" * 60)
print(f"🎯 YOUR FIT SCORE: {fit_score:.0f}%")
print(f"   You have {len(your_demanded)} of {len(demanded_skills)} in-demand skills")
print("=" * 60)"""))

    cells.append(code("""# Skills You Have vs Market Demand
your_skills_demand = all_skill_demand[all_skill_demand['you_have']].sort_values('job_count', ascending=False).head(15)

fig = px.bar(
    your_skills_demand,
    x='job_count', y='skill_name',
    orientation='h',
    color_discrete_sequence=['#4CC9F0'],
    text=your_skills_demand.apply(lambda r: f"✅ {r['job_count']} jobs ({r['pct']}%)", axis=1),
    title='✅ Your Skills That Are In Demand',
    labels={'job_count': 'Number of Job Postings', 'skill_name': ''},
)
fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
fig.update_traces(textposition='outside')
fig.show()"""))

    cells.append(code("""# Skills Gap — What you're missing that employers want
gap_skills = (
    all_skill_demand[~all_skill_demand['you_have']]
    .sort_values('job_count', ascending=False)
    .head(15)
)

fig = px.bar(
    gap_skills,
    x='job_count', y='skill_name',
    orientation='h',
    color_discrete_sequence=['#F72585'],
    text=gap_skills.apply(lambda r: f"❌ {r['job_count']} jobs ({r['pct']}%)", axis=1),
    title='❌ Skills Gap — High-Demand Skills You Should Learn',
    labels={'job_count': 'Number of Job Postings', 'skill_name': ''},
)
fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
fig.update_traces(textposition='outside')
fig.show()"""))

    cells.append(code("""# Combined View: Have vs Gap
top_all = all_skill_demand.head(25).copy()
top_all['status'] = top_all['you_have'].map({True: '✅ You Have', False: '❌ Gap'})

fig = px.bar(
    top_all,
    x='job_count', y='skill_name',
    orientation='h',
    color='status',
    color_discrete_map={'✅ You Have': '#4CC9F0', '❌ Gap': '#F72585'},
    text=top_all['pct'].apply(lambda x: f"{x}%"),
    title='🎯 Top 25 Skills: Your Coverage vs Market Demand',
    labels={'job_count': 'Number of Job Postings', 'skill_name': ''},
)
fig.update_layout(height=650, yaxis={'categoryorder': 'total ascending'}, legend_title='')
fig.update_traces(textposition='outside')
fig.show()"""))

    cells.append(code("""# Job Category Fit — How many jobs can you apply to per category?
def check_fit(row):
    \"\"\"Check if candidate meets at least 60% of required skills for a job.\"\"\"
    job_id = row['job_id']
    required = set(
        job_skills[job_skills['job_id'] == job_id]
        .merge(skills, on='skill_id')['skill_name']
    )
    if not required:
        return True
    match = len(required & set(MY_SKILLS))
    return match / len(required) >= 0.4  # 40% threshold

# Sample for speed
sample_jobs = jobs.sample(min(500, len(jobs)), random_state=42)
sample_jobs['qualifies'] = sample_jobs.apply(check_fit, axis=1)

fit_by_cat = (
    sample_jobs.groupby('job_category')
    .agg(total=('qualifies', 'count'), qualifies=('qualifies', 'sum'))
    .reset_index()
)
fit_by_cat['fit_pct'] = (fit_by_cat['qualifies'] / fit_by_cat['total'] * 100).round(1)
fit_by_cat = fit_by_cat.sort_values('fit_pct', ascending=False)

fig = px.bar(
    fit_by_cat,
    x='job_category', y='fit_pct',
    color='fit_pct',
    color_continuous_scale='RdYlGn',
    text=fit_by_cat['fit_pct'].apply(lambda x: f"{x}%"),
    title='🎯 Your Qualification Rate by Job Category (40% skill match threshold)',
    labels={'fit_pct': 'Qualification Rate (%)', 'job_category': ''},
    range_color=[0, 100],
)
fig.update_layout(height=400, coloraxis_showscale=False)
fig.update_traces(textposition='outside')
fig.show()"""))

    # ============================================================
    # 7. TAKEAWAYS
    # ============================================================
    cells.append(md("""---
## 7. Key Takeaways <a id="7-takeaways"></a>"""))

    cells.append(code("""# Generate automated takeaways
print("=" * 60)
print("📋 KEY FINDINGS")
print("=" * 60)

# Top 3 skills
top3 = skill_demand.head(3)
print(f\"\"\"
1. TOP SKILLS: {top3.iloc[0]['skill_name'].upper()} ({top3.iloc[0]['pct']}%),
   {top3.iloc[1]['skill_name'].upper()} ({top3.iloc[1]['pct']}%),
   {top3.iloc[2]['skill_name'].upper()} ({top3.iloc[2]['pct']}%)

2. SALARY RANGE:
   - Data Analyst: ${salary_jobs[salary_jobs['job_category']=='Data Analyst']['salary_avg'].median():,.0f} median
   - Data Scientist: ${salary_jobs[salary_jobs['job_category']=='Data Scientist']['salary_avg'].median():,.0f} median
   - Data Engineer: ${salary_jobs[salary_jobs['job_category']=='Data Engineer']['salary_avg'].median():,.0f} median

3. YOUR FIT: {fit_score:.0f}% of in-demand skills covered
   Top gaps: {', '.join(gap_skills.head(5)['skill_name'].tolist())}

4. MARKET COMPOSITION:
   - {category_counts.iloc[0]['Category']}: {category_counts.iloc[0]['Percentage']}% of postings
   - {total_companies} unique companies hiring
   - {work_counts.iloc[0]['Work Model']}: {work_counts.iloc[0]['Count']/total_jobs*100:.0f}% of roles
\"\"\")

print("=" * 60)
print("💡 RECOMMENDATIONS")
print("=" * 60)
print(f\"\"\"
1. Focus applications on: Data Analyst & Data Scientist roles
2. Learn next: {', '.join(gap_skills.head(3)['skill_name'].tolist())}
3. Highlight: Python, SQL, ML, Docker — your strongest assets
4. Target companies: {', '.join(top_companies.head(5)['company'].tolist())}
\"\"\")"""))

    cells.append(code("""# Close database connection
conn.close()
print("✅ Analysis complete. Database connection closed.")"""))

    # Build notebook structure
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12.0"
            }
        },
        "cells": cells
    }

    return notebook


if __name__ == "__main__":
    notebook = build_notebook()

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_eda_analysis.ipynb")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

    print(f"✅ Notebook saved to {output_path}")
    print(f"   Cells: {len(notebook['cells'])}")
    print(f"\n   Run with: jupyter notebook notebooks/03_eda_analysis.ipynb")
