"""Per-country PDF report: seaborn visuals + narrative (LLM w/ deterministic fallback)."""
import tempfile
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime, timezone
import analytics as an
import narrative

sns.set_theme(style="whitegrid", palette="husl")
sns.set_context("notebook", font_scale=1.1)

NAVY = (11, 37, 64)
BLUE = (0, 103, 192)
RED = (220, 38, 38)
GREEN = (5, 150, 105)
GRAY = (100, 116, 139)

LABELS = {
    "en": {"gen_btn": "Generate country report (PDF)", "generating": "Building PDF...", "dl_btn": "Download report (PDF)",
           "report_title": "Country Intelligence Report", "generated": "Generated on",
           "source": "Source: World Bank / Our World in Data", "exec_summary": "Executive Summary",
           "kpi": "Key Metrics", "pestel_analysis": "PESTEL Analysis", "conclusion": "Conclusion & Recommendation",
           "indicator": "Indicator", "value": "Value", "world": "World median", "vs_world": "vs world",
           "above": "above", "below": "below", "radar": "PESTEL Radar", "trend": "GDP & Inflation Trends",
           "sector": "Sector Composition", "trade": "Trade Balance (% GDP)", "invest_score": "Investment Score",
           "flags": "Risk Signals", "noflag": "No major risk signal", "political": "Political", "economic": "Economic",
           "social": "Social", "technological": "Technological", "environmental": "Environmental", "legal": "Legal",
           "exports": "Exports", "imports": "Imports", "net": "Net", "radar_world": "World median",
           "ai_note": "Narrative generated from computed indicators (LLM-enhanced when available)."},
    "fr": {"gen_btn": "Générer le rapport pays (PDF)", "generating": "Construction du PDF...", "dl_btn": "Télécharger le rapport (PDF)",
           "report_title": "Rapport d'intelligence pays", "generated": "Généré le",
           "source": "Source : Banque Mondiale / Our World in Data", "exec_summary": "Synthèse exécutive",
           "kpi": "Indicateurs clés", "pestel_analysis": "Analyse PESTEL", "conclusion": "Conclusion & Recommandation",
           "indicator": "Indicateur", "value": "Valeur", "world": "Médiane mondiale", "vs_world": "vs médiane",
           "above": "au-dessus", "below": "en-dessous", "radar": "Radar PESTEL", "trend": "Tendances PIB & Inflation",
           "sector": "Composition sectorielle", "trade": "Balance commerciale (% PIB)", "invest_score": "Score d'investissement",
           "flags": "Signaux de risque", "noflag": "Aucun signal de risque majeur", "political": "Politique", "economic": "Économique",
           "social": "Social", "technological": "Technologique", "environmental": "Environnemental", "legal": "Légal",
           "exports": "Exportations", "imports": "Importations", "net": "Solde", "radar_world": "Médiane mondiale",
           "ai_note": "Narratif généré à partir des indicateurs calculés (enrichi par LLM si disponible)."},
}


def ui_label(lang, key):
    return LABELS[lang][key]


def _png(fig, paths):
    buf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    fig.savefig(buf.name, dpi=300, bbox_inches="tight", facecolor="white", pad_inches=0.2)
    plt.close(fig)
    paths.append(buf.name)
    return buf.name


def _fig_radar(sc_c, sc_w, L, country, paths):
    cats = [L[p] for p in an.PESTEL_REPORT]
    vc = [sc_c[p] for p in an.PESTEL_REPORT]
    vw = [sc_w[p] for p in an.PESTEL_REPORT]
    ang = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    vc += vc[:1]
    vw += vw[:1]
    ang += ang[:1]
    fig = plt.figure(figsize=(8, 5.5))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(ang, vc, color="#0067C0", lw=2.5, label=country)
    ax.fill(ang, vc, color="#0067C0", alpha=.2)
    ax.plot(ang, vw, color="#94a3b8", lw=2, ls="--", label=L["radar_world"])
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(cats, fontsize=10, weight="bold")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=10, frameon=True)
    ax.set_title(L["radar"], fontsize=14, color="#0B2540", pad=25, weight="bold")
    return _png(fig, paths)


def _fig_trend(dc, L, paths):
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(dc["year"], dc["gdp_per_capita"], color="#0067C0", lw=2.5, marker="o", markersize=6, label="GDP/cap")
    ax1.set_ylabel("GDP/cap (USD)", color="#0067C0", fontsize=11, weight="bold")
    ax2 = ax1.twinx()
    ax2.plot(dc["year"], dc["inflation"], color="#dc2626", lw=2, marker="s", markersize=5, label="Inflation")
    ax2.set_ylabel("Inflation (%)", color="#dc2626", fontsize=11, weight="bold")
    ax1.set_title(L["trend"], fontsize=14, color="#0B2540", weight="bold", pad=15)
    ax1.grid(True, alpha=0.3)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9)
    fig.tight_layout()
    return _png(fig, paths)


def _fig_donut(row, L, paths):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    vals = [row["agriculture_pct"], row["industry_pct"], row["services_pct"]]
    wedges, texts, autotexts = ax.pie(vals, labels=["Agriculture", "Industry", "Services"], autopct="%1.1f%%",
           colors=["#059669", "#0067C0", "#7c3aed"], textprops={"fontsize": 11, "weight": "bold"},
           wedgeprops={"width": .4, "edgecolor": "white", "linewidth": 2})
    for a in autotexts:
        a.set_color("white")
        a.set_weight("bold")
    ax.set_title(L["sector"], fontsize=14, color="#0B2540", weight="bold", pad=15)
    return _png(fig, paths)


def _fig_trade(row, L, paths):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    vals = [row.get("exports_pct_gdp", 0), -row.get("imports_pct_gdp", 0), row.get("current_account_pct_gdp", 0)]
    colors = ["#059669", "#dc2626", "#0067C0"]
    labs = [L["exports"], L["imports"], L["net"]]
    ax.barh(labs, vals, color=colors, edgecolor="white", linewidth=1.5)
    ax.axvline(0, color="#64748b", lw=1, ls="--")
    for i, v in enumerate(vals):
        ax.text(v + (1.5 if v >= 0 else -1.5), i, f"{v:.1f}%", va="center", ha="left" if v >= 0 else "right",
                fontsize=11, weight="bold", color=colors[i])
    ax.set_title(L["trade"], fontsize=14, color="#0B2540", weight="bold", pad=15)
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
    dc, row = an.latest_row(df_all, country)
    year = int(row["year"])
    w = an.world(df_all, year)
    paths = []
    facts = an.build_facts(df_all, country)

    pdf = _PDF(f"{L['report_title']} - {L['source']}")
    pdf.set_margins(15, 15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, country)
    pdf.ln(14)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 9, L["report_title"])
    pdf.ln(9)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 7, f"{year} - {L['generated']} {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    pdf.ln(10)
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(1)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, L["exec_summary"])
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(0, 6, narrative.generate_narrative(facts, lang))
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, L["ai_note"])
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, L["kpi"])
    pdf.ln(9)
    widths = [70, 40, 40, 35]
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for txt, wdt in zip([L["indicator"], L["value"], L["world"], L["vs_world"]], widths):
        pdf.cell(wdt, 9, " " + txt, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    zebra = False
    for key, en, fr, fmt, inverse in an.KPIS:
        if key not in w.columns:
            continue
        v, med = row.get(key), w[key].median()
        pdf.set_fill_color(241, 245, 249) if zebra else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(widths[0], 8, " " + (en if lang == "en" else fr), fill=True)
        pdf.cell(widths[1], 8, fmt.format(v) if pd.notna(v) else "-", fill=True)
        pdf.cell(widths[2], 8, fmt.format(med) if pd.notna(med) else "-", fill=True)
        if pd.notna(v) and pd.notna(med):
            better = (v >= med) != inverse
            pdf.set_text_color(*(GREEN if better else RED))
            pdf.cell(widths[3], 8, L["above"] if better else L["below"], fill=True)
        else:
            pdf.cell(widths[3], 8, "-", fill=True)
        pdf.ln()
        zebra = not zebra
    pdf.ln(8)

    y0 = pdf.get_y()
    pdf.set_fill_color(232, 240, 250)
    pdf.rect(15, y0, 180, 40, style="F")
    pdf.set_xy(19, y0 + 4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, L["invest_score"])
    pdf.ln(8)
    pdf.set_x(19)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 12, f"{facts['score']:.1f}/100")
    pdf.ln(12)
    pdf.set_xy(105, y0 + 5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, L["flags"])
    pdf.ln(7)
    pdf.set_x(105)
    pdf.set_font("Helvetica", "", 9)
    if facts["flags"]:
        pdf.set_text_color(*RED)
        pdf.multi_cell(85, 5.5, "\n".join("- " + f for f in facts["flags"]))
    else:
        pdf.set_text_color(*GREEN)
        pdf.multi_cell(85, 5.5, "- " + L["noflag"])
    pdf.set_y(y0 + 48)

    pdf.add_page()
    sc_c = an.pillar_scores(df_all, year, lambda c: row.get(c))
    sc_w = an.pillar_scores(df_all, year, lambda c: w[c].median() if c in w.columns else None)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, L["pestel_analysis"])
    pdf.ln(11)
    pdf.image(_fig_radar(sc_c, sc_w, L, country, paths), x=15, y=pdf.get_y(), w=180, h=125)
    pdf.set_y(pdf.get_y() + 130)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 9, L["trend"])
    pdf.ln(10)
    pdf.image(_fig_trend(dc, L, paths), x=15, y=pdf.get_y(), w=180, h=90)

    pdf.add_page()
    if all(c in row.index and pd.notna(row[c]) for c in ["agriculture_pct", "industry_pct", "services_pct"]):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 9, L["sector"])
        pdf.ln(10)
        pdf.image(_fig_donut(row, L, paths), x=40, y=pdf.get_y(), w=130, h=95)
        pdf.set_y(pdf.get_y() + 100)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, L["trade"])
    pdf.ln(10)
    pdf.image(_fig_trade(row, L, paths), x=15, y=pdf.get_y(), w=180, h=80)

    out = pdf.output()
    if isinstance(out, str):
        out = out.encode("latin1")
    for p in paths:
        try:
            os.remove(p)
        except OSError:
            pass
    return bytes(out)
