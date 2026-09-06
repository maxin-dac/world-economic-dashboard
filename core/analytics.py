"""Analytical helpers: PESTEL scoring only.
Extracted from app.py so they can be unit-tested independently."""
import numpy as np
import streamlit as st
import pandas as pd
from core.constants import (
    PESTEL_PILLAR_ORDER, PESTEL_INDICATORS, INVERSE_INDICATORS,
)


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
