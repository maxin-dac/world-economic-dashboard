"""Analytical helpers: PESTEL scoring, investment score, red flags, CAGR.
Extracted from app.py so they can be unit-tested independently.
Emoji markers are built via chr() to keep this source ASCII-safe."""
import numpy as np
import streamlit as st
import pandas as pd
from translations import t
from core.constants import (
    PESTEL_PILLAR_ORDER, PESTEL_INDICATORS, INVERSE_INDICATORS,
)

RED = chr(0x1F534)
YELLOW = chr(0x1F7E1)
CHECK = chr(0x2705)

INVESTMENT_INDICATORS = {
    "fdi_pct_gdp": 0.15,
    "gdp_growth_pct": 0.15,
    "political_stability_index": 0.15,
    "regulatory_quality": 0.10,
    "control_of_corruption": 0.10,
    "inflation": 0.10,
    "gdp_total_bn": 0.10,
    "debt_pct_gdp": 0.05,
    "trade_openness_pct_gdp": 0.05,
    "reserves_months_imports": 0.05,
}
INVESTMENT_INVERSE = {"inflation", "debt_pct_gdp"}
INVESTMENT_LOG = {"gdp_total_bn"}
DEFAULT_MIN_POP_MN = 1.0


def previous_year(years: list, current: int) -> int:
    earlier = [y for y in years if y < current]
    return max(earlier) if earlier else current


def safe_delta(current, previous):
    if pd.notna(current) and pd.notna(previous):
        return float(current) - float(previous)
    return None


@st.cache_data(show_spinner=False)
def get_pestel_scores(df_target: pd.DataFrame, df_world: pd.DataFrame, year: int) -> dict:
    world_year = df_world[df_world["year"] == year]
    target_year = df_target[df_target["year"] == year]
    scores = {}
    for pillar in PESTEL_PILLAR_ORDER:
        norms = []
        for ind in PESTEL_INDICATORS[pillar]:
            if ind not in target_year.columns or ind not in world_year.columns:
                continue
            value = target_year[ind].median(skipna=True)
            w_min = world_year[ind].min(skipna=True)
            w_max = world_year[ind].max(skipna=True)
            if pd.isna(value) or pd.isna(w_min) or pd.isna(w_max) or w_max <= w_min:
                continue
            norm = (value - w_min) / (w_max - w_min)
            if ind in INVERSE_INDICATORS:
                norm = 1.0 - norm
            norms.append(float(np.clip(norm, 0.0, 1.0)))
        scores[pillar] = round(100.0 * np.mean(norms), 1) if norms else 0.0
    return scores


@st.cache_data(show_spinner=False)
def compute_investment_score(df_world: pd.DataFrame, year: int,
                             min_pop_mn: float = DEFAULT_MIN_POP_MN) -> pd.DataFrame:
    """Composite investment attractiveness score (0-100).

    Methodology (v2, realism-oriented):
    - Balances OPPORTUNITY (FDI inflows = revealed investor preference, growth,
      market size in log) and SAFETY (stability, regulation, corruption,
      inflation, debt).
    - Each indicator normalized by world PERCENTILE RANK (robust to outliers);
      50/100 = world median. Market size is ranked on log10(GDP).
    - Countries below min_pop_mn (default 1M) excluded by default.
    """
    df_year = df_world[df_world["year"] == year].copy()
    ranks = {}
    for ind in INVESTMENT_INDICATORS:
        if ind not in df_year.columns:
            continue
        s = df_year[ind]
        if ind in INVESTMENT_LOG:
            s = np.log10(s.where(s > 0))
        ranks[ind] = s.rank(pct=True)
    scores = []
    for idx, row in df_year.iterrows():
        norm_values = []
        available_weight = 0.0
        for ind, weight in INVESTMENT_INDICATORS.items():
            if ind not in row or pd.isna(row[ind]):
                continue
            norm = ranks[ind].loc[idx]
            if pd.isna(norm):
                continue
            if ind in INVESTMENT_INVERSE:
                norm = 1.0 - norm
            norm_values.append(norm * weight)
            available_weight += weight
        scores.append(sum(norm_values) / available_weight * 100 if available_weight else None)
    df_year["investment_score"] = scores
    if min_pop_mn and "population_mn" in df_year.columns:
        micro = df_year["population_mn"].fillna(0.0) < float(min_pop_mn)
        df_year.loc[micro, "investment_score"] = np.nan
    return df_year[["iso3", "country", "region", "income_group",
                    "investment_score"]].dropna(subset=["investment_score"])


@st.cache_data(show_spinner=False)
def detect_red_flags(df_world: pd.DataFrame, year: int, lang: str = "en") -> pd.DataFrame:
    """Countries with risk signals based on stress-calibrated thresholds."""
    df_year = df_world[df_world["year"] == year].copy()
    flags = []
    for _, row in df_year.iterrows():
        country_flags = []
        if pd.notna(row.get("inflation")) and row["inflation"] > 15:
            country_flags.append(f"{RED} {t('flag_high_inflation', lang)}")
        if pd.notna(row.get("debt_pct_gdp")) and row["debt_pct_gdp"] > 150:
            country_flags.append(f"{RED} {t('flag_high_debt', lang)}")
        if pd.notna(row.get("unemployment_pct")) and row["unemployment_pct"] > 20:
            country_flags.append(f"{RED} {t('flag_high_unemployment', lang)}")
        if pd.notna(row.get("political_stability_index")) and row["political_stability_index"] < -1.5:
            country_flags.append(f"{RED} {t('flag_political_instability', lang)}")
        if pd.notna(row.get("corruption_perception_index")) and row["corruption_perception_index"] < 25:
            country_flags.append(f"{RED} {t('flag_high_corruption', lang)}")
        if pd.notna(row.get("inflation")) and 8 < row["inflation"] <= 15:
            country_flags.append(f"{YELLOW} {t('flag_moderate_inflation', lang)}")
        if pd.notna(row.get("debt_pct_gdp")) and 80 < row["debt_pct_gdp"] <= 150:
            country_flags.append(f"{YELLOW} {t('flag_moderate_debt', lang)}")
        flags.append({
            "country": row["country"],
            "iso3": row["iso3"],
            "region": row["region"],
            "income_group": row["income_group"],
            "red_flags": len([f for f in country_flags if RED in f]),
            "yellow_flags": len([f for f in country_flags if YELLOW in f]),
            "total_flags": len(country_flags),
            "flag_details": " | ".join(country_flags) if country_flags
            else f"{CHECK} {t('flag_no_risk', lang)}",
        })
    return pd.DataFrame(flags)


@st.cache_data(show_spinner=False)
def compute_cagr(df_world: pd.DataFrame, country: str, indicator: str, years: list) -> float:
    """Compound Annual Growth Rate for a country/indicator over given years."""
    df_c = df_world[(df_world["country"] == country)
                    & (df_world["year"].isin(years))].sort_values("year")
    if len(df_c) < 2 or indicator not in df_c.columns:
        return None
    first, last = df_c[indicator].iloc[0], df_c[indicator].iloc[-1]
    if pd.isna(first) or pd.isna(last) or first <= 0 or last <= 0:
        return None
    n_years = df_c["year"].iloc[-1] - df_c["year"].iloc[0]
    if n_years <= 0:
        return None
    return (last / first) ** (1 / n_years) - 1
