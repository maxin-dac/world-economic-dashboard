# 🌍 Global Economic Intelligence Dashboard

Interactive bilingual platform (EN/FR) - 217 countries · 2000-2024 · 58 World Bank indicators structured around the **PESTEL** framework, plus a dedicated **Investment Intelligence** module.

<p align="left">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
<img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
<img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white" alt="Matplotlib" />
<img src="https://img.shields.io/badge/Statsmodels-4B3F72?style=flat" alt="Statsmodels" />
<img src="https://img.shields.io/badge/Requests-3776AB?style=flat&logo=python&logoColor=white" alt="Requests" />
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white" alt="pytest" />
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="GitHub Actions" />
<img src="https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white" alt="HTML5" />
<img src="https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white" alt="CSS3" />
<img src="https://img.shields.io/badge/World_Bank_API-0072BC?style=flat" alt="World Bank API" />
<img src="https://img.shields.io/badge/MIT_License-green?style=flat" alt="MIT License" />
</p>

<p align="left">
<a href="https://world-bi-dashboard.streamlit.app/">
<img src="https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" />
</a>
</p>

![Overview](assets/image-3.png)

> **French version:** [README-fr.md](README-fr.md)

## Features

**7 coordinated views** + 1 investment module:

- **World Map** - choropleth + bubble maps, percentile clipping, regional median cards
- **Trends & Correlations** - time series by region/income, annotated shock lines (2008, 2020, 2022), OLS scatter
- **Country Profile** - PESTEL radar, 10-year normalized heatmap, dual-axis GDP/inflation, sectoral area chart, trade balance waterfall, sectoral donut
- **Country Comparison** - up to 12 countries, time series + ranking bars + summary table
- **Economic Structure** - sectoral treemap, log-scale violin plot of GDP/capita, Top/Bottom 10 rankings
- **Data Explorer** - filterable dataset, null-safe conditional formatting, one-click CSV export
- **Investment Score** - composite 0-100 attractiveness score (8 weighted indicators), risk/return 4-quadrant matrix, red-flag detector, clean-opportunity shortlist

## PESTEL Coverage (58 indicators)

| Pillar | # | Examples |
|---|---|---|
| Political | 4 | Military expenditure, Government Effectiveness, Political Stability (WGI) |
| Economic | 20 | GDP, GDP/capita, Growth, Inflation, Public Debt, Trade Openness, FDI, Current Account |
| Social | 16 | Population, Life Expectancy, HDI, Gini, Unemployment, Literacy, Infant Mortality |
| Technological | 7 | R&D, Researchers, High-tech exports, Internet users, Mobile subscriptions |
| Environmental | 4 | PM2.5, Electricity access, Power losses, Cereal yield |
| Legal & Governance | 7 | Corruption Control, Rule of Law, Regulatory Quality, CPI, Transparency score |

## Project Structure

    world-economic-dashboard/
    ├── .github/workflows/
    │   └── update-data.yml              # Monthly CI/CD pipeline
    ├── .streamlit/config.toml           # App theme
    ├── assets/style.css                 # Custom stylesheet
    ├── data/
    │   ├── fetch_data.py                # World Bank API collector
    │   └── world_economic.csv           # Aggregated dataset (217 x 2000-2024)
    ├── docs/OPERATIONS.md               # Operations guide
    ├── scripts/changelog_entry.py       # Auto-generated changelog
    ├── tests/test_investment.py         # pytest suite
    ├── CHANGELOG.md                     # Monthly data refresh history
    ├── app.py                           # Streamlit application
    ├── translations.py                  # EN/FR dictionary
    ├── requirements.txt                 # Dependencies
    ├── LICENSE                          # MIT
    ├── README.md                        # This file
    └── README-fr.md                     # French documentation

## Stack

**Python · Streamlit · Plotly · Pandas · NumPy · Matplotlib · Statsmodels · pytest · GitHub Actions**

Data pulled from the **World Bank REST API** and **Our World in Data**, **automatically refreshed on the first Monday of every month** via a GitHub Actions pipeline (test, fetch, changelog, commit, Streamlit Cloud redeploy). Manual trigger available from the repository's Actions tab.

## Data Quality & Limitations

- 2024 is the latest fully validated year (12-18 month World Bank publication lag)
- Null cells rendered as "**-**" (tables) / "**N/A**" (KPI cards) with neutral gray background
- Monthly changelog tracks coverage, null rates, and lowest-coverage indicators

## Author

**Maxime NDACLEU** - Data Analyst & Business Intelligence Analyst

<p>
<a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

## License

Distributed under the **MIT License** (see [LICENSE](LICENSE)).
Data provided by the **World Bank** (Open Data License) and **Our World in Data** (CC BY).
