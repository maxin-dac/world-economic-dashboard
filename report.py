"""Standalone per-country HTML report generator. No Streamlit dependency."""
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone

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

LABELS = {
    "en": {
        "gen_btn": "Ì≥Ñ Generate country report", "generating": "Building report‚Ä¶",
        "dl_btn": "‚¨áÔ∏è Download report (HTML)", "report_title": "Country Intelligence Report",
        "generated": "Generated on", "source": "Source: World Bank / Our World in Data",
        "kpi": "Key indicators", "indicator": "Indicator", "value": "Value", "world": "World median",
        "radar": "PESTEL profile", "trend": "GDP per capita vs inflation", "sector": "Sector structure",
        "trade": "Trade balance", "invest": "Investment attractiveness", "flags": "Risk signals",
        "noflag": "No major risk signal", "print": "Tip: open in a browser and use Print > Save as PDF.",
        "political": "Political", "economic": "Economic", "social": "Social",
        "technological": "Technological", "environmental": "Environmental", "legal": "Legal",
    },
    "fr": {
        "gen_btn": "Ì≥Ñ G√©n√©rer le rapport pays", "generating": "Construction du rapport‚Ä¶",
        "dl_btn": "‚¨áÔ∏è T√©l√©charger le rapport (HTML)", "report_title": "Rapport d'intelligence pays",
        "generated": "G√©n√©r√© le", "source": "Source : Banque Mondiale / Our World in Data",
        "kpi": "Indicateurs cl√©s", "indicator": "Indicateur", "value": "Valeur", "world": "M√©diane mondiale",
        "radar": "Profil PESTEL", "trend": "PIB/hab. vs inflation", "sector": "Structure sectorielle",
        "trade": "Balance commerciale", "invest": "Attractivit√© investissement", "flags": "Signaux de risque",
        "noflag": "Aucun signal de risque majeur", "print": "Astuce : ouvrez dans un navigateur puis Imprimer > Enregistrer en PDF.",
        "political": "Politique", "economic": "√âconomique", "social": "Social",
        "technological": "Technologique", "environmental": "Environnemental", "legal": "L√©gal",
    },
}

KPIS = [
    ("gdp_per_capita", "GDP per capita (USD)", "PIB/hab. (USD)", "${:,.0f}", False),
    ("gdp_growth_pct", "GDP growth (%)", "Croissance PIB (%)", "{:.1f}%", False),
    ("inflation", "Inflation (%)", "Inflation (%)", "{:.1f}%", True),
    ("unemployment_pct", "Unemployment (%)", "Ch√¥mage (%)", "{:.1f}%", True),
    ("hdi", "Human Development Index", "Indice d√©v. humain", "{:.3f}", False),
    ("life_expectancy", "Life expectancy (years)", "Esp√©rance de vie (ans)", "{:.1f}", False),
]


def ui_label(lang, key):
    return LABELS[lang][key]


def _latest_row(df_all, country):
    dc = df_all[df_all["country"] == country].sort_values("year")
    row = dc.dropna(subset=["gdp_per_capita"]).tail(1)
    if row.empty:
        row = dc.tail(1)
    return dc, row.iloc[0]


def _world(df_all, year):
    return df_all[df_all["year"] == year]


def _norm(value, series, inverse):
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


def pestel_scores(df_all, row):
    w = _world(df_all, int(row["year"]))
    out = {}
    for pillar, cols in PESTEL_REPORT.items():
        vals = [_norm(row[c], w[c], c in INVERSE_REPORT) for c in cols if c in w.columns and pd.notna(row.get(c))]
        vals = [v for v in vals if v is not None]
        out[pillar] = sum(vals) / len(vals) if vals else 0.0
    return out


def invest_score(df_all, row):
    w = _world(df_all, int(row["year"]))
    tot = 0.0
    for c, wt in INVEST_W.items():
        if c in w.columns and pd.notna(row.get(c)):
            v = _norm(row[c], w[c], c in INVEST_INV)
            if v is not None:
                tot += v * wt
    return tot * 100


def red_flags(row, lang):
    flags = []
    checks = [
        ("inflation", lambda v: v > 10, "ÔøΩÔøΩ", "High inflation", "Inflation √©lev√©e"),
        ("debt_pct_gdp", lambda v: v > 80, "Ì¥¥", "High debt", "Dette √©lev√©e"),
        ("unemployment_pct", lambda v: v > 15, "Ì¥¥", "High unemployment", "Ch√¥mage √©lev√©"),
        ("political_stability_index", lambda v: v < -1, "Ì¥¥", "Political instability", "Instabilit√© politique"),
        ("corruption_perception_index", lambda v: v < 25, "Ì¥¥", "High corruption", "Corruption √©lev√©e"),
    ]
    for col, test, emoji, en, fr in checks:
        v = row.get(col)
        if pd.notna(v) and test(v):
            flags.append(f"{emoji} {en if lang == 'en' else fr}")
    return flags


def _fig_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})


def build_country_report(df_all, country, lang):
    L = LABELS[lang]
    dc, row = _latest_row(df_all, country)
    year = int(row["year"])
    w = _world(df_all, year)

    kpi_rows = ""
    for key, en, fr, fmt, inverse in KPIS:
        if key not in w.columns:
            continue
        v, med = row.get(key), w[key].median()
        vs = ""
        if pd.notna(v) and pd.notna(med):
            better = (v >= med) != inverse
            vs = ("‚ñ≤" if better else "‚ñº")
        kpi_rows += f"<tr><td>{en if lang=='en' else fr}</td><td>{fmt.format(v) if pd.notna(v) else '‚Äî'}</td><td>{fmt.format(med) if pd.notna(med) else '‚Äî'}</td><td>{vs}</td></tr>"

    scores = pestel_scores(df_all, row)
    fig_radar = go.Figure(go.Scatterpolar(
        r=[scores[p] for p in PESTEL_REPORT], theta=[L[p] for p in PESTEL_REPORT],
        fill="toself", line=dict(color="#0067C0")))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=40, b=40), height=360, showlegend=False)

    fig_line = go.Figure()
    if len(dc) > 1 and "gdp_per_capita" in dc.columns and "inflation" in dc.columns:
        fig_line.add_trace(go.Scatter(x=dc["year"], y=dc["gdp_per_capita"], name="GDP/cap", line=dict(color="#0067C0")))
        fig_line.add_trace(go.Scatter(x=dc["year"], y=dc["inflation"], name="Inflation", yaxis="y2", line=dict(color="#dc2626")))
        fig_line.update_layout(yaxis=dict(title="GDP/cap"), yaxis2=dict(title="Inflation", overlaying="y", side="right"), height=320, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(orientation="h"))

    fig_donut = go.Figure()
    if all(c in row.index for c in ["agriculture_pct", "industry_pct", "services_pct"]):
        fig_donut.add_trace(go.Pie(labels=["Agriculture", "Industry", "Services"],
            values=[row["agriculture_pct"], row["industry_pct"], row["services_pct"]], hole=.5))
        fig_donut.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(orientation="h"))

    score = invest_score(df_all, row)
    flags = red_flags(row, lang)
    flag_html = "".join(f"<li>{f}</li>" for f in flags) or f"<li>‚úÖ {L['noflag']}</li>"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    css = ("body{font-family:Segoe UI,Arial,sans-serif;color:#0f172a;margin:32px}"
           "h1{color:#0B2540;border-bottom:3px solid #0067C0;padding-bottom:8px}"
           "h2{color:#0B2540;font-size:17px;margin-top:26px}"
           "table{border-collapse:collapse;width:100%}td,th{border:1px solid #cbd5e1;padding:6px 10px;font-size:13px}"
           "th{background:#0B2540;color:#fff;text-align:left}.meta{color:#475569;font-size:13px}"
           ".score{font-size:26px;font-weight:800;color:#0067C0}.grid{display:flex;gap:24px;flex-wrap:wrap}"
           "@media print{body{margin:10mm}}")

    html = f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">
<title>{country} ‚Äî {L['report_title']}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script><style>{css}</style></head><body>
<h1>Ìºç {country}</h1>
<p class="meta">{L['report_title']} ¬∑ {year} ¬∑ {L['generated']} {now} ¬∑ {L['source']}</p>
<h2>{L['kpi']}</h2>
<table><tr><th>{L['indicator']}</th><th>{L['value']}</th><th>{L['world']}</th><th></th></tr>{kpi_rows}</table>
<div class="grid"><div><h2>{L['radar']}</h2>{_fig_html(fig_radar)}</div>
<div><h2>{L['invest']}</h2><p class="score">{score:.1f}/100</p><h2>{L['flags']}</h2><ul>{flag_html}</ul></div></div>
<h2>{L['trend']}</h2>{_fig_html(fig_line)}
<div class="grid"><div><h2>{L['sector']}</h2>{_fig_html(fig_donut)}</div></div>
<p class="meta">{L['print']}</p></body></html>"""
    return html
