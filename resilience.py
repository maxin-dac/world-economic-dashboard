"""Resilience module: shock magnitude & recovery speed (2008 / 2020).
Self-contained: own labels + own math, rendered via Streamlit.
Real GDP/capita index compounded from annual real growth (price-base agnostic)."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from translations import t
from core.theme import style_plotly
from core.theme import render_table

L = {
    "en": {
        "title": "Resilience to Economic Shocks",
        "tip": "ℹ️ Real GDP per capita index (compounded from annual real growth). Drop = % change at the shock year. Recovery = years to return to the pre-shock peak.",
        "kpi_drop09": "Median drop (2009)", "kpi_drop20": "Median drop (2020)",
        "kpi_rec": "Recovered by 2024 (2020 shock)",
        "kpi_drop09_tip": "Median year-on-year change of the real GDP/capita index at the 2009 shock, across all countries. Closer to 0 (or positive) = milder average shock.",
        "kpi_drop20_tip": "Median year-on-year change of the real GDP/capita index at the 2020 shock, across all countries. Closer to 0 (or positive) = milder average shock.",
        "kpi_rec_tip": "Share of countries whose real GDP/capita index returned to or exceeded its 2019 peak by 2024.",
        "scatter": "Shock magnitude vs recovery speed (2020 shock)",
        "x": "GDP drop 2020 (%)", "y": "Years to recover",
        "rank": "Resilience ranking", "score": "Resilience score",
        "top": "Most resilient", "bottom": "Least resilient",
        "traj": "Country trajectory", "select": "Country",
        "not_rec": "not recovered by 2024", "country_col": "Country",
        "d09": "Drop 2009 (%)", "r09": "Recovery 2008 (yrs)",
        "d20": "Drop 2020 (%)", "r20": "Recovery 2019 (yrs)",
    },
    "fr": {
        "title": "Résilience aux chocs économiques",
        "tip": "ℹ️ Indice de PIB réel par habitant (composé depuis la croissance réelle annuelle). Chute = % de variation l'année du choc. Récupération = années pour revenir au pic d'avant-choc.",
        "kpi_drop09": "Chute médiane (2009)", "kpi_drop20": "Chute médiane (2020)",
        "kpi_rec": "Rétabli d'ici 2024 (choc 2020)",
        "kpi_drop09_tip": "Variation médiane (d'une année sur l'autre) de l'indice de PIB réel/hab. lors du choc 2009, tous pays confondus. Proche de 0 (ou positif) = choc moyen plus faible.",
        "kpi_drop20_tip": "Variation médiane (d'une année sur l'autre) de l'indice de PIB réel/hab. lors du choc 2020, tous pays confondus. Proche de 0 (ou positif) = choc moyen plus faible.",
        "kpi_rec_tip": "Part des pays dont l'indice de PIB réel/hab. est revenu au pic de 2019 (ou au-dessus) d'ici 2024.",
        "scatter": "Ampleur du choc vs vitesse de récupération (choc 2020)",
        "x": "Chute PIB 2020 (%)", "y": "Années pour récupérer",
        "rank": "Classement de résilience", "score": "Score de résilience",
        "top": "Les plus résilients", "bottom": "Les moins résilients",
        "traj": "Trajectoire du pays", "select": "Pays",
        "not_rec": "non rétabli en 2024", "country_col": "Pays",
        "d09": "Chute 2009 (%)", "r09": "Récup. 2008 (ans)",
        "d20": "Chute 2020 (%)", "r20": "Récup. 2019 (ans)",
    },
}
INCOME_COLORS = {"High income": "#059669", "Upper middle income": "#2563eb",
                 "Lower middle income": "#e8871e", "Low income": "#dc2626"}


def _t(lang, k):
    return L[lang][k]


def _real_index(series):
    idx = {}
    base = None
    for year, growth in series.items():
        if pd.isna(growth):
            continue
        base = 100.0 if base is None else base * (1 + growth / 100.0)
        idx[int(year)] = base
    return idx


def _shock(idx, peak):
    if peak not in idx or peak + 1 not in idx:
        return None, None
    p = idx[peak]
    drop = (idx[peak + 1] - p) / p * 100
    rec = next((y - peak for y in sorted(idx) if y > peak and idx[y] >= p), None)
    return drop, rec


@st.cache_data(show_spinner=False)


def compute_resilience(df_all):
    rows = []
    for country, group in df_all.groupby("country"):
        sub = group.set_index("year")["gdp_growth_pct"]
        idx = _real_index(sub.to_dict())
        d09, r09 = _shock(idx, 2008)
        d20, r20 = _shock(idx, 2019)
        meta = group.iloc[0]
        rows.append({"country": country, "iso3": meta.get("iso3"), "region": meta.get("region"),
                     "income_group": meta.get("income_group"),
                     "drop_2009": d09, "rec_2009": r09, "drop_2020": d20, "rec_2020": r20, "_idx": idx})
    df = pd.DataFrame(rows).dropna(subset=["drop_2020"])
    if df.empty:
        return df
    d = df["drop_2020"]
    sd = (d - d.min()) / (d.max() - d.min() + 1e-9)
    rec = df["rec_2020"].fillna(df["rec_2020"].max() + 1 if df["rec_2020"].notna().any() else 5)
    sr = 1 - (rec - rec.min()) / (rec.max() - rec.min() + 1e-9)
    df["score"] = (100 * (0.5 * sd + 0.5 * sr)).round(1)
    return df


TIER_RGB = {"high": (5, 150, 105), "mid": (217, 119, 6), "low": (220, 38, 38)}


def _tier(score):
    if pd.isna(score):
        return "mid"
    return "high" if score >= 60 else ("low" if score < 40 else "mid")


def _make_style(d, score_col):
    def row_css(row):
        r, g, b = TIER_RGB[_tier(row[score_col])]
        out = []
        for name in row.index:
            if name == score_col:
                out.append(f"background-color: rgba({r},{g},{b},0.20); font-weight: 700; color: rgb({r},{g},{b})")
            else:
                out.append(f"background-color: rgba({r},{g},{b},0.07)")
        return out
    return d.style.apply(row_css, axis=1)


def render(df_all, lang, theme_mode="dark"):
    st.divider()
    st.markdown(f'<div class="section-head"><span class="sh-num">05</span><span class="sh-title">{_t(lang, "title")}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="indicator-banner">{_t(lang, "tip")}</div>', unsafe_allow_html=True)

    df = compute_resilience(df_all)
    df["_cname"] = df["country"].map(lambda n: t(n, lang))
    if df.empty:
        st.info("-")
        return

    k1, k2, k3 = st.columns(3)
    k1.metric(_t(lang, "kpi_drop09"), f"{df['drop_2009'].median():.1f}%", help=_t(lang, "kpi_drop09_tip"))
    k2.metric(_t(lang, "kpi_drop20"), f"{df['drop_2020'].median():.1f}%", help=_t(lang, "kpi_drop20_tip"))
    k3.metric(_t(lang, "kpi_rec"), f"{df['rec_2020'].notna().mean() * 100:.0f}%", help=_t(lang, "kpi_rec_tip"))

    fig = go.Figure()
    for inc, grp in df.groupby("income_group"):
        fig.add_trace(go.Scatter(
            x=grp["drop_2020"], y=grp["rec_2020"].fillna(5), mode="markers", name=inc,
            marker=dict(size=10, color=INCOME_COLORS.get(inc, "#64748b"), opacity=.8),
            text=grp["_cname"],
            hovertemplate="<b>%{text}</b><br>" + _t(lang, "x") + ": %{x:.1f}%<br>" + _t(lang, "y") + ": %{y:.0f}<extra></extra>"))
    fig.update_layout(xaxis_title=_t(lang, "x"), yaxis_title=_t(lang, "y"), height=420,
                      margin=dict(t=40, b=20, l=10, r=10), legend=dict(orientation="h", y=-.15))
    fig.add_vline(x=df["drop_2020"].median(), line_dash="dash", line_color="#94a3b8")
    fig.add_hline(y=df["rec_2020"].median(), line_dash="dash", line_color="#94a3b8")
    st.plotly_chart(style_plotly(fig, theme_mode), width="stretch", theme="streamlit")

    st.markdown(f"**{_t(lang, 'rank')}**")
    cols = ["_cname", "drop_2009", "rec_2009", "drop_2020", "rec_2020", "score"]
    disp = df.sort_values("score", ascending=False)[cols].rename(columns={
        "_cname": _t(lang, "country_col"), "drop_2009": _t(lang, "d09"), "rec_2009": _t(lang, "r09"),
        "drop_2020": _t(lang, "d20"), "rec_2020": _t(lang, "r20"), "score": _t(lang, "score")})
    disp = disp.round(1)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{_t(lang, 'top')}**")
        render_table(_make_style(disp.head(10), _t(lang, "score")), theme_mode, hide_index=True)
    with c2:
        st.markdown(f"**{_t(lang, 'bottom')}**")
        render_table(_make_style(disp.tail(10), _t(lang, "score")), theme_mode, hide_index=True)

    st.markdown(f"**{_t(lang, 'traj')}**")
    sel = st.selectbox(_t(lang, "select"), sorted(df["country"].unique()), key="resil_ctry", format_func=lambda n: t(n, lang))
    idx = df[df["country"] == sel].iloc[0]["_idx"]
    ys = sorted(idx)
    fig2 = go.Figure(go.Scatter(x=ys, y=[idx[y] for y in ys], mode="lines+markers",
                                line=dict(color="#0067C0", width=2.2)))
    for peak, col in [(2008, "#dc2626"), (2019, "#e8871e")]:
        if peak in idx:
            fig2.add_vline(x=peak, line_width=1.5, line_color=col)
    fig2.update_layout(height=360, margin=dict(t=30, b=20, l=10, r=10), yaxis_title="Index (first year = 100)")
    st.plotly_chart(style_plotly(fig2, theme_mode), width="stretch", theme="streamlit")
