"""Per-country PDF report mirroring the app's Country Profile visuals.
Seaborn-styled, base font 11, titles 15. Self-contained (no fragile imports)."""
import os
import json
import tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime, timezone

sns.set_theme(style="whitegrid", rc={
    "font.size": 11, "axes.titlesize": 15, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10,
    "axes.titleweight": "bold",
})
sns.set_palette(sns.color_palette(["#0067C0", "#e8871e", "#059669", "#7c3aed", "#dc2626"]))

NAVY = (11, 37, 64); BLUE = (0, 103, 192); RED = (220, 38, 38); GREEN = (5, 150, 105); GRAY = (100, 116, 139)
C_SERVICES, C_INDUSTRY, C_AGRI = "#e8871e", "#2563eb", "#059669"
WORLD_GEO_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"

PESTEL_REPORT = {
    "political": ["govt_effectiveness_index", "political_stability_index", "military_expenditure_pct_gdp"],
    "economic": ["gdp_per_capita", "gdp_growth_pct", "inflation", "debt_pct_gdp", "trade_openness_pct_gdp"],
    "social": ["life_expectancy", "hdi", "unemployment_pct", "literacy_rate"],
    "technological": ["internet_users_pct", "mobile_subscriptions_per_100", "rd_expenditure_pct_gdp"],
    "environmental": ["electricity_access_pct", "pm25_air_pollution", "cereal_yield_kg_per_ha"],
    "legal": ["control_of_corruption", "rule_of_law_index", "regulatory_quality", "corruption_perception_index"],
}
INVERSE_REPORT = {"inflation", "debt_pct_gdp", "unemployment_pct", "pm25_air_pollution"}
INVEST_W = {"gdp_growth_pct": .20, "political_stability_index": .20, "control_of_corruption": .15,
            "inflation": .15, "debt_pct_gdp": .10, "trade_openness_pct_gdp": .10,
            "electricity_access_pct": .05, "internet_users_pct": .05}
INVEST_INV = {"inflation", "debt_pct_gdp"}
HEAT_COLS = ["gdp_per_capita", "inflation", "debt_pct_gdp", "unemployment_pct",
             "life_expectancy", "electricity_access_pct", "internet_users_pct", "pm25_air_pollution"]
GAUGES = [("unemployment_pct", 30, "Unemployment", "#dc2626"), ("gdp_growth_pct", 10, "GDP growth", "#0067C0"),
          ("primary_completion_rate_pct", 100, "Primary completion", "#2563eb"), ("life_expectancy", 90, "Life expectancy", "#059669"),
          ("internet_users_pct", 100, "Internet users", "#7c3aed"), ("electricity_access_pct", 100, "Electricity access", "#e8871e")]

LABELS = {
    "en": {"gen_btn": "Generate country report (PDF)", "generating": "Building PDF...", "dl_btn": "Download report (PDF)",
           "report_title": "Country Intelligence Report", "generated": "Generated on", "source": "Source: World Bank / Our World in Data",
           "exec_summary": "Executive Summary", "location": "Geographic location", "sector": "Sector breakdown",
           "radar": "PESTEL performance radar", "waterfall": "Trade balance waterfall", "evol": "Sector evolution (100% stacked)",
           "heat": "Indicator trends (last 10 years)", "gdp": "GDP per capita & inflation", "kpi": "Key metrics",
           "invest": "Investment score", "flags": "Risk signals", "noflag": "No major risk signal", "conclusion": "Conclusion & recommendation",
           "world": "World median", "indicator": "Indicator", "value": "Value", "vs": "vs world", "above": "above", "below": "below",
           "ai_note": "Narrative generated from computed indicators (LLM-enhanced when available).",
           "political": "Political", "economic": "Economic", "social": "Social", "technological": "Technological",
           "environmental": "Environmental", "legal": "Legal & Governance"},
    "fr": {"gen_btn": "Générer le rapport pays (PDF)", "generating": "Construction du PDF...", "dl_btn": "Télécharger le rapport (PDF)",
           "report_title": "Rapport d'intelligence pays", "generated": "Généré le", "source": "Source : Banque Mondiale / Our World in Data",
           "exec_summary": "Synthèse exécutive", "location": "Localisation géographique", "sector": "Composition sectorielle",
           "radar": "Radar de performance PESTEL", "waterfall": "Cascade balance commerciale", "evol": "Évolution sectorielle (100% empilé)",
           "heat": "Tendances des indicateurs (10 ans)", "gdp": "PIB/hab. & inflation", "kpi": "Indicateurs clés",
           "invest": "Score d'investissement", "flags": "Signaux de risque", "noflag": "Aucun signal de risque majeur", "conclusion": "Conclusion & recommandation",
           "world": "Médiane mondiale", "indicator": "Indicateur", "value": "Valeur", "vs": "vs médiane", "above": "au-dessus", "below": "en-dessous",
           "ai_note": "Narratif généré à partir des indicateurs calculés (enrichi par LLM si disponible).",
           "political": "Politique", "economic": "Économique", "social": "Social", "technological": "Technologique",
           "environmental": "Environnemental", "legal": "Légal & Gouvernance"},
}
FLAG_LBL = {"en": {"inflation": "High inflation", "debt": "High debt", "unemployment": "High unemployment",
                   "stability": "Political instability", "corruption": "Weak corruption control"},
            "fr": {"inflation": "Inflation élevée", "debt": "Dette élevée", "unemployment": "Chômage élevé",
                   "stability": "Instabilité politique", "corruption": "Corruption élevée"}}


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


def _norm(v, s, inv):
    s = s.dropna()
    if s.empty or v is None or pd.isna(v):
        return None
    lo, hi = s.min(), s.max()
    if hi <= lo:
        return 50.0
    n = (v - lo) / (hi - lo)
    return (1 - n) * 100 if inv else n * 100


def _pillar_scores(df_all, year, get):
    w = _world(df_all, year)
    out = {}
    for p, cols in PESTEL_REPORT.items():
        vals = [n for c in cols if c in w.columns and pd.notna(get(c)) for n in [_norm(get(c), w[c], c in INVERSE_REPORT)] if n is not None]
        out[p] = sum(vals) / len(vals) if vals else 0.0
    return out


def _invest_score(df_all, row):
    w = _world(df_all, int(row["year"]))
    tot = 0.0
    for c, wt in INVEST_W.items():
        if c in w.columns and pd.notna(row.get(c)):
            n = _norm(row[c], w[c], c in INVEST_INV)
            if n is not None:
                tot += n * wt
    return tot * 100


def _red_flags(row):
    f = []
    if pd.notna(row.get("inflation")) and row["inflation"] > 10: f.append("inflation")
    if pd.notna(row.get("debt_pct_gdp")) and row["debt_pct_gdp"] > 80: f.append("debt")
    if pd.notna(row.get("unemployment_pct")) and row["unemployment_pct"] > 15: f.append("unemployment")
    if pd.notna(row.get("political_stability_index")) and row["political_stability_index"] < -1: f.append("stability")
    if pd.notna(row.get("corruption_perception_index")) and row["corruption_perception_index"] < 25: f.append("corruption")
    return f


def _narrative(facts, lang):
    P = LABELS[lang]; F = FLAG_LBL[lang]
    c, s, pc = facts["country"], facts["score"], facts["percentile"]
    pos = f"top {pc}%" if pc >= 50 else f"bottom {100 - pc}%"
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        try:
            import requests
            prompt = (f"Senior macro-economic analyst. Write a concise 3-paragraph executive summary in "
                      f"{'French' if lang == 'fr' else 'English'} for {c} ({facts['year']}). Use ONLY provided data. "
                      f"P1 positioning (score {s}/100, {pos}, strength {facts['strongest']}, weakness {facts['weakest']}). "
                      f"P2 risk/stability. P3 investment recommendation. DATA: {json.dumps(facts)}")
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Authorization": f"Bearer {key}"},
                              json={"model": "llama-3.1-8b-instant", "temperature": 0, "max_tokens": 600,
                                    "messages": [{"role": "user", "content": prompt}]}, timeout=20)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip().encode("latin-1", "replace").decode("latin-1")
        except Exception:
            pass
    if lang == "fr":
        l1 = f"{c} obtient {s}/100 ({pos} mondial). Atout principal : {P[facts['strongest']]} ({facts['strongest_score']}/100) ; faiblesse : {P[facts['weakest']]} ({facts['weakest_score']}/100)."
        l2 = "Aucun signal critique ; profil stable." if not facts["flags"] else f"{len(facts['flags'])} signal(s) à surveiller : " + ", ".join(F[x] for x in facts["flags"]) + "."
        l3 = "Recommandation : candidat solide." if s >= 70 and not facts["flags"] else "Recommandation : prudence, surveiller les risques." if s >= 50 and len(facts["flags"]) <= 1 else "Recommandation : profil à haut risque, due diligence approfondie."
    else:
        l1 = f"{c} scores {s}/100 ({pos} globally). Main strength: {P[facts['strongest']]} ({facts['strongest_score']}/100); weakness: {P[facts['weakest']]} ({facts['weakest_score']}/100)."
        l2 = "No critical signal; stable profile." if not facts["flags"] else f"{len(facts['flags'])} signal(s) to monitor: " + ", ".join(F[x] for x in facts["flags"]) + "."
        l3 = "Recommendation: strong candidate." if s >= 70 and not facts["flags"] else "Recommendation: proceed with caution." if s >= 50 and len(facts["flags"]) <= 1 else "Recommendation: high-risk, extensive due diligence."
    return f"{l1} {l2} {l3}"


_geo = {}
def _world_geo():
    if "g" not in _geo:
        try:
            import requests
            r = requests.get(WORLD_GEO_URL, timeout=20); r.raise_for_status()
            _geo["g"] = r.json()
        except Exception:
            _geo["g"] = None
    return _geo["g"]


def _png(fig, paths):
    buf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    fig.savefig(buf.name, dpi=300, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)
    paths.append(buf.name)
    return buf.name


def _fig_identity(df_all, row, iso3, L, paths):
    fig, (axm, axd) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1.4, 1]})
    geo = _world_geo()
    axm.set_axis_off(); axm.set_facecolor("#dbe9f6")
    if geo:
        for f in geo["features"]:
            hl = f.get("id") == iso3
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                xs = [p[0] for p in poly[0]]; ys = [p[1] for p in poly[0]]
                axm.fill(xs, ys, color="#e8542f" if hl else "#cfd6dd", ec="white", lw=.3, zorder=3 if hl else 1)
        axm.set_xlim(-180, 180); axm.set_ylim(-60, 85)
    axm.set_title(f"{L['location']} - {row['country']}", fontsize=15, weight="bold", color="#0B2540")
    vals = [row.get("agriculture_pct", 0), row.get("industry_pct", 0), row.get("services_pct", 0)]
    w_, t_, a_ = axd.pie(vals, labels=["Agriculture", "Industry", "Services"], autopct="%1.0f%%",
                         colors=[C_AGRI, C_INDUSTRY, C_SERVICES], wedgeprops={"width": .42, "edgecolor": "white", "linewidth": 2},
                         textprops={"fontsize": 10, "weight": "bold"})
    for x in a_: x.set_color("white")
    axd.set_title(f"{L['sector']} ({int(row['year'])})", fontsize=15, weight="bold", color="#0B2540")
    fig.tight_layout()
    return _png(fig, paths)


def _fig_gdp(dc, L, paths):
    fig, ax1 = plt.subplots(figsize=(10, 3.4))
    ax1.plot(dc["year"], dc["gdp_per_capita"], color="#0067C0", lw=2.2, label="GDP per capita (USD)")
    ax1.set_ylabel("GDP per capita (USD)", color="#0067C0")
    ax2 = ax1.twinx()
    ax2.plot(dc["year"], dc["inflation"], color="#e8871e", lw=1.8, ls="--", label="Inflation (%)")
    ax2.set_ylabel("Inflation (%)", color="#e8871e")
    ax1.set_title(L["gdp"], fontsize=15, weight="bold", color="#0B2540")
    h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(.5, -.14), ncol=2, frameon=False)
    fig.tight_layout()
    return _png(fig, paths)


def _fig_pestel(df_all, row, L, paths):
    w = _world(df_all, int(row["year"]))
    sc = _pillar_scores(df_all, int(row["year"]), lambda c: row.get(c))
    sw = _pillar_scores(df_all, int(row["year"]), lambda c: w[c].median() if c in w.columns else None)
    fig = plt.figure(figsize=(10, 4.4))
    axr = fig.add_subplot(121, polar=True)
    cats = [L[p] for p in PESTEL_REPORT]
    vc = [sc[p] for p in PESTEL_REPORT]; vw = [sw[p] for p in PESTEL_REPORT]
    ang = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    vc += vc[:1]; vw += vw[:1]; ang += ang[:1]
    axr.plot(ang, vc, color="#0067C0", lw=2.2, label=row["country"])
    axr.fill(ang, vc, color="#0067C0", alpha=.18)
    axr.plot(ang, vw, color="#059669", lw=1.8, ls="--", label=L["world"])
    axr.set_xticks(ang[:-1]); axr.set_xticklabels(cats, fontsize=9)
    axr.set_ylim(0, 100); axr.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
    axr.set_title(L["radar"], fontsize=15, weight="bold", color="#0B2540", pad=18)
    axw = fig.add_subplot(122)
    vals = [row.get("exports_pct_gdp", 0), -row.get("imports_pct_gdp", 0), row.get("current_account_pct_gdp", 0)]
    labs = ["Exports", "Imports", "Current account"]
    cols = [C_AGRI, "#ef4444", "#2563eb"]
    axw.bar(labs, vals, color=cols, edgecolor="white", linewidth=1.5)
    axw.axhline(0, color="#64748b", lw=.8)
    for i, v in enumerate(vals):
        axw.text(i, v + (0.4 if v >= 0 else -0.8), f"{v:.1f}%", ha="center", fontsize=10, weight="bold")
    axw.set_ylabel("% of GDP")
    axw.set_title(L["waterfall"], fontsize=15, weight="bold", color="#0B2540")
    sns.despine(ax=axw)
    fig.tight_layout()
    return _png(fig, paths)


def _fig_evol_heat(dc, L, paths):
    out = []
    if all(c in dc.columns for c in ["agriculture_pct", "industry_pct", "services_pct"]):
        fig, ax = plt.subplots(figsize=(10, 3.2))
        ax.stackplot(dc["year"], dc["agriculture_pct"], dc["industry_pct"], dc["services_pct"],
                     labels=["Agriculture", "Industry", "Services"], colors=[C_AGRI, C_INDUSTRY, C_SERVICES], alpha=.85)
        ax.set_ylim(0, 100); ax.set_ylabel("Share of GDP (%)")
        ax.set_title(L["evol"], fontsize=15, weight="bold", color="#0B2540")
        ax.legend(loc="upper center", bbox_to_anchor=(.5, -.16), ncol=3, frameon=False)
        sns.despine()
        fig.tight_layout()
        out.append(_png(fig, paths))
    hm = dc[dc["year"] >= dc["year"].max() - 9]
    cols = [c for c in HEAT_COLS if c in hm.columns]
    if cols and len(hm) > 1:
        mat = hm.set_index("year")[cols].T
        mat = (mat - mat.min(axis=1)) / (mat.max(axis=1) - mat.min(axis=1) + 1e-9)
        fig, ax = plt.subplots(figsize=(10, 3.6))
        sns.heatmap(mat, cmap="RdBu_r", cbar_kws={"label": "Normalized score", "shrink": .8}, ax=ax, linewidths=.4, linecolor="white")
        ax.set_title(L["heat"], fontsize=15, weight="bold", color="#0B2540")
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
        fig.tight_layout()
        out.append(_png(fig, paths))
    return out


def _fig_gauges(row, paths):
    fig, axes = plt.subplots(2, 3, figsize=(10, 3.6))
    for ax, (col, vmax, label, color) in zip(axes.flat, GAUGES):
        ax.set_axis_off()
        v = row.get(col)
        th = np.linspace(np.pi, 0, 100)
        ax.plot(np.cos(th), np.sin(th), color="#e2e8f0", lw=7, solid_capstyle="round")
        if pd.notna(v):
            fr = max(0, min(1, v / vmax))
            t2 = np.linspace(np.pi, np.pi - fr * np.pi, 100)
            ax.plot(np.cos(t2), np.sin(t2), color=color, lw=7, solid_capstyle="round")
            ax.text(0, .18, f"{v:.1f}", ha="center", fontsize=13, weight="bold")
        ax.text(0, -.28, label, ha="center", fontsize=10)
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-.45, 1.2)
    fig.tight_layout()
    return _png(fig, paths)


class _PDF(FPDF):
    def __init__(self, footer_text):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.footer_text = footer_text
        self.alias_nb_pages()

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 8, self.footer_text, align="L")
        self.cell(0, 8, f"{self.page_no()}/{{nb}}", align="R")


def build_country_report(df_all, country, lang):
    L = LABELS[lang]
    dc, row = an_iso = (None, None)
    dc, row = _latest_row(df_all, country)
    iso3 = row.get("iso3", "")
    year = int(row["year"])
    w = _world(df_all, year)
    paths = []
    score = _invest_score(df_all, row)
    pillars = _pillar_scores(df_all, year, lambda c: row.get(c))
    flags = _red_flags(row)
    facts = {"country": country, "year": year, "score": round(score, 1),
             "percentile": int((sum(1 for _, r in w.iterrows() if _invest_score(df_all, r) <= score) / max(1, len(w))) * 100),
             "strongest": max(pillars, key=pillars.get), "strongest_score": round(max(pillars.values()), 1),
             "weakest": min(pillars, key=pillars.get), "weakest_score": round(min(pillars.values()), 1),
             "flags": flags}

    pdf = _PDF(f"{L['report_title']} - {L['source']}")
    pdf.set_margins(15, 15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 24); pdf.set_text_color(*NAVY); pdf.cell(0, 12, country); pdf.ln(12)
    pdf.set_font("Helvetica", "B", 15); pdf.set_text_color(*BLUE); pdf.cell(0, 8, L["report_title"]); pdf.ln(8)
    pdf.set_font("Helvetica", "", 11); pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, f"{year} - {L['generated']} {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"); pdf.ln(9)
    pdf.set_draw_color(*BLUE); pdf.set_line_width(.8); pdf.line(15, pdf.get_y(), 195, pdf.get_y()); pdf.ln(6)

    pdf.set_font("Helvetica", "B", 15); pdf.set_text_color(*NAVY); pdf.cell(0, 9, L["exec_summary"]); pdf.ln(10)
    pdf.set_font("Helvetica", "", 11); pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(0, 6, _narrative(facts, lang)); pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8); pdf.set_text_color(*GRAY); pdf.cell(0, 5, L["ai_note"]); pdf.ln(6)
    pdf.image(_fig_gauges(row, paths), x=15, w=180)

    pdf.add_page()
    pdf.image(_fig_identity(df_all, row, iso3, L, paths), x=15, w=180)
    pdf.ln(6)
    pdf.image(_fig_gdp(dc, L, paths), x=15, w=180)

    pdf.add_page()
    pdf.image(_fig_pestel(df_all, row, L, paths), x=15, w=180)

    pdf.add_page()
    for p in _fig_evol_heat(dc, L, paths):
        pdf.image(p, x=15, w=180)
        pdf.ln(6)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15); pdf.set_text_color(*NAVY); pdf.cell(0, 9, L["kpi"]); pdf.ln(9)
    widths = [70, 40, 40, 30]
    pdf.set_fill_color(*NAVY); pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 11)
    for txt, wd in zip([L["indicator"], L["value"], L["world"], L["vs"]], widths):
        pdf.cell(wd, 8, " " + txt, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 11)
    zebra = False
    for key, en, fr, fmt, inv in [("gdp_per_capita", "GDP per capita", "PIB/hab.", "${:,.0f}", False),
                                  ("gdp_growth_pct", "GDP growth", "Croissance", "{:.1f}%", False),
                                  ("inflation", "Inflation", "Inflation", "{:.1f}%", True),
                                  ("unemployment_pct", "Unemployment", "Chômage", "{:.1f}%", True),
                                  ("hdi", "HDI", "IDH", "{:.3f}", False),
                                  ("life_expectancy", "Life expectancy", "Espérance de vie", "{:.1f}", False)]:
        if key not in w.columns: continue
        v, med = row.get(key), w[key].median()
        pdf.set_fill_color(241, 245, 249) if zebra else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(widths[0], 8, " " + (en if lang == "en" else fr), fill=True)
        pdf.cell(widths[1], 8, fmt.format(v) if pd.notna(v) else "-", fill=True)
        pdf.cell(widths[2], 8, fmt.format(med) if pd.notna(med) else "-", fill=True)
        if pd.notna(v) and pd.notna(med):
            better = (v >= med) != inv
            pdf.set_text_color(*(GREEN if better else RED))
            pdf.cell(widths[3], 8, L["above"] if better else L["below"], fill=True)
        else:
            pdf.cell(widths[3], 8, "-", fill=True)
        pdf.ln(); zebra = not zebra
    pdf.ln(6)
    y0 = pdf.get_y()
    pdf.set_fill_color(232, 240, 250); pdf.rect(15, y0, 180, 36, style="F")
    pdf.set_xy(19, y0 + 4); pdf.set_font("Helvetica", "B", 15); pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, L["invest"]); pdf.ln(9)
    pdf.set_x(19); pdf.set_font("Helvetica", "B", 20); pdf.set_text_color(*BLUE)
    pdf.cell(0, 10, f"{score:.1f}/100"); pdf.ln(10)
    pdf.set_xy(105, y0 + 5); pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, L["flags"]); pdf.ln(7)
    pdf.set_x(105); pdf.set_font("Helvetica", "", 10)
    if flags:
        pdf.set_text_color(*RED); pdf.multi_cell(85, 5.5, "\n".join("- " + FLAG_LBL[lang][f] for f in flags))
    else:
        pdf.set_text_color(*GREEN); pdf.multi_cell(85, 5.5, "- " + L["noflag"])

    out = pdf.output()
    if isinstance(out, str):
        out = out.encode("latin1")
    out = bytes(out)
    for p in paths:
        try: os.remove(p)
        except OSError: pass
    return out
