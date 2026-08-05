# 🌍 Global Economic Intelligence Dashboard

> **Problem**: public macroeconomic data is scattered, technical, and rarely presented in a comparable, educational, and strategic way.  
> **Solution**: an open-source, bilingual, interactive platform aggregating **58 World Bank / Our World in Data indicators** for **217 countries (2000–2024)**, structured around the **PESTEL framework**, with a decision-support module for risk, attractiveness, and opportunity screening.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=matplotlib&logoColor=white" alt="Matplotlib" />
  <img src="https://img.shields.io/badge/Statsmodels-4B3F72?style=for-the-badge" alt="Statsmodels" />
  <img src="https://img.shields.io/badge/Requests-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Requests" />
  <img src="https://img.shields.io/badge/pycountry-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="pycountry" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/World_Bank_API-0072BC?style=for-the-badge" alt="World Bank API" />
  <img src="https://img.shields.io/badge/MIT_License-green?style=for-the-badge" alt="MIT License" />
</p>

<p align="left">
  <a href="https://world-bi-dashboard.streamlit.app/">
    <img src="https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" />
  </a>
</p>

![Overview](image-1.png)

🇫🇷 Version française : [README-fr.md](README-fr.md)

---

## In brief - Overview

- **What it does**: explore, compare, and analyze 217 countries using macroeconomic, social, technological, environmental, and governance indicators.
- **Skills involved**: data engineering, exploratory analysis, statistics, data visualization, bilingual UX, dashboarding.
- **Demo**: [world-bi-dashboard.streamlit.app](https://world-bi-dashboard.streamlit.app/)
- **Stack**: Python · Streamlit · Plotly · Pandas · NumPy · Statsmodels · World Bank API

## Key Features

- 🗺️ **World Map** : choropleth or bubble maps, with regional medians.
- 📈 **Trends & Correlations** : time series, OLS scatter plots, annotated shocks for 2008, 2020 and 2022.
- 🔎 **Country Profile** : PESTEL radar, GDP vs inflation, sector structure, trade balance, 10-year heatmap.
- ↔️ **Country Comparison** : up to 12 countries, line charts, ranking and year-on-year summary table.
- 🏗️ **Economic Structure** : sector treemap, GDP per capita distribution, top 10 / bottom 10 rankings.
- 📋 **Data Explorer** : filters, conditional formatting, CSV export.
- 💎 **Investment Score** : attractiveness score, risk/reward matrix, red-flag detection and clean opportunity shortlist.

## Quick Start

```bash
pip install -r requirements.txt
python data/fetch_data.py
streamlit run app.py
```

## PESTEL Framework

| Pillar | Example Indicators |
|---|---|
| Political | Political stability, government effectiveness, military expenditure |
| Economic | GDP, growth, inflation, debt, trade, FDI, reserves |
| Social | Population, health, education, employment, inequality |
| Technological | Internet, mobile, R&D, financial inclusion |
| Environmental | Electricity access, PM2.5 pollution, cereal yield |
| Legal & Governance | Corruption, rule of law, regulatory quality, transparency |

## Investment Score

A decision-support module to quickly compare countries by attractiveness and risk level.

<details>
<summary>Score weighting</summary>

| Weight | Indicator | Direction |
|---:|---|---|
| 20% | GDP growth | Higher = better |
| 20% | Political stability | Higher = better |
| 15% | Control of corruption | Higher = better |
| 15% | Inflation | Lower = better |
| 10% | Public debt | Lower = better |
| 10% | Trade openness | Higher = better |
| 5% | Electricity access | Higher = better |
| 5% | Internet users | Higher = better |

</details>

<details>
<summary>Risk flags</summary>

| Signal | Threshold | Severity |
|---|---:|:---:|
| Inflation | > 10% | 🔴 |
| Public debt | > 80% of GDP | 🔴 |
| Unemployment | > 15% | 🔴 |
| Political stability | < -1 | 🔴 |
| Corruption perception | < 25 | 🔴 |
| Inflation | 5–10% | 🟡 |
| Public debt | 50–80% of GDP | 🟡 |

</details>

## Data Sources

| Source | Coverage | Access |
|---|---|---|
| World Bank — WDI | 56 indicators, 217 countries, 2000–2024 | Public API |
| Our World in Data | HDI, Corruption Perceptions Index | Public CSV |

## Limitations

The Investment Score is a **first-pass screening tool**, not an econometrically validated index. Weights are analyst choices, and missing data may disadvantage the most fragile countries.

<details>
<summary>More details</summary>

- Min-max normalization is sensitive to extreme values.
- Some development indicators are highly correlated.
- Political, currency and sovereign-default risk are only partially captured.
- The 5-year CAGR reflects past dynamics, not guaranteed future returns.

</details>

## Project Structure

```text
world-economic-dashboard/
├── .streamlit/
│   └── config.toml
├── assets/
│   └── style.css
├── data/
│   ├── fetch_data.py
│   └── world_economic.csv
├── app.py
├── translations.py
├── requirements.txt
├── LICENSE
├── README.md
└── README-fr.md
```

---

## Author

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

<p align="left">
  <a href="https://github.com/maxin-dac">
    <img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  </a>
  <a href="https://www.linkedin.com/in/maximendacleu">
    <img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
</p>

---

## License

MIT License. Data provided by the World Bank and Our World in Data.