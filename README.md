# 🌍 Global Economic Intelligence Dashboard

Interactive bilingual platform (EN/FR) - 217 countries · 2000-2024 · 58 World Bank indicators structured around the **PESTEL** framework, plus a dedicated **Investment Intelligence** module.

<p align="left">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
<img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
<img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white" alt="Matplotlib" />
<img src="https://img.shields.io/badge/Statsmodels-4B3F72?style=flat" alt="Statsmodels" />
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white" alt="pytest" />
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="GitHub Actions" />
<img src="https://img.shields.io/badge/World_Bank_API-0072BC?style=flat" alt="World Bank API" />
<img src="https://img.shields.io/badge/MIT_License-green?style=flat" alt="MIT License" />
</p>

<p align="left">
<a href="https://world-bi-dashboard.streamlit.app/">
<img src="https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" />
</a>
</p>

![Overview](static/globe.png)

> **French version:** [README-fr.md](README-fr.md)

## Features

**7 coordinated views** + specialized analytical modules:

- **World Map** - Choropleth + bubble maps, percentile clipping, regional median cards.
- **Trends & Correlations** - Time series by region/income, annotated shock lines (2008, 2020, 2022), OLS scatter plots.
- **Country Profile** - PESTEL radar, 10-year normalized heatmap, dual-axis GDP/inflation, trade balance waterfall.
- **Country Comparison & Similarity** - Multi-country benchmarking (up to 12 countries) and peer similarity matching engine.
- **Economic Structure & Resilience** - Sectoral treemap, log-scale violin plot of GDP/capita, resilience & shock analysis.
- **Data Explorer & Quality Audit** - Filterable dataset with missingness audit, null-safe conditional formatting, one-click CSV export.
- **Investment Score** - Composite 0-100 attractiveness score (8 weighted indicators), risk/return 4-quadrant matrix, red-flag detector, clean-opportunity shortlist.

## PESTEL Coverage (58 indicators)

| Pillar | # | Examples |
|---|---|---|
| Political | 4 | Military expenditure, Government Effectiveness, Political Stability (WGI) |
| Economic | 20 | GDP, GDP/capita, Growth, Inflation, Public Debt, Trade Openness, FDI, Current Account |
| Social | 16 | Population, Life Expectancy, HDI, Gini, Unemployment, Literacy, Infant Mortality |
| Technological | 7 | R&D, Researchers, High-tech exports, Internet users, Mobile subscriptions |
| Environmental | 4 | PM2.5, Electricity access, Power losses, Cereal yield |
| Legal & Governance | 7 | Corruption Control, Rule of Law, Regulatory Quality, CPI, Transparency score |

## Project Architecture

```
world-economic-dashboard/
├── .github/workflows/
│   ├── lint.yml                      # CI code quality & syntax validation
│   └── update-data.yml               # Monthly automated data refresh pipeline
├── .streamlit/config.toml            # Streamlit theme & UI settings
├── assets/style.css                  # Custom styling & glassmorphism CSS
├── core/                             # Core modular python package
│   ├── __init__.py
│   ├── analytics.py                  # Statistical analytics & data transformations
│   ├── constants.py                  # PESTEL definitions, colors & indicator schemas
│   ├── data.py                       # Cached data loading & optimization
│   ├── indicators.py                 # Indicator calculation engines
│   ├── investment.py                 # Investment scoring & quadrant algorithms
│   └── labels.py                     # Multilingual label resolvers
├── data/
│   ├── fetch_data.py                 # World Bank API data ingestion pipeline
│   └── world_economic.csv            # Aggregated dataset (217 countries x 2000-2024)
├── docs/OPERATIONS.md                # Maintenance & operations documentation
├── static/
│   └── globe.png                     # Dashboard visual assets
├── tests/
│   └── test_investment.py            # Pytest automated test suite
├── app.py                            # Streamlit entry point application
├── dataquality.py                    # Data quality auditing & coverage reporting
├── exports.py                        # Custom report & data exporting engine
├── resilience.py                     # Economic resilience & vulnerability module
├── similar.py                        # Country similarity algorithm engine
├── translations.py                   # Multilingual (EN/FR) translation matrix
├── Dockerfile                        # Production Docker container configuration
├── .dockerignore                     # Docker build optimization rules
├── requirements.txt                  # Python dependencies
├── LICENSE                           # MIT License
├── README.md                         # English Documentation
└── README-fr.md                      # French Documentation
```

## Quick Start & Installation

### Option 1: Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/maxin-dac/world-economic-dashboard.git
   cd world-economic-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

### Option 2: Docker Setup

1. **Build the Docker image:**
   ```bash
   docker build -t world-economic-dashboard .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 world-economic-dashboard
   ```

3. Open `http://localhost:8501` in your web browser.

## Stack & Data Pipeline

**Python 3.12 · Streamlit · Docker · Plotly · Pandas · NumPy · Matplotlib · Statsmodels · pytest · GitHub Actions**

Data is ingested from the **World Bank REST API** and **Our World in Data**, and **automatically updated on the first Monday of every month** via a GitHub Actions CI/CD pipeline (tests, data fetch, changelog generation, auto-commit, and Streamlit Cloud redeployment).

## Data Quality & Limitations

- 2024 is the latest fully validated year (12-18 month World Bank publication lag)
- Null cells rendered as "**-**" (tables) / "**N/A**" (KPI cards) with neutral gray background
- Dedicated data quality module monitors coverage rates, missingness, and indicator health

## Author

**Maxime NDACLEU** - Data Analyst & Business Intelligence Analyst

<p>
<a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

## License

Distributed under the **MIT License** (see [LICENSE](LICENSE)).
Data provided by the **World Bank** (Open Data License) and **Our World in Data** (CC BY).
