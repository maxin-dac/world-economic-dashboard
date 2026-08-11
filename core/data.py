"""Data loading with parquet cache."""
import os
import pandas as pd
import streamlit as st
from core.constants import CORE_INDICATORS, INCOME_ORDER

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    csv_path = os.path.join("data", "world_economic.csv")
    cache_path = os.path.join("data", "world_economic.parquet")
    if not os.path.exists(csv_path):
        st.error(f"Dataset not found at `{csv_path}`. Please run `data/fetch_data.py` first.")
        st.stop()
    if os.path.exists(cache_path) and os.path.getmtime(cache_path) >= os.path.getmtime(csv_path):
        try:
            df = pd.read_parquet(cache_path)
        except Exception:
            df = pd.read_csv(csv_path)
    else:
        df = pd.read_csv(csv_path)
        try:
            df.to_parquet(cache_path, index=False)
        except Exception:
            pass
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    text_cols = ["iso3", "country", "region", "income_group", "capital"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None, " ": None})
    if "iso3" in df.columns:
        df["iso3"] = df["iso3"].str.upper()
    available = [c for c in CORE_INDICATORS if c in df.columns]
    meta_cols = ["iso3", "country", "region", "income_group", "latitude", "longitude"]
    keep = [c for c in meta_cols if c in df.columns] + ["year"] + available
    df = df[keep].copy()
    for col in available:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "income_group" in df.columns:
        df["income_group"] = pd.Categorical(df["income_group"], categories=INCOME_ORDER, ordered=True)
    return df
