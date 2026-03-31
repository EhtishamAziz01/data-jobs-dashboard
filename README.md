# 🇮🇪 Ireland Data Jobs Market Dashboard

An end-to-end data analytics project analyzing job listings to uncover trends, in-demand skills, and salary insights in Ireland's data job market.

## 📊 Key Findings

> *Coming soon — dashboard and analysis in progress.*

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| **Data Collection** | Python, BeautifulSoup, Requests |
| **Data Processing** | Pandas, NumPy |
| **Database** | DuckDB |
| **Visualization** | Power BI, Plotly, Seaborn |
| **Notebooks** | Jupyter |

## 🏗️ Project Structure

```
Project1/
├── data/
│   ├── raw/                  # Raw scraped/imported data
│   ├── processed/            # Cleaned, transformed data
│   └── reference/            # Skill keyword dictionary, lookups
├── notebooks/                # EDA and analysis notebooks
├── src/
│   ├── scraper/              # Job listing scrapers
│   ├── cleaning/             # Data cleaning & skill extraction
│   └── database/             # Schema & data loading
├── dashboard/                # Power BI files & screenshots
├── reports/                  # Written analysis report
└── docs/                     # Data dictionary & documentation
```

## 🚀 Setup

```bash
# Clone the repository
git clone <repo-url>
cd Project1

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the data pipeline
python src/scraper/run_scraper.py
python src/cleaning/run_cleaning.py
python src/database/load_data.py
```

## 📈 Dashboard Preview

> *Screenshots coming soon.*

## 👤 Author

**Ehtisham Aziz** — Junior Data Analyst | Data Scientist
- [LinkedIn](https://linkedin.com)
- [GitHub](https://github.com)
