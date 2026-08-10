"""Pure computation layer. No plotting, no PDF, no prose.
Shared by report.py and narrative.py."""
import pandas as pd

PESTEL_REPORT = {
    "political": ["govt_effectiveness_index", "political_stability_index", "military_expenditure_pct_gdp"],
    "economic": ["gdp_per_capita", "gdp_growth_pct", "inflation", "debt_pct_gdp", "trade_openness_pct_gdp"],
    "social": ["life_expectancy", "hdi", "unemployment_pct", "literacy_rate"],
    "technological": ["internet_users_pct", "mobile_subscriptions_per_100", "rd_expenditure_pct_gdp"],
    "environmental": ["electricity_access_pct", "pm25_air_pollution", "cereal_yield_kg_per_ha"],
    "legal": ["control_of_corruption", "rule_of_law_index", "regulatory_quality", "corruption_perception_index"],
}
INVERSE_REPORT = {"inflation", "debt_pct_gdp", "unemployment_pct", "pm25_air_pollution"}
INVEST_W = {
    "gdp_growth_pct": .20, "political_stability_index": .20, "control_of_corruption": .15,
    "inflation": .15, "debt_pct_gdp": .10, "trade_openness_pct_gdp": .10,
    "electricity_access_pct": .05, "internet_users_pct": .05,
}
INVEST_INV = {"inflation", "debt_pct_gdp"}
KPIS = [
    ("gdp_per_capita", "GDP per capita (USD)", "PIB/hab. (USD)", "${:,.0f}", False),
    ("gdp_growth_pct", "GDP growth (%)", "Croissance PIB (%)", "{:.1f}%", False),
    ("inflation", "Inflation (%)", "Inflation (%)", "{:.1f}%", True),
    ("unemployment_pct", "Unemployment (%)", "Chômage (%)", "{:.1f}%", True),
    ("hdi", "Human Development Index", "Indice dév. humain", "{:.3f}", False),
    ("life_expectancy", "Life expectancy (years)", "Espérance de vie (ans)", "{:.1f}", False),
]


def latest_row(df_all, country):
    dc = df_all[df_all["country"] == country].sort_values("year")
    row = dc.dropna(subset=["gdp_per_capita"]).tail(1)
    if row.empty:
        row = dc.tail(1)
    return dc, row.iloc[0]


def world(df_all, year):
    return df_all[df_all["year"] == year]


def norm(value, series, inverse):
    s = series.dropna()
    if s.empty or value is None or pd.isna(value):
        return None
    lo, hi = s.min(), s.max()
    if hi <= lo:
        return 50.0
    n = (value - lo) / (hi - lo)
    if inverse:
        n = 1 - n
    return n * 100


def pillar_scores(df_all, year, get):
    w = world(df_all, year)
    out = {}
    for pillar, cols in PESTEL_REPORT.items():
        vals = []
        for c in cols:
            v = get(c)
            if c in w.columns and v is not None and pd.notna(v):
                n = norm(v, w[c], c in INVERSE_REPORT)
                if n is not None:
                    vals.append(n)
        out[pillar] = sum(vals) / len(vals) if vals else 0.0
    return out


def invest_score(df_all, row):
    w = world(df_all, int(row["year"]))
    tot = 0.0
    for c, wt in INVEST_W.items():
        if c in w.columns and pd.notna(row.get(c)):
            v = norm(row[c], w[c], c in INVEST_INV)
            if v is not None:
                tot += v * wt
    return tot * 100


def score_percentile(df_all, row):
    w = world(df_all, int(row["year"]))
    score = invest_score(df_all, row)
    all_scores = [invest_score(df_all, r) for _, r in w.iterrows()]
    all_scores = [s for s in all_scores if not pd.isna(s)]
    if not all_scores:
        return 50
    return int((sum(1 for s in all_scores if s <= score) / len(all_scores)) * 100)


def red_flags(row):
    flags = []
    checks = [
        ("inflation", lambda v: v > 10),
        ("debt", lambda v: row.get("debt_pct_gdp") is not None and pd.notna(row.get("debt_pct_gdp")) and row.get("debt_pct_gdp") > 80),
        ("unemployment", lambda v: row.get("unemployment_pct") is not None and pd.notna(row.get("unemployment_pct")) and row.get("unemployment_pct") > 15),
        ("stability", lambda v: row.get("political_stability_index") is not None and pd.notna(row.get("political_stability_index")) and row.get("political_stability_index") < -1),
        ("corruption", lambda v: row.get("corruption_perception_index") is not None and pd.notna(row.get("corruption_perception_index")) and row.get("corruption_perception_index") < 25),
    ]
    if pd.notna(row.get("inflation")) and row["inflation"] > 10:
        flags.append("inflation")
    if pd.notna(row.get("debt_pct_gdp")) and row["debt_pct_gdp"] > 80:
        flags.append("debt")
    if pd.notna(row.get("unemployment_pct")) and row["unemployment_pct"] > 15:
        flags.append("unemployment")
    if pd.notna(row.get("political_stability_index")) and row["political_stability_index"] < -1:
        flags.append("stability")
    if pd.notna(row.get("corruption_perception_index")) and row["corruption_perception_index"] < 25:
        flags.append("corruption")
    return flags


def build_facts(df_all, country):
    dc, row = latest_row(df_all, country)
    year = int(row["year"])
    w = world(df_all, year)
    pillars = pillar_scores(df_all, year, lambda c: row.get(c))
    strongest = max(pillars.items(), key=lambda x: x[1])
    weakest = min(pillars.items(), key=lambda x: x[1])
    kpis = []
    for key, en, fr, fmt, inverse in KPIS:
        if key not in w.columns:
            continue
        v, med = row.get(key), w[key].median()
        if pd.notna(v) and pd.notna(med):
            kpis.append({"key": key, "value": round(float(v), 2), "world_median": round(float(med), 2),
                         "better": bool((v >= med) != inverse)})
    return {
        "country": country, "year": year,
        "score": round(invest_score(df_all, row), 1),
        "percentile": score_percentile(df_all, row),
        "pillars": {k: round(v, 1) for k, v in pillars.items()},
        "strongest": strongest[0], "strongest_score": round(strongest[1], 1),
        "weakest": weakest[0], "weakest_score": round(weakest[1], 1),
        "flags": red_flags(row),
        "kpis": kpis,
    }
