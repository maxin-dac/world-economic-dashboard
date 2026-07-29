# 🌍 Global Economic Intelligence Dashboard

An interactive bilingual platform for exploring the macroeconomic and strategic environment of **217 countries**, from **2010 to 2024** — structured around the **PESTEL framework** and powered by **58 real World Bank indicators**.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/World%20Bank%20API-0072BC?style=flat" alt="World Bank API" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="MIT License" />
</p>

## 🚀 App Link

***Click on this button to launch the application***

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://world-bi-dashboard.streamlit.app/)

---

## Overview

<img width="1240" height="580" alt="image" src="https://github.com/user-attachments/assets/ca8ac053-1d28-46c0-a0e1-03746225ea61" />

## Why this dashboard?

Most freely available macroeconomic tools force you to choose between breadth (many countries, few indicators) and depth (rich analyses, one country at a time). This dashboard does both.

It combines **58 World Bank indicators** covering all PESTEL dimensions, data sourced directly from the official World Bank API, and a suite of visualizations designed for strategic analysis — all within a bilingual interface that is equally effective for quick country lookups and rigorous comparative studies.

## Features

### 🗺️ World Map
- Switch between **choropleth maps** (color-coded countries) and **bubble maps** (proportional circles) for any of the 58 indicators.
- Logarithmic scale for GDP per capita — ensuring every income group is visually distinguishable, not just the extremes.
- Percentile clipping for better contrast on skewed distributions.
- Regional median cards displayed directly beneath the map.

### 📈 Trends & Correlations
- Time series grouped by **region** or **income group** (2010–2024).
- Annotated vertical lines marking the **COVID-19 (2020)** and the **2022 inflation surge**.
- **OLS Scatter plots** between any two indicators, with bubble sizes proportional to economic weight.
- Contextual info banners for each indicator, explaining what the metric means and how to interpret it.

### 🔎 Country Profile
The most comprehensive module. For each of the 217 countries:
- **Geographic map** with automatic zoom centered on the selected country, highlighted in its income group's color.
- **PESTEL Radar** across 6 pillars — with inverse indicators (inflation, debt, unemployment, etc.) automatically inverted so the radar always reads "outward = better".
- **Dual-axis GDP vs. Inflation chart** — tracking economic output and price pressures on the same timeline.
- **100% stacked area chart** showing sectoral evolution (Agriculture / Industry / Services) over time.
- **Trade balance waterfall** — exports and imports side-by-side, with the net balance clearly displayed.
- **10-year normalized heatmap** — all available indicators from the last decade, standardized (z-score) by column to highlight relative performance.
- **Sectoral donut chart** for the latest available year.
- **KPI cards** with year-on-year deltas, comparison to the world median, and dynamic natural language interpretation (e.g., "HDI: very high", "above world median (unfavorable)").
- **Tooltips** on every KPI card providing static bilingual definitions and reading tips.

### ↔️ Country Comparison
- Select up to **12 countries** simultaneously.
- Time-series line charts, ranking bar charts, and a summary table with year-on-year deltas.
- Works for any of the 58 available indicators.

### 🏗️ Economic Structure
- **Treemap** of sectoral composition (Agriculture / Industry / Services) by region and income group.
- **Violin plot** of GDP per capita distribution (log scale) — showing dispersion, concentrations, and outliers by income group.
- **Top 10 / Bottom 10 rankings** for any indicator.
- **Animated chart** of sectoral evolution by region over time.

### 📋 Data Explorer
- Fully navigable dataset with advanced filtering.
- Null-safe conditional formatting with semantically correct color gradients: green = better, red = worse (inverse indicators are handled automatically).
- **One-click CSV export** of any filtered view.

## PESTEL Framework

The 58 indicators are organized into six strategic dimensions used in macroeconomic and competitive environment analysis.

| Pillar | # | Example Indicators |
|---|---|---|
| **Political** | 4 | Military expenditure (% GDP & % budget), Government Effectiveness (WGI), Political Stability (WGI) |
| **Economic** | 20 | GDP, GDP per capita (USD & PPP), Growth, Inflation, Public Debt, Trade Openness, FDI, Current Account, Remittances, FX Reserves, Sectoral value added |
| **Social** | 16 | Population, Life Expectancy, HDI, Gini Index, Unemployment, Youth Unemployment, Literacy, Infant Mortality, Fertility, Sanitation, Health & Education spending |
| **Technological** | 7 | R&D Expenditure, Researchers/million, High-tech exports, Internet users, Mobile & broadband subscriptions, Bank account ownership |
| **Environmental** | 4 | PM2.5 pollution, Electricity access, Power transmission losses, Cereal yield |
| **Legal & Governance** | 7 | Control of Corruption, Rule of Law, Regulatory Quality, Voice & Accountability (all WGI), CPI (Transparency Intl.), Transparency score, Women in parliament |

> **Inverse indicators** — where a higher value is unfavorable (inflation, debt, PM2.5, unemployment, etc.) — are handled automatically throughout the app: inverted in the PESTEL radar, colored with a "higher = worse" scale, and ranked in the correct direction.

## Project Structure

```text
world-economic-dashboard/
├── __pycache__/                    # Python cache (auto-generated)
│   ├── app.cpython-313.pyc
│   └── translations.cpython-313.pyc
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                 # App theme and settings
│
├── assets/                         # Static resources (CSS, HTML)
│   ├── _kpi_hover_en.html          # EN tooltip template (generated)
│   ├── _kpi_hover_fr.html          # FR tooltip template (generated)
│   └── style.css                   # Custom stylesheet
│
├── data/                           # Data and collection scripts
│   ├── fetch_data.py               # World Bank API collection script
│   └── world_economic.csv          # Aggregated dataset (217 countries × 2010-2024)
│
├── .gitignore                      # Files to ignore in Git
├── app.py                          # Main Streamlit application
├── translations.py                 # EN/FR translation dictionary
├── requirements.txt                # Python dependencies
├── README-en-us.md                 # This file, English documentation
└── README-fr.md                    # French documentation
```

## Data Sources

| Source | Coverage | Access |
|---|---|---|
| [World Bank — World Development Indicators (WDI)](https://databank.worldbank.org/source/world-development-indicators) | 56 indicators · 217 countries · 2010–2024 | Free REST API (`api.worldbank.org/v2`) |
| [Our World in Data — HDI](https://ourworldindata.org/human-development-index) | Human Development Index | Free CSV download (CC BY) |
| [Our World in Data — CPI](https://ourworldindata.org/corruption) | Corruption Perceptions Index | Free CSV download (CC BY) |

All data is open and freely accessible. World Bank data is used in accordance with the [World Bank Open Data Terms of Use](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).

## Data Availability & Limitations

### Why is some data missing for certain countries?

Several factors explain gaps in the dataset:

1. **Variable national statistical capacities** — Developing countries may lack the resources or infrastructure needed for regular, standardized data collection, leading to irregular or missing reports.
2. **Creation and dissolution of countries** — Some countries simply did not exist before certain dates. South Sudan, for example, was created in 2011; data for prior years is structurally absent.
3. **Conflicts and political instability** — Wars, crises, and state fragility disrupt data collection and publication chains, sometimes for years.
4. **Publication delays** — International organizations typically take 12 to 18 months to validate, harmonize, and publish official data. The most recent calendar year is almost never fully covered.
5. **Indicator-specific coverage** — Some indicators only apply to subsets of countries: the CPIA transparency score, for instance, only applies to IDA-eligible countries; the Gini index is measured irregularly and with varying frequency across countries.
6. **Methodological differences** — Countries may use different calculation standards that are not directly comparable, leading to intentional exclusions during harmonization.

The dashboard displays all available data transparently. Missing cells are indicated by a neutral "None" marker without color formatting, ensuring gaps are never confused with low values.

### Why does the analysis period end in 2024?

1. **Data availability** — 2024 represents the most recent validated data published by the World Bank at the time of development.
2. **World Bank publication cycle** — Data is published with a 12 to 18-month lag. Complete indicator coverage for 2024 will not be available until late 2025 or 2026, depending on the metric.
3. **Consistency** — Setting 2024 as the end year ensures all 58 indicators have comparable, validated coverage, rather than mixing preliminary and final figures.
4. **Easy updating** — The `fetch_data.py` script can be rerun at any time.

> **Note:** A **Refresh from API** button is available in the dashboard sidebar. A single run updates all 58 indicators for all 217 countries in one pass.

## Use Cases

- **Business Intelligence** — Country risk scoring, market entry evaluation.
- **Strategic Planning** — PESTEL environmental analysis for any country or region.
- **Country Benchmarking** — Side-by-side comparison of up to 12 countries.
- **Academic Research** — 15 years of harmonized World Bank data, exportable to CSV.
- **Economic Intelligence** — Tracking macroeconomic trends in emerging markets.
- **Public Policy Analysis** — Monitoring governance, development, and sustainability indicators.
- **Education** — Interactive exploration of global economic data.

## Author

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

[![GitHub](https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white)](https://github.com/maxin-dac)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maximendacleu)

---

## License

Distributed under the **MIT License**.
Data provided by the **World Bank** (Open Data License) and **Our World in Data** (CC BY).
