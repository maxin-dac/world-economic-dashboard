import pandas as pd
import numpy as np
import pytest
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from core.investment import INVESTMENT_INDICATORS
from core.investment import (compute_investment_score,
    detect_red_flags, compute_cagr)
from core.investment import INVESTMENT_INVERSE
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "iso3": ["AAA", "BBB", "CCC"],
        "country": ["Alpha", "Beta", "Gamma"],
        "region": ["Europe", "Africa", "Asia"],
        "income_group": ["High income", "Low income", "Upper middle income"],
        "year": [2024, 2024, 2024],
        "gdp_growth_pct": [3.0, 7.0, 5.0],
        "political_stability_index": [1.0, -1.5, 0.5],
        "control_of_corruption": [1.5, -0.5, 0.8],
        "inflation": [2.0, 25.0, 8.0],
        "debt_pct_gdp": [40.0, 90.0, 65.0],
        "trade_openness_pct_gdp": [80.0, 30.0, 55.0],
        "electricity_access_pct": [100.0, 40.0, 85.0],
        "internet_users_pct": [90.0, 20.0, 70.0],
    })


class TestWeights:
    def test_sum_to_one(self):
        assert abs(sum(INVESTMENT_INDICATORS.values()) - 1.0) < 1e-9

    def test_inverse_set_subset(self):
        assert INVESTMENT_INVERSE <= set(INVESTMENT_INDICATORS.keys())


class TestInvestmentScore:
    def test_range(self, sample_df):
        result = compute_investment_score(sample_df, 2024)
        assert result["investment_score"].between(0, 100).all()

    def test_stable_country_outperforms(self, sample_df):
        result = compute_investment_score(sample_df, 2024)
        score = dict(zip(result["country"], result["investment_score"]))
        assert score["Alpha"] > score["Beta"]

    def test_nan_resilience(self, sample_df):
        sample_df.loc[0, "gdp_growth_pct"] = np.nan
        result = compute_investment_score(sample_df, 2024)
        assert result["investment_score"].notna().all()

    def test_missing_indicators_are_renormalized(self, sample_df):
        available = ["gdp_growth_pct"]
        reduced = sample_df[["iso3", "country", "region", "income_group", "year"] + available]
        result = compute_investment_score(reduced, 2024)
        scores = dict(zip(result["country"], result["investment_score"]))
        assert scores["Beta"] == 100.0

    def test_empty_year_returns_empty(self, sample_df):
        result = compute_investment_score(sample_df, 1999)
        assert result.empty


class TestRedFlags:
    def test_high_inflation_flagged(self, sample_df):
        flags = detect_red_flags(sample_df, 2024, "en")
        beta = flags[flags["country"] == "Beta"].iloc[0]
        assert beta["red_flags"] >= 1

    def test_clean_country_zero_red(self, sample_df):
        flags = detect_red_flags(sample_df, 2024, "en")
        alpha = flags[flags["country"] == "Alpha"].iloc[0]
        assert alpha["red_flags"] == 0

    def test_boundary_not_triggered(self, sample_df):
        sample_df.loc[0, "inflation"] = 10.0
        flags = detect_red_flags(sample_df, 2024, "en")
        alpha = flags[flags["country"] == "Alpha"].iloc[0]
        assert "High inflation" not in alpha["flag_details"]

    def test_bilingual_output(self, sample_df):
        en = detect_red_flags(sample_df, 2024, "en")
        fr = detect_red_flags(sample_df, 2024, "fr")
        en_detail = en[en["country"] == "Beta"].iloc[0]["flag_details"]
        fr_detail = fr[fr["country"] == "Beta"].iloc[0]["flag_details"]
        assert en_detail != fr_detail