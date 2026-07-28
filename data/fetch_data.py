"""
World Bank API + Our World in Data (OWID) - Unified Data Extraction Script

Retrieves 58 macroeconomic and social indicators for 217 countries (2000-2024),
organized for PESTEL analysis:
  - 56 indicators from the World Bank API v2
  - 2 supplementary indicators from Our World in Data (HDI, Corruption Perceptions Index)

NOTE: The Worldwide Governance Indicators (WGI) live in a separate World Bank
database and require the "GOV_WGI_" prefix (e.g. GOV_WGI_GE.EST). The legacy
unprefixed codes (GE.EST, RL.EST, ...) return empty payloads.

Output: data/world_economic.csv  (single unified file)
OWID data is licensed CC-BY. Source: https://ourworldindata.org
"""

import os
import time
import logging
from io import StringIO

import requests
import pandas as pd
import numpy as np


# ── Logging configuration ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Constants ───────────────────────────────────────────────────────────────
BASE_URL = "http://api.worldbank.org/v2"
START_YEAR = 2000
END_YEAR = 2024

MAX_RETRIES = 3          # attempts per World Bank indicator
REQUEST_DELAY = 0.6      # seconds between requests (avoids rate-limiting)

OWID_TIMEOUT = 120
OWID_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EconomicDashboard/1.0)"}


# ── World Bank indicators (56) ──────────────────────────────────────────────
INDICATORS = {
    # P - Political
    "MS.MIL.XPND.GD.ZS":    "military_expenditure_pct_gdp",
    "MS.MIL.XPND.ZS":       "military_expenditure_pct_govt",
    "GOV_WGI_GE.EST":       "govt_effectiveness_index",
    "GOV_WGI_PV.EST":       "political_stability_index",

    # E - Economic
    "NY.GDP.PCAP.CD":       "gdp_per_capita",
    "NY.GDP.PCAP.PP.CD":    "gdp_per_capita_ppp",
    "NY.GDP.MKTP.CD":       "gdp_total_usd",
    "NY.GDP.MKTP.KD.ZG":    "gdp_growth_pct",
    "NE.GDI.TOTL.ZS":       "gross_fixed_capital_formation_pct_gdp",
    "NE.TRD.GNFS.ZS":       "trade_openness_pct_gdp",
    "FP.CPI.TOTL.ZG":       "inflation",
    "FP.CPI.TOTL":          "cpi_index_raw",
    "PA.NUS.FCRF":          "exchange_rate",
    "GC.DOD.TOTL.GD.ZS":    "debt_pct_gdp",
    "GC.REV.XGRT.GD.ZS":    "tax_revenue_pct_gdp",
    "NE.EXP.GNFS.ZS":       "exports_pct_gdp",
    "NE.IMP.GNFS.ZS":       "imports_pct_gdp",
    "BX.KLT.DINV.WD.GD.ZS": "fdi_pct_gdp",
    "BN.CAB.XOKA.GD.ZS":    "current_account_pct_gdp",
    "BX.TRF.PWKR.DT.GD.ZS": "remittances_pct_gdp",
    "FI.RES.TOTL.MO":       "reserves_months_imports",
    "NV.AGR.TOTL.ZS":       "agriculture_pct",
    "NV.IND.TOTL.ZS":       "industry_pct",
    "NV.SRV.TOTL.ZS":       "services_pct",

    # S - Social
    "SP.POP.TOTL":          "population",
    "SL.UEM.TOTL.ZS":       "unemployment_pct",
    "SL.UEM.1524.ZS":       "youth_unemployment_pct",
    "SL.TLF.ACTI.ZS":       "labor_force_participation_pct",
    "SP.DYN.LE00.IN":       "life_expectancy",
    "SE.ADT.LITR.ZS":       "literacy_rate",
    "SE.PRM.CMPT.ZS":       "primary_completion_rate_pct",
    "SE.SEC.ENRR":          "school_enrollment_secondary_pct",
    "SH.DYN.MORT":          "under5_mortality_per_1000",
    "SP.DYN.TFRT.IN":       "fertility_rate",
    "SI.POV.GINI":          "gini_index",
    "SP.URB.TOTL.IN.ZS":    "urban_population_pct",
    "SH.STA.BASS.ZS":       "basic_sanitation_access_pct",
    "SH.XPD.CHEX.PC.CD":    "health_expenditure_per_capita",
    "SE.XPD.TOTL.GD.ZS":    "education_expenditure_pct_gdp",

    # T - Technological
    "GB.XPD.RSDV.GD.ZS":    "rd_expenditure_pct_gdp",
    "SP.POP.SCIE.RD.P6":    "researchers_per_million",
    "TX.VAL.TECH.MF.ZS":    "high_tech_exports_pct",
    "IT.NET.USER.ZS":       "internet_users_pct",
    "IT.CEL.SETS.P2":       "mobile_subscriptions_per_100",
    "IT.NET.BBND.P2":       "fixed_broadband_per_100",
    "FX.OWN.TOTL.ZS":       "bank_account_ownership_pct",

    # E - Environmental
    "EN.ATM.PM25.MC.M3":    "pm25_air_pollution",
    "EG.ELC.ACCS.ZS":       "electricity_access_pct",
    "EG.ELC.LOSS.ZS":       "electric_power_losses_pct",
    "AG.YLD.CREL.KG":       "cereal_yield_kg_per_ha",

    # L - Legal & Governance (WGI indicators require the GOV_WGI_ prefix)
    "GOV_WGI_CC.EST":       "control_of_corruption",
    "GOV_WGI_RL.EST":       "rule_of_law_index",
    "GOV_WGI_RQ.EST":       "regulatory_quality",
    "GOV_WGI_VA.EST":       "voice_accountability",
    "IQ.CPA.TRAN.XQ":       "transparency_corruption_score",
    "SG.GEN.PARL.ZS":       "women_parliament_pct",
}


# ── OWID supplementary indicators (2) ───────────────────────────────────────
OWID_SOURCES = [
    {
        "column": "hdi",
        "label": "Human Development Index (HDI)",
        "urls": ["https://ourworldindata.org/grapher/human-development-index.csv"],
    },
    {
        "column": "corruption_perception_index",
        "label": "Corruption Perceptions Index (Transparency International)",
        "urls": ["https://ourworldindata.org/grapher/ti-corruption-perception-index.csv"],
    },
]


# ── World Bank: country metadata ────────────────────────────────────────────
def fetch_country_metadata() -> pd.DataFrame:
    """Fetch metadata for all real countries (filtering out regional aggregates)."""
    url = f"{BASE_URL}/country?format=json&per_page=300"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2:
            return pd.DataFrame()

        rows = []
        for c in data[1]:
            if c.get("region", {}).get("id") != "NA":
                rows.append({
                    "iso3": c.get("id"),
                    "country": c.get("name"),
                    "region": c.get("region", {}).get("value"),
                    "income_group": c.get("incomeLevel", {}).get("value"),
                    "latitude": float(c.get("latitude")) if c.get("latitude") else np.nan,
                    "longitude": float(c.get("longitude")) if c.get("longitude") else np.nan,
                    "capital": c.get("capitalCity", ""),
                })
        return pd.DataFrame(rows)
    except Exception as e:
        log.error(f"Error fetching country metadata: {e}")
        return pd.DataFrame()


# ── World Bank: single indicator with retry + backoff ───────────────────────
def fetch_indicator(indicator_code: str, col_name: str,
                    start_year: int = START_YEAR, end_year: int = END_YEAR):
    """Fetch a time series with automatic retry and exponential backoff."""
    url = f"{BASE_URL}/country/all/indicator/{indicator_code}"
    params = {"date": f"{start_year}:{end_year}", "format": "json", "per_page": 20000}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                raise ValueError("empty payload")

            rows = []
            for item in data[1]:
                country_id = item.get("countryiso3code") or item.get("country", {}).get("id")
                val = item.get("value")
                year = item.get("date")
                if country_id and val is not None and year:
                    rows.append({"iso3": country_id, "year": int(year), col_name: float(val)})

            if not rows:
                raise ValueError("no usable rows")

            df = pd.DataFrame(rows).drop_duplicates(subset=["iso3", "year"])
            log.info(f"  ✓ {col_name:<40} {len(df):>6,} rows  ({df['iso3'].nunique()} countries)")
            return df

        except Exception as e:
            if attempt < MAX_RETRIES:
                wait = REQUEST_DELAY * attempt * 2
                log.warning(f"  ⚠ {col_name} — attempt {attempt} failed ({e}); retry in {wait:.1f}s")
                time.sleep(wait)
            else:
                log.warning(f"  ✗ {col_name} — failed after {MAX_RETRIES} attempts: {e}")
                return None

    return None


# ── OWID: fetch + normalize ─────────────────────────────────────────────────
def fetch_owid_first_available(urls):
    """Try each URL in order and return the first successful CSV as a DataFrame."""
    for url in urls:
        try:
            resp = requests.get(url, timeout=OWID_TIMEOUT, headers=OWID_HEADERS)
            resp.raise_for_status()
            df = pd.read_csv(StringIO(resp.text))
            log.info(f"  ✓ Fetched from: {url}")
            return df
        except Exception as e:
            log.warning(f"  ✗ Failed: {url} ({e})")
    return None


def normalize_owid(df):
    """Normalize an OWID grapher CSV to (iso3, year, value)."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    id_cols = {"entity", "code", "year"}

    value_col = None
    for c in df.columns:
        cl = c.lower()
        if cl in id_cols or "region" in cl:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            value_col = c
            break
    if value_col is None:
        candidates = [c for c in df.columns if c.lower() not in id_cols and "region" not in c.lower()]
        if not candidates:
            return None
        value_col = candidates[0]

    if "Code" not in df.columns:
        return None

    df = df.dropna(subset=["Code"])
    df["iso3"] = df["Code"].astype(str).str.strip().str.upper()

    out = df[["iso3", "Year", value_col]].rename(columns={"Year": "year", value_col: "value"})
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["year", "value", "iso3"])
    out["year"] = out["year"].astype(int)
    out = out[out["iso3"].str.match(r"^[A-Z]{3}$")]  # drop aggregates
    return out[["iso3", "year", "value"]]


# ── Build the unified dataset ───────────────────────────────────────────────
def build_dataset(countries: pd.DataFrame) -> pd.DataFrame:
    """Fetch all indicators (World Bank + OWID) and merge into one wide DataFrame."""

    # 1. World Bank indicators
    log.info(f"\nFetching {len(INDICATORS)} World Bank indicators...")
    frames = {}
    failed = []
    for wb_code, col_name in INDICATORS.items():
        df_ind = fetch_indicator(wb_code, col_name)
        if df_ind is not None:
            frames[col_name] = df_ind
        else:
            failed.append(col_name)
        time.sleep(REQUEST_DELAY)

    if not frames:
        raise RuntimeError("No World Bank indicator data could be retrieved.")

    df_list = list(frames.values())
    master = df_list[0]
    for df_ in df_list[1:]:
        master = master.merge(df_, on=["iso3", "year"], how="outer")

    # 2. OWID supplementary indicators
    log.info(f"\nFetching {len(OWID_SOURCES)} OWID supplementary indicators...")
    for source in OWID_SOURCES:
        col = source["column"]
        log.info(f"  {source['label']}")
        raw = fetch_owid_first_available(source["urls"])
        if raw is None:
            log.warning(f"  ⚠ Could not fetch '{col}' — skipping.")
            continue
        norm = normalize_owid(raw)
        if norm is None or norm.empty:
            log.warning(f"  ⚠ No usable rows for '{col}' — skipping.")
            continue
        master = master.merge(norm.rename(columns={"value": col}), on=["iso3", "year"], how="left")
        log.info(f"  ✓ Merged '{col}': {master[col].notna().sum():,} values available.")

    # 3. Merge country metadata
    master = master.merge(countries, on="iso3", how="left")
    master = master[master["country"].notna() & (master["country"] != "")]

    # 4. Unit conversions for readability
    if "gdp_total_usd" in master.columns:
        master["gdp_total_bn"] = (master["gdp_total_usd"] / 1e9).round(3)
        master = master.drop(columns=["gdp_total_usd"])
    if "population" in master.columns:
        master["population_mn"] = (master["population"] / 1e6).round(3)
        master = master.drop(columns=["population"])

    # 5. Normalize sector breakdown to exactly 100%
    sects = ["agriculture_pct", "industry_pct", "services_pct"]
    if all(s in master.columns for s in sects):
        row_sum = master[sects].sum(axis=1, skipna=False)
        mask = (row_sum > 0) & (row_sum.notna())
        for s in sects:
            master.loc[mask, s] = (master.loc[mask, s] / row_sum.loc[mask] * 100).round(2)

    if failed:
        log.warning(f"\n{len(failed)} World Bank indicator(s) failed: {', '.join(failed)}")

    return master.sort_values(["country", "year"]).reset_index(drop=True)


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    total = len(INDICATORS) + len(OWID_SOURCES)
    log.info("=" * 65)
    log.info("World Bank API v2 + OWID — PESTEL Matrix Data Collection")
    log.info(f"Period: {START_YEAR}:{END_YEAR}  |  Target indicators: {total} "
             f"({len(INDICATORS)} World Bank + {len(OWID_SOURCES)} OWID)")
    log.info("=" * 65)

    countries = fetch_country_metadata()
    if countries.empty:
        log.error("Failed to retrieve country metadata. Aborting.")
        return
    log.info(f"  ✓ Country metadata retrieved: {len(countries)} countries")

    master = build_dataset(countries)

    out_dir = "data"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "world_economic.csv")
    master.to_csv(out_path, index=False)

    log.info("=" * 65)
    log.info(f" SUCCESS: Dataset saved to `{out_path}`")
    log.info(f" Final shape: {master.shape[0]:,} rows × {master.shape[1]} columns")
    log.info("=" * 65)


if __name__ == "__main__":
    main()