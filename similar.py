"""Similar countries: PCA + k-means on standardized structural indicators.
Exploratory by design: shows structural peers, not causal twins.
Designed to be embedded as a section in Country Profile."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from translations import t as tr

L = {
    "en": {
        "title": "Similar Countries (PCA + clustering)",
        "tip": "ℹ️ Exploratory view: countries are positioned by standardized structural indicators (log GDP/cap, growth, inflation, debt, trade, sector mix, human development). Proximity = structural similarity, not causal equivalence.",
        "target": "Reference country", "clusters": "Number of clusters",
        "scatter": "Structural map (PCA)", "similar": "Most structurally similar countries",
        "similarity": "Similarity", "pca1": "PCA axis 1", "pca2": "PCA axis 2",
        "cluster": "Cluster", "country": "Country", "gdp_cap": "GDP/cap",
        "life_exp": "Life expectancy",
    },
    "fr": {
        "title": "Pays similaires (PCA + clustering)",
        "tip": "ℹ️ Vue exploratoire : les pays sont positionnés selon des indicateurs structurels standardisés (log PIB/hab, croissance, inflation, dette, commerce, mix sectoriel, développement humain). Proximité = similarité structurelle, pas équivalence causale.",
        "target": "Pays de référence", "clusters": "Nombre de groupes",
        "scatter": "Carte structurelle (PCA)", "similar": "Pays structurellement les plus similaires",
        "similarity": "Similarité", "pca1": "Axe PCA 1", "pca2": "Axe PCA 2",
        "cluster": "Groupe", "country": "Pays", "gdp_cap": "PIB/hab",
        "life_exp": "Espérance de vie",
    },
}
FEATURES = ["gdp_per_capita", "gdp_growth_pct", "inflation", "debt_pct_gdp",
            "trade_openness_pct_gdp", "agriculture_pct", "industry_pct", "services_pct",
            "life_expectancy", "hdi", "internet_users_pct", "electricity_access_pct",
            "urban_population_pct", "unemployment_pct"]


def _t(lang, k):
    return L[lang][k]


def render(df_all, lang, default_country=None):
    st.divider()
    st.markdown(f'<div class="section-head"><span class="sh-num">03</span><span class="sh-title">{_t(lang, "title")}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="indicator-banner">{_t(lang, "tip")}</div>', unsafe_allow_html=True)

    year = int(df_all["year"].max())
    countries = sorted(df_all["country"].unique())
    default_idx = countries.index(default_country) if default_country in countries else 0
    c1, c2 = st.columns([2, 1])
    with c1:
        target = st.selectbox(_t(lang, "target"), countries, index=default_idx,
                              key="sim_target", format_func=lambda n: tr(n, lang))
    with c2:
        k = st.selectbox(_t(lang, "clusters"), [3, 4, 5, 6], index=1, key="sim_k")

    dfy = df_all[df_all["year"] == year].set_index("country")

    # Guard: if target has no data for latest_year, fall back to most recent available year
    if target not in dfy.index:
        available_years = sorted(df_all[df_all["country"] == target]["year"].unique(), reverse=True)
        fallback = next((y for y in available_years if y in df_all["year"].values), None)
        if fallback is None:
            st.warning(f"No data available for {target}.")
            return
        year = fallback
        dfy = df_all[df_all["year"] == year].set_index("country")
        if target not in dfy.index:
            st.warning(f"No data available for {target}.")
            return

    cols = [c for c in FEATURES if c in dfy.columns]
    X = dfy[cols].copy()
    if "gdp_per_capita" in X.columns:
        X["gdp_per_capita"] = np.log1p(X["gdp_per_capita"].clip(lower=0))
    X = X.fillna(X.median()).fillna(0)
    Z = StandardScaler().fit_transform(X.values)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(Z)
    labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(Z)

    dist = np.linalg.norm(Z - Z[dfy.index.get_loc(target)], axis=1)
    dmax = dist.max() or 1.0
    sim = 100.0 * (1.0 - dist / dmax)
    order = np.argsort(dist)
    top_idx = [i for i in order if dfy.index[i] != target][:8]

    fig = go.Figure()
    for cl in range(k):
        mask = labels == cl
        fig.add_trace(go.Scatter(x=coords[mask, 0], y=coords[mask, 1], mode="markers",
                                 name=f"{_t(lang, 'cluster')} {cl + 1}",
                                 marker=dict(size=9, opacity=.75),
                                 text=[tr(n, lang) for n in dfy.index[mask]],
                                 hovertemplate="<b>%{text}</b><extra></extra>"))
    ti = dfy.index.get_loc(target)
    fig.add_trace(go.Scatter(x=[coords[ti, 0]], y=[coords[ti, 1]], mode="markers+text",
                             name=tr(target, lang), text=[tr(target, lang)], textposition="top center",
                             marker=dict(size=16, symbol="star", color="#0067C0", line=dict(color="white", width=2)),
                             hovertemplate="<b>%{text}</b><extra></extra>"))
    fig.update_layout(xaxis_title=f"{_t(lang, 'pca1')} ({pca.explained_variance_ratio_[0]:.0%})",
                      yaxis_title=f"{_t(lang, 'pca2')} ({pca.explained_variance_ratio_[1]:.0%})",
                      height=460, margin=dict(t=30, b=20, l=10, r=10),
                      legend=dict(orientation="h", y=-.15))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**{_t(lang, 'similar')}**")
    rows = []
    for i in top_idx:
        gdp_val = dfy.iloc[i].get("gdp_per_capita", None)
        life_val = dfy.iloc[i].get("life_expectancy", None)
        rows.append({
            _t(lang, "country"): tr(dfy.index[i], lang),
            _t(lang, "similarity"): round(float(sim[i]), 1),
            _t(lang, "gdp_cap"): round(float(gdp_val), 0) if pd.notna(gdp_val) else "-",
            _t(lang, "life_exp"): round(float(life_val), 1) if pd.notna(life_val) else "-",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True)
