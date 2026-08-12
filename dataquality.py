"""Data Quality module: coverage, freshness, anomalies, null trends.
Self-contained labels, no emoji (encoding-safe)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from translations import t as tr

META = {"iso3", "country", "region", "income_group", "capital", "latitude",
        "longitude", "year", "gdp_total_bn", "population_mn"}

L = {
    "en": {
        "title": "Data Quality & Coverage",
        "tip": "ℹ️ Transparency layer: how complete and fresh the dataset is, and which values are statistical anomalies.",
        "kpi_cov": "Overall coverage", "kpi_full": "Indicators >=95% complete",
        "kpi_lag": "Indicators lagging >=2 yrs", "kpi_anom": "Anomalies (|z| > 4)",
        "cov_title": "Coverage per indicator (2000-2024)",
        "fresh_title": "Freshness: indicators not at the latest year",
        "fresh_ok": "All indicators are up to date.",
        "anom_title": "Statistical anomalies (robust z-score > 4, latest year)",
        "anom_none": "No anomaly detected for the latest year.",
        "null_title": "Null rate per year (all indicators)",
        "country": "Country", "indicator": "Indicator", "value": "Value", "z": "Robust z-score",
        "coverage": "Coverage (%)", "latest": "Latest year",
    },
    "fr": {
        "title": "Qualité & couverture des données",
        "tip": "ℹ️ Couche de transparence : complétude et fraîcheur du jeu de données, et valeurs statistiquement anormales.",
        "kpi_cov": "Couverture globale", "kpi_full": "Indicateurs complets >=95%",
        "kpi_lag": "Indicateurs en retard >=2 ans", "kpi_anom": "Anomalies (|z| > 4)",
        "cov_title": "Couverture par indicateur (2000-2024)",
        "fresh_title": "Fraîcheur : indicateurs non à jour",
        "fresh_ok": "Tous les indicateurs sont à jour.",
        "anom_title": "Anomalies statistiques (z-score robuste > 4, dernière année)",
        "anom_none": "Aucune anomalie détectée pour la dernière année.",
        "null_title": "Taux de nulls par année (tous indicateurs)",
        "country": "Pays", "indicator": "Indicateur", "value": "Valeur", "z": "Z-score robuste",
        "coverage": "Couverture (%)", "latest": "Dernière année",
    },
}


def _inds(df):
    return [c for c in df.columns if c not in META and pd.api.types.is_numeric_dtype(df[c])]


def _robust_z(s):
    med = s.median()
    mad = (s - med).abs().median()
    if mad == 0 or pd.isna(mad):
        return pd.Series(0.0, index=s.index)
    return (s - med) / (1.4826 * mad)


def render(df_all, lang):
    t = lambda k: L[lang][k]
    st.divider()
    st.markdown(f'<div class="section-head"><span class="sh-num">02</span><span class="sh-title">{t("title")}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="indicator-banner">{t("tip")}</div>', unsafe_allow_html=True)

    inds = _inds(df_all)
    latest = int(df_all["year"].max())
    cov = (df_all[inds].notna().mean() * 100).sort_values(ascending=False)
    fresh = pd.Series({c: int(df_all[df_all[c].notna()]["year"].max()) for c in inds})
    lag = latest - fresh

    dl = df_all[df_all["year"] == latest]
    rows = []
    for c in [x for x in inds if x not in ("exchange_rate", "cpi_index_raw")]:
        z = _robust_z(dl[c].dropna())
        for i in z[z.abs() > 4].index:
            rows.append({"country": tr(dl.loc[i, "country"], lang), "indicator": c,
                         "value": round(float(dl.loc[i, c]), 2), "z": round(float(z.loc[i]), 1)})
    anom = pd.DataFrame(rows)


    st.markdown(f"**{t('cov_title')}**")
    fig = go.Figure(go.Bar(x=cov.values, y=cov.index, orientation="h",
                           marker_color=["#059669" if v >= 90 else "#d97706" if v >= 70 else "#dc2626" for v in cov.values]))
    fig.update_layout(xaxis_range=[0, 100], xaxis_title=t("coverage"), yaxis=dict(autorange="reversed"),
                      height=max(500, len(cov) * 16), margin=dict(t=20, b=20, l=10, r=10))
    fig.update_yaxes(tickfont=dict(size=9))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**{t('null_title')}**")
    yearly = df_all[inds].isna().groupby(df_all["year"]).mean().mean(axis=1) * 100
    fig2 = go.Figure(go.Scatter(x=yearly.index, y=yearly.values, mode="lines+markers", line=dict(color="#0067C0", width=2.2)))
    fig2.update_layout(yaxis_title="%", height=320, margin=dict(t=30, b=20, l=10, r=10))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"**{t('fresh_title')}**")
    old = fresh[fresh < latest].sort_values()
    if old.empty:
        st.success(t("fresh_ok"))
    else:
        fd = old.reset_index()
        fd.columns = [t("indicator"), t("latest")]
        st.dataframe(fd, hide_index=True)

    st.markdown(f"**{t('anom_title')}**")
    if anom.empty:
        st.info(t("anom_none"))
    else:
        ad = anom.sort_values("z", key=abs, ascending=False).head(30)
        ad = ad.rename(columns={"country": t("country"), "indicator": t("indicator"),
                                "value": t("value"), "z": t("z")})
        st.dataframe(ad, hide_index=True)
