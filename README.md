# 🌍 World Economic Intelligence Dashboard

An interactive bilingual platform for exploring, analyzing, and assessing the macroeconomic environment of **217 countries**, from **2000 to 2024**.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/statsmodels-6A5ACD?style=flat" alt="statsmodels" />
  <img src="https://img.shields.io/badge/World%20Bank%20API-0072BC?style=flat" alt="World Bank API" />
</p>

> 🇫🇷 **Version française :** [README-fr.md](README-fr.md)

---

## Preview

_Add a screenshot or an animated GIF of the application here._

---

## Key Features

- **PESTEL Analysis Framework** – Explore **58 World Bank indicators** organized into six strategic dimensions: Political, Economic, Social, Technological, Environmental, and Legal & Governance.
- **Interactive World Maps** – Switch between Choropleth and Bubble Maps with adaptive color scales (including percentile clipping for better contrast) to quickly identify regional disparities.
- **Trends & Correlation Analysis** – Analyze historical trends by region or income group and discover relationships between indicators using integrated Ordinary Least Squares (OLS) regression, with annotated historical events (2008, 2020, 2022).
- **Comprehensive Country Profiles** – Access an analytical overview for every country, including:
  - Interactive geographic map with automatic country zoom
  - PESTEL performance radar (inverse indicators correctly inverted)
  - Trade balance waterfall chart
  - 100% stacked sector evolution area chart
  - Normalized indicator heatmap (last 10 years)
  - Dual-axis GDP vs inflation chart
  - Key Performance Indicators (KPIs) with year-on-year delta
  - Economic sector breakdown (donut chart)
- **Multi-country Comparison** – Compare up to 12 countries simultaneously across any available indicator, with a line chart, ranking bars, and a summary table with year-on-year deltas.
- **Structural Economic Analysis** – Visualize sector contributions (Agriculture, Industry, Services) through Treemaps, analyze indicator distributions with Violin Plots, and browse Top/Bottom 10 rankings.
- **Interactive Data Explorer** – Browse the complete dataset with advanced filtering (by year, region, PESTEL pillar), null-safe conditional formatting, and one-click CSV export.
- **Fully Bilingual Interface** – Instantly switch the entire application — charts, labels, legends, tooltips, and table headers — between English and French without reloading the page. All **180+ translation keys** are managed in a single `translations.py` file, with a built-in parity validator.
- **Source code 100% in English** – All variable names, comments, docstrings, and function names are written in English. Only user-facing text is bilingual, handled through the translation layer.

---

## PESTEL Framework

The dashboard organizes **58 World Bank indicators** into six strategic dimensions commonly used in environmental scanning and strategic analysis.

| Dimension            | #  | Example Indicators                                                                     |
| -------------------- | -- | -------------------------------------------------------------------------------------- |
| Political            | 5  | Military expenditure, Foreign aid, Government effectiveness, Political stability       |
| Economic             | 18 | GDP, GDP per capita, GDP growth, Inflation, Debt, Trade, FDI, Reserves, Sector value added |
| Social               | 14 | Population, Unemployment, Youth unemployment, Life expectancy, Gini, HDI, Literacy, Health & education expenditure |
| Technological        | 8  | R&D expenditure, Patent applications, High-tech exports, Internet access, Mobile & broadband subscriptions |
| Environmental        | 8  | CO₂ & GHG emissions, Renewable energy, Forest & arable land, Electricity access, Cereal yield |
| Legal & Governance   | 5  | Corruption perception (CPI), Rule of law, Time to start a business, Women in parliament |

> **Note:** Indicators where a *higher* value is *worse* (inflation, debt, unemployment, CO₂, etc.) are flagged as **inverse indicators**. They are automatically inverted in the PESTEL radar, colored with a "higher = worse" scale, and ranked in the correct direction.

---

## Project Structure

```text
world-economic-dashboard/
├── app.py                  # Main Streamlit application (English code, bilingual UI)
├── translations.py         # Centralized EN/FR translation dictionary (180+ keys) + validator
├── requirements.txt        # Python dependencies
├── data/
│   ├── world_economic.csv  # Aggregated dataset (217 countries × 2000–2024)
│   └── fetch_data.py       # World Bank API v2 data collection script
├── README-en-us.md         # English documentation (this file)
└── README-fr.md            # French documentation
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/maxin-dac/world-economic-dashboard.git
cd world-economic-dashboard
```

### 2. Create a virtual environment

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Refresh the dataset

The project includes a preprocessed dataset at `data/world_economic.csv`.

> **Note:** This file is generated from real World Bank API data. The values are accurate. To fetch the latest figures directly:

```bash
python data/fetch_data.py
```

This script calls the World Bank REST API v2 directly (no third-party wrapper), handles pagination automatically, and overwrites `world_economic.csv`. Allow 3–5 minutes for the full fetch (~58 indicators × 217 countries).

### 5. Run the application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### 6. (Optional) Validate translations

```bash
python translations.py
```

This runs the built-in parity validator and reports any missing or malformed keys between the English and French dictionaries.

---

## Dependencies

| Package     | Version | Purpose                                              |
| ----------- | ------- | ---------------------------------------------------- |
| streamlit   | ≥ 1.35  | Web interface                                        |
| plotly      | ≥ 5.20  | All charts and maps                                  |
| pandas      | ≥ 2.0   | Data loading and manipulation                        |
| numpy       | ≥ 1.26  | Numerical operations                                 |
| statsmodels | ≥ 0.14  | OLS trendlines in scatter plots                      |
| matplotlib  | ≥ 3.7   | Color gradient computation for the data table        |
| requests    | ≥ 2.31  | HTTP client for World Bank API calls                 |

All dependencies are listed in `requirements.txt` and install with a single `pip install -r requirements.txt`.

---

## Deployment

The application is fully configured for deployment on **Streamlit Community Cloud**.

### Deploy in a few steps

1. Push the project to your GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New App**.
4. Select the repository `maxin-dac/world-economic-dashboard`, branch `main`, entry point `app.py`.
5. Click **Deploy**.

Once deployed, your dashboard will be publicly accessible through a unique Streamlit URL — shareable on LinkedIn, GitHub, or with clients.

---

## Dashboard Overview

| Tab                | Content                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------- |
| 🗺️ World Map       | Choropleth or bubble map · percentile-clipped color scale · regional medians                 |
| 📈 Trends          | Time series by region or income group · OLS scatter · event annotations (2008, 2020, 2022)   |
| 🔎 Country Profile | Geographic zoom map · PESTEL radar · waterfall · 100% stacked area · heatmap · dual-axis chart · KPIs · sector donut |
| ↔️ Compare         | Up to 12 countries · line chart · ranking bars · summary table with deltas                   |
| 🏗️ Structure       | Treemap · violin plot · top/bottom 10 ranking                                                |
| 📋 Data            | PESTEL filter · null-safe conditional formatting · CSV export                                |

---

## Data Source

**World Development Indicators (WDI) — World Bank Open Data**

- API endpoint: `https://api.worldbank.org/v2/country/all/indicator/{CODE}?format=json`
- Data is collected via direct REST API calls (no third-party wrapper), cleaned, and saved to `world_economic.csv`.
- Licence: [World Bank Open Data Terms of Use](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets)

---

## Use Cases

Business Intelligence · Country benchmarking · Economic analysis · Strategic planning · Academic research · Market intelligence · Public policy analysis · International business studies

---

## Future Improvements

- AI-powered country recommendations
- Forecasting and predictive analytics
- Time-series anomaly detection
- PDF and PowerPoint report export
- OECD and IMF data integration
- Custom dashboard builder

---

## Author

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

- GitHub: [github.com/maxin-dac](https://github.com/maxin-dac)
- LinkedIn: [linkedin.com/in/maximendacleu](https://www.linkedin.com/in/maximendacleu)

---

## License

Distributed under the **MIT License**. The datasets are provided by the World Bank under its Open Data License.
