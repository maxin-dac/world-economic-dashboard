"""
Global Economic Intelligence Dashboard
Real World Bank + Our World in Data · 217 countries · 2000-2024
Code is 100% in English. All user-facing text is bilingual (EN/FR) via translations.py.

Design: glassmorphism cards on an ambient gradient canvas, solid navy "Control
Center" sidebar, single typeface (Manrope), light/dark toggle, hover tooltips on
KPI cards, dynamic per-country interpretations, PESTEL analytics.
"""
import os
import sys
import json
import subprocess

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import streamlit as st

from translations import t, TRANSLATIONS

# Optional dependency for translating country names (FR)
try:
    import pycountry
    _HAS_PYCOUNTRY = True
except ImportError:
    _HAS_PYCOUNTRY = False


# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GLOBAL ECONOMIC DASHBOARD",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════════════
# THEME STATE (read before CSS + Plotly template)
# ═══════════════════════════════════════════════════════════════════════════
is_dark = st.session_state.get("theme_choice", "☀️") == "🌙"


# ═══════════════════════════════════════════════════════════════════════════
# PLOTLY TEMPLATE — Manrope everywhere, centered titles, theme-aware colors
# ═══════════════════════════════════════════════════════════════════════════
def _build_template(dark: bool) -> go.layout.Template:
    tpl = go.layout.Template()
    tpl.layout.paper_bgcolor = "rgba(0,0,0,0)"
    tpl.layout.plot_bgcolor = "rgba(0,0,0,0)"
    tpl.layout.font.family = "Manrope, system-ui, sans-serif"
    tpl.layout.font.size = 12
    tpl.layout.font.color = "#cbd5e1" if dark else "#475569"
    tpl.layout.title.font.family = "Manrope, system-ui, sans-serif"
    tpl.layout.title.font.size = 16
    tpl.layout.title.font.weight = 700
    tpl.layout.title.font.color = "#f1f5f9" if dark else "#0f172a"
    tpl.layout.title.x = 0.5
    tpl.layout.title.xanchor = "center"
    grid = "rgba(148,163,184,0.14)" if dark else "rgba(100,116,139,0.12)"
    tpl.layout.xaxis.gridcolor = grid
    tpl.layout.yaxis.gridcolor = grid
    tpl.layout.transition = dict(duration=450, easing="cubic-in-out")
    return tpl

pio.templates["app_theme"] = _build_template(is_dark)
pio.templates.default = "app_theme"


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — glassmorphism + solid navy sidebar, single typeface
# ═══════════════════════════════════════════════════════════════════════════
_LIGHT_TOKENS = """
--bg: radial-gradient(1200px 600px at 85% -10%, rgba(0,103,192,.08), transparent 55%),
      radial-gradient(1000px 500px at -10% 20%, rgba(5,150,105,.05), transparent 50%),
      radial-gradient(900px 500px at 50% 110%, rgba(0,103,192,.06), transparent 55%),
      linear-gradient(180deg, #f8fafd 0%, #f1f5fa 50%, #eef2f8 100%);
--card: linear-gradient(150deg, rgba(255,255,255,.92), rgba(255,255,255,.68));
--card-border: rgba(255,255,255,.75);
--card-inset: inset 0 1px 0 rgba(255,255,255,.9);
--ink: #0f172a; --ink-2: #475569; --ink-3: #94a3b8;
--edge: rgba(15,23,42,.08); --edge-strong: rgba(15,23,42,.14);
--shadow-1: 0 1px 2px rgba(15,23,42,.04), 0 2px 8px rgba(15,23,42,.05);
--shadow-2: 0 1px 2px rgba(15,23,42,.05), 0 4px 16px rgba(15,23,42,.08), 0 12px 40px rgba(15,23,42,.06);
--sidebar-bg: #0B2540;
--sidebar-text: #dbe7f3; --sidebar-text-2: #8fa6bd; --sidebar-border: rgba(255,255,255,.10);
--sidebar-input-bg: rgba(255,255,255,.07); --sidebar-input-border: rgba(255,255,255,.14);
--tab-active-bg: rgba(255,255,255,.92);
--banner-bg: linear-gradient(135deg, rgba(0,103,192,.07), rgba(0,103,192,.025));
--banner-border: rgba(0,103,192,.14);
--btn-bg: rgba(255,255,255,.82); --btn-border: rgba(15,23,42,.14); --btn-text: #0f172a;
--null-bg: #f1f5f9; --null-text: #94a3b8;
--scroll-thumb: rgba(255,255,255,.2);
"""

_DARK_TOKENS = """
--bg: radial-gradient(1200px 600px at 85% -10%, rgba(46,141,224,.13), transparent 55%),
      radial-gradient(1000px 500px at -10% 20%, rgba(16,185,129,.07), transparent 50%),
      radial-gradient(900px 500px at 50% 110%, rgba(0,103,192,.10), transparent 55%),
      linear-gradient(180deg, #0b1120 0%, #0f172a 50%, #0b1120 100%);
--card: linear-gradient(150deg, rgba(30,41,59,.85), rgba(15,23,42,.75));
--card-border: rgba(148,163,184,.14);
--card-inset: inset 0 1px 0 rgba(255,255,255,.06);
--ink: #f1f5f9; --ink-2: #cbd5e1; --ink-3: #64748b;
--edge: rgba(255,255,255,.08); --edge-strong: rgba(255,255,255,.14);
--shadow-1: 0 1px 2px rgba(0,0,0,.4), 0 2px 8px rgba(0,0,0,.35);
--shadow-2: 0 1px 2px rgba(0,0,0,.4), 0 4px 16px rgba(0,0,0,.45), 0 12px 40px rgba(0,0,0,.4);
--sidebar-bg: #0A1A2E;
--sidebar-text: #e2e8f0; --sidebar-text-2: #94a3b8; --sidebar-border: rgba(255,255,255,.10);
--sidebar-input-bg: rgba(30,41,59,.7); --sidebar-input-border: rgba(148,163,184,.18);
--tab-active-bg: rgba(30,41,59,.9);
--banner-bg: linear-gradient(135deg, rgba(46,141,224,.13), rgba(46,141,224,.04));
--banner-border: rgba(46,141,224,.28);
--btn-bg: rgba(30,41,59,.8); --btn-border: rgba(148,163,184,.18); --btn-text: #f1f5f9;
--null-bg: rgba(148,163,184,.08); --null-text: #64748b;
--scroll-thumb: rgba(148,163,184,.25);
"""

# Font import MUST be the very first rule in the <style> block.
_FONT_IMPORT = ("@import url('https://fonts.googleapis.com/css2?"
                "family=Manrope:wght@300;400;500;600;700;800&display=swap');")

_COMMON_CSS = """
:root {
  --blue: #0067C0; --blue-bright: #2E8DE0; --blue-deep: #0050A0; --blue-glow: rgba(0,103,192,.16);
  --pos: #059669; --neg: #dc2626; --warn: #d97706;
  --font: 'Manrope', system-ui, sans-serif;
  --r-md: 12px; --r-sm: 8px;
  --ease: cubic-bezier(.22, 1, .36, 1);
}

/* ── ONE typeface everywhere ── */
html, body, [class*="css"], .stMarkdown, .stText,
h1, h2, h3, h4, h5, h6, p, label, a, small,
[data-testid="stCaptionContainer"], .stCaption,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"],
[data-baseweb="tab"], [data-baseweb="tab"] p,
[data-baseweb="select"], [data-baseweb="input"], [data-baseweb="tag"],
[data-testid="stDataFrame"], [data-testid="stTable"],
[data-testid="stPopoverButton"] button { font-family: var(--font) !important; }

/* ── Ambient gradient canvas ── */
.stApp { background: var(--bg); background-attachment: fixed; }
::selection { background: var(--blue-glow); }
hr { border-color: var(--edge-strong); opacity: .5; }

/* ── Typographic hierarchy (never overflow the column) ── */
h1, h2 { font-weight: 800 !important; color: var(--ink) !important;
         letter-spacing: -.02em !important; overflow-wrap: break-word; word-break: break-word; }
h3 { font-weight: 700 !important; color: var(--ink) !important; letter-spacing: -.015em !important; }
h4 { font-weight: 700 !important; font-size: .75rem !important; text-transform: uppercase !important;
     letter-spacing: .08em !important; color: var(--ink-2) !important; }
[data-testid="stCaptionContainer"], .stCaption {
    font-size: .68rem; letter-spacing: .02em; color: var(--ink-3); font-weight: 500; }

/* ── Sidebar — solid navy Control Center ── */
[data-testid="stSidebar"] {
    position: relative; background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    scrollbar-width: thin; scrollbar-color: var(--scroll-thumb) transparent;
}
[data-testid="stSidebar"]::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; z-index: 10;
    background: linear-gradient(90deg, var(--blue), var(--blue-bright) 50%, #22d3ee);
}
[data-testid="stSidebar"]::-webkit-scrollbar { width: 8px; }
[data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 4px; }
/* hide the collapse control (removes the keyboard_double_* glyph) */
[data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stSidebar"] h2 {
    color: var(--sidebar-text) !important; font-size: 1.02rem !important; font-weight: 800 !important;
    border-bottom: 1px solid var(--sidebar-border) !important; padding-bottom: 10px;
    overflow-wrap: break-word; word-break: break-word;
}
/* live status badge sits in normal flow (no negative offset → no overlap) */
[data-testid="stSidebar"] h2::after {
    content: "● LIVE"; display: block; margin-top: 8px;
    font-size: .58rem; font-weight: 600; letter-spacing: .12em; color: #34d399;
    animation: livePulse 2.2s infinite;
}
@keyframes livePulse { 0%,100% { opacity: 1; } 50% { opacity: .4; } }
[data-testid="stSidebar"], [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] div { color: var(--sidebar-text); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] small {
    color: var(--sidebar-text-2) !important; font-size: .64rem !important; font-weight: 500; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"], [data-testid="stSidebar"] label {
    color: var(--sidebar-text) !important; font-weight: 700 !important; font-size: .72rem !important;
    text-transform: uppercase; letter-spacing: .07em; }
[data-testid="stSidebar"] button, [data-testid="stSidebar"] a,
[data-testid="stSidebar"] [role="button"] { color: var(--sidebar-text) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--sidebar-input-bg) !important; border: 1px solid var(--sidebar-input-border) !important;
    border-radius: var(--r-sm) !important; backdrop-filter: blur(8px);
    transition: border-color .2s var(--ease), box-shadow .2s var(--ease); }
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color: rgba(46,141,224,.55) !important; box-shadow: 0 0 0 3px rgba(46,141,224,.12); }
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(46,141,224,.20) !important; color: #7dd3fc !important;
    border: 1px solid rgba(46,141,224,.30); border-radius: 6px; }
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: var(--sidebar-text-2) !important; color: var(--sidebar-text-2) !important; }
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: linear-gradient(180deg, var(--blue-bright), var(--blue)) !important;
    color: #ffffff !important; border: 1px solid rgba(255,255,255,.18) !important;
    border-radius: var(--r-sm) !important; font-weight: 700; letter-spacing: .03em;
    box-shadow: 0 2px 10px rgba(0,103,192,.35), inset 0 1px 0 rgba(255,255,255,.25);
    transition: all .22s var(--ease); }
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: linear-gradient(180deg, #3d9ae8, var(--blue-bright)) !important;
    box-shadow: 0 4px 18px rgba(0,103,192,.5), inset 0 1px 0 rgba(255,255,255,.3); transform: translateY(-1px); }
[data-testid="stSidebar"] hr { border-color: var(--sidebar-border) !important; opacity: .8; }

/* ── KPI cards — glass, equal height, hover lift + top accent bar ── */
[data-testid="stMetric"] {
    background: var(--card); backdrop-filter: blur(20px) saturate(170%);
    -webkit-backdrop-filter: blur(20px) saturate(170%);
    border: 1px solid var(--card-border); border-radius: var(--r-md);
    padding: 16px 16px 14px; height: 124px; box-sizing: border-box;
    display: flex; flex-direction: column; justify-content: center; gap: 4px; overflow: hidden;
    position: relative; box-shadow: var(--shadow-1), var(--card-inset);
    transition: transform .25s var(--ease), box-shadow .25s var(--ease), border-color .25s var(--ease); }
[data-testid="stMetric"]::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; opacity: .45;
    background: linear-gradient(90deg, var(--blue), var(--blue-bright)); transition: opacity .25s var(--ease); }
[data-testid="stMetric"]:hover { transform: translateY(-2px);
    box-shadow: var(--shadow-2), var(--card-inset); border-color: rgba(0,103,192,.35); }
[data-testid="stMetric"]:hover::before { opacity: 1; }
[data-testid="stMetricLabel"] {
    font-weight: 700 !important; font-size: .6rem !important; text-transform: uppercase !important;
    letter-spacing: .05em !important; color: var(--ink-2) !important;
    white-space: normal !important; line-height: 1.2 !important;
    display: -webkit-box !important; -webkit-line-clamp: 2 !important; -webkit-box-orient: vertical !important;
    overflow: hidden !important; }
[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 800 !important;
    color: var(--ink) !important; letter-spacing: -.02em !important; font-variant-numeric: tabular-nums; }
[data-testid="stMetricDelta"] { font-size: .66rem !important; font-weight: 600 !important;
    font-variant-numeric: tabular-nums; }

/* ── Tabs — segmented control, WRAP to avoid horizontal overflow ── */
[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--edge);
    background: var(--card); backdrop-filter: blur(12px);
    border-radius: var(--r-md) var(--r-md) 0 0; padding: 6px 4px 0; }
[data-baseweb="tab"] { position: relative; flex: 1 1 0 !important; min-width: 0 !important;
    justify-content: center; font-weight: 700 !important; color: var(--ink-2); background: transparent;
    border: 1px solid transparent; border-bottom: none;
    border-radius: var(--r-sm) var(--r-sm) 0 0; padding: 10px 4px 9px;
    transition: background .22s var(--ease), color .22s var(--ease), box-shadow .22s var(--ease); }
[data-baseweb="tab"] p {
    font-weight: 700 !important; font-size: .7rem !important; letter-spacing: 0 !important;
    line-height: 1.15 !important; text-align: center; margin: 0;
    white-space: normal !important; display: -webkit-box !important;
    -webkit-line-clamp: 2 !important; -webkit-box-orient: vertical !important; overflow: hidden !important; }
[data-baseweb="tab"]:hover { background: var(--edge); color: var(--ink); }
[data-baseweb="tab"][aria-selected="true"] { background: var(--tab-active-bg);
    border-color: var(--card-border); box-shadow: 0 -2px 14px rgba(0,0,0,.08), var(--card-inset); }
[data-baseweb="tab"][aria-selected="true"]::after { content: ""; position: absolute;
    bottom: 0; left: 50%; transform: translateX(-50%); width: 55%; height: 3px;
    border-radius: 3px 3px 0 0; background: linear-gradient(90deg, var(--blue), var(--blue-bright)); }
[data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] p {
    color: var(--blue-bright) !important; font-weight: 800 !important; }

/* ── Chart & table cards — glass ── */
[data-testid="stPlotlyChart"] { background: var(--card);
    backdrop-filter: blur(20px) saturate(170%); -webkit-backdrop-filter: blur(20px) saturate(170%);
    border: 1px solid var(--card-border); border-radius: var(--r-md);
    box-shadow: var(--shadow-1), var(--card-inset); padding: 12px 8px 6px;
    transition: box-shadow .3s var(--ease), border-color .3s var(--ease); }
[data-testid="stPlotlyChart"]:hover { box-shadow: var(--shadow-2), var(--card-inset);
    border-color: rgba(0,103,192,.25); }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--card-border);
    border-radius: var(--r-md); overflow: hidden; box-shadow: var(--shadow-1); }

/* ── Income tiles (popovers) — same card look + top bar + equal height ── */
[data-testid="stPopoverButton"] button,
[data-testid="stPopoverButton"] [data-testid="stBaseButton-secondary"],
button[data-testid="stPopoverButton"] {
    background: var(--card) !important; backdrop-filter: blur(20px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(170%) !important;
    border: 1px solid var(--card-border) !important; border-radius: var(--r-md) !important;
    height: 124px !important; width: 100% !important; box-sizing: border-box !important;
    display: flex !important; flex-direction: column !important; align-items: stretch !important;
    justify-content: center !important; padding: 16px 16px 14px !important;
    box-shadow: var(--shadow-1), var(--card-inset) !important;
    position: relative !important; overflow: hidden !important; text-align: left !important;
    transition: transform .25s var(--ease), box-shadow .25s var(--ease), border-color .25s var(--ease) !important;
    cursor: pointer !important; }
[data-testid="stPopoverButton"] button::before,
[data-testid="stPopoverButton"] [data-testid="stBaseButton-secondary"]::before,
button[data-testid="stPopoverButton"]::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; z-index: 1;
    background: linear-gradient(90deg, var(--blue), var(--blue-bright));
    opacity: .45; transition: opacity .25s var(--ease); }
[data-testid="stPopoverButton"] button:hover::before { opacity: 1; }
/* hide the popover chevron (removes the expand_more glyph) */
[data-testid="stPopoverButton"] [data-testid="stIconMaterial"],
[data-testid="stPopoverButton"] svg { display: none !important; }
/* label line (small, uppercase) */
[data-testid="stPopoverButton"] button p,
[data-testid="stPopoverButton"] button [data-testid="stMarkdownContainer"] {
    font-weight: 700 !important; font-size: .6rem !important; text-transform: uppercase !important;
    letter-spacing: .05em !important; color: var(--ink-2) !important; line-height: 1.2 !important;
    white-space: normal !important; margin: 0 !important;
    display: -webkit-box !important; -webkit-line-clamp: 3 !important; -webkit-box-orient: vertical !important;
    overflow: hidden !important; }
/* the bold count rendered big, like a metric value */
[data-testid="stPopoverButton"] button strong {
    display: block !important; font-size: 1.6rem !important; font-weight: 800 !important;
    text-transform: none !important; letter-spacing: -.02em !important; color: var(--ink) !important;
    line-height: 1.1 !important; margin-top: 2px !important; font-variant-numeric: tabular-nums; }
[data-testid="stPopoverButton"] button:hover,
[data-testid="stPopoverButton"] [data-testid="stBaseButton-secondary"]:hover,
button[data-testid="stPopoverButton"]:hover {
    transform: translateY(-2px) !important; box-shadow: var(--shadow-2), var(--card-inset) !important;
    border-color: rgba(0,103,192,.35) !important; }

/* ── Insight banner — Fluent InfoBar ── */
@keyframes bannerIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
.indicator-banner { background: var(--banner-bg); backdrop-filter: blur(12px);
    border: 1px solid var(--banner-border); border-left: 3px solid var(--blue);
    border-radius: var(--r-sm); padding: 11px 15px; font-size: .85rem; line-height: 1.55;
    font-weight: 500; color: var(--ink); box-shadow: var(--shadow-1);
    animation: bannerIn .35s var(--ease); transition: box-shadow .25s var(--ease), border-color .25s var(--ease); }
.indicator-banner:hover { box-shadow: var(--shadow-2); border-left-color: var(--blue-bright); }

/* ── Buttons & inputs (main area) ── */
.stButton > button, [data-testid="stBaseButton-secondary"],
[data-testid="stDownloadButton"] > button {
    font-weight: 700; border-radius: var(--r-sm); border: 1px solid var(--btn-border);
    background: var(--btn-bg); backdrop-filter: blur(8px); color: var(--btn-text);
    box-shadow: var(--shadow-1); transition: all .2s var(--ease); }
.stButton > button:hover, [data-testid="stBaseButton-secondary"]:hover,
[data-testid="stDownloadButton"] > button:hover {
    border-color: rgba(0,103,192,.4); box-shadow: var(--shadow-2), 0 0 0 3px var(--blue-glow);
    transform: translateY(-1px); }
[data-baseweb="select"] > div, [data-baseweb="input"] > div {
    border-radius: var(--r-sm); border-color: var(--btn-border); background: var(--btn-bg); }
"""

st.markdown(
    "<style>" + _FONT_IMPORT + ":root{" + (_DARK_TOKENS if is_dark else _LIGHT_TOKENS) + "}" + _COMMON_CSS + "</style>",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════
INCOME_ORDER = ["High income", "Upper middle income", "Lower middle income", "Low income"]

INCOME_COLORS = {
    "High income": "#1a9850", "Upper middle income": "#fee08b",
    "Lower middle income": "#f46d43", "Low income": "#d73027",
}
REGION_COLORS = {
    "East Asia & Pacific": "#1D9E75", "Europe & Central Asia": "#3778C2",
    "Latin America & Caribbean": "#E67E22", "Middle East & North Africa": "#9B59B6",
    "North America": "#17A589", "South Asia": "#F39C12", "Sub-Saharan Africa": "#E24B4A",
}
SECTOR_COLORS = {"Agriculture": "#1D9E75", "Industry": "#3778C2", "Services": "#E67E22"}
SECTOR_LABEL_KEYS = {"agriculture_pct": "Agriculture", "industry_pct": "Industry", "services_pct": "Services"}
GEO_STYLE = dict(
    showframe=False, showcoastlines=True, coastlinecolor="#b0bec5",
    showland=True, landcolor="#f0f0f0", showocean=True, oceancolor="#e0f2fe",
    showlakes=True, lakecolor="#e0f2fe", showcountries=True,
    countrycolor="#b0bec5", countrywidth=0.6,
)


# ═══════════════════════════════════════════════════════════════════════════
# PESTEL STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════
PESTEL_PILLAR_ORDER = ["political", "economic", "social", "technological", "environmental", "legal"]
PESTEL_LABEL_KEYS = {
    "political": "pestel_political", "economic": "pestel_economic",
    "social": "pestel_social", "technological": "pestel_technological",
    "environmental": "pestel_environmental", "legal": "pestel_legal",
}
PESTEL_INDICATORS = {
    "political": ["govt_effectiveness_index", "military_expenditure_pct_gdp",
                  "military_expenditure_pct_govt", "political_stability_index"],
    "economic": ["agriculture_pct", "cpi_index_raw", "current_account_pct_gdp",
                 "debt_pct_gdp", "exchange_rate", "exports_pct_gdp", "fdi_pct_gdp",
                 "gdp_growth_pct", "gdp_per_capita", "gdp_per_capita_ppp", "gdp_total_bn",
                 "gross_fixed_capital_formation_pct_gdp", "imports_pct_gdp", "industry_pct",
                 "inflation", "remittances_pct_gdp", "reserves_months_imports",
                 "services_pct", "tax_revenue_pct_gdp", "trade_openness_pct_gdp"],
    "social": ["basic_sanitation_access_pct", "education_expenditure_pct_gdp",
               "fertility_rate", "gini_index", "health_expenditure_per_capita", "hdi",
               "labor_force_participation_pct", "life_expectancy", "literacy_rate",
               "population_mn", "primary_completion_rate_pct",
               "school_enrollment_secondary_pct", "under5_mortality_per_1000",
               "unemployment_pct", "urban_population_pct", "youth_unemployment_pct"],
    "technological": ["bank_account_ownership_pct", "fixed_broadband_per_100",
                      "high_tech_exports_pct", "internet_users_pct",
                      "mobile_subscriptions_per_100", "rd_expenditure_pct_gdp",
                      "researchers_per_million"],
    "environmental": ["cereal_yield_kg_per_ha", "electric_power_losses_pct",
                      "electricity_access_pct", "pm25_air_pollution"],
    "legal": ["control_of_corruption", "corruption_perception_index",
              "regulatory_quality", "rule_of_law_index",
              "transparency_corruption_score", "voice_accountability", "women_parliament_pct"],
}
INDICATOR_TO_PILLAR = {ind: p for p, inds in PESTEL_INDICATORS.items() for ind in inds}
CORE_INDICATORS = {ind: ind for group in PESTEL_INDICATORS.values() for ind in group}
INVERSE_INDICATORS = {
    "inflation", "cpi_index_raw", "debt_pct_gdp", "imports_pct_gdp",
    "unemployment_pct", "youth_unemployment_pct", "pm25_air_pollution",
    "military_expenditure_pct_gdp", "military_expenditure_pct_govt",
    "gini_index", "under5_mortality_per_1000", "fertility_rate",
    "electric_power_losses_pct",
}


# ═══════════════════════════════════════════════════════════════════════════
# SEMANTIC COLOR SCALES
# ═══════════════════════════════════════════════════════════════════════════
INDICATOR_COLORSCALE = {
    "gdp_per_capita": "Viridis", "gdp_per_capita_ppp": "Viridis",
    "gdp_total_bn": "Viridis", "gdp_growth_pct": "RdYlGn",
    "gross_fixed_capital_formation_pct_gdp": "YlGn", "trade_openness_pct_gdp": "YlGn",
    "exports_pct_gdp": "YlGn", "fdi_pct_gdp": "YlGn",
    "remittances_pct_gdp": "YlGn", "reserves_months_imports": "YlGn",
    "tax_revenue_pct_gdp": "PuBu", "current_account_pct_gdp": "RdYlGn",
    "inflation": "YlOrRd", "cpi_index_raw": "YlOrRd", "debt_pct_gdp": "YlOrRd",
    "imports_pct_gdp": "OrRd", "exchange_rate": "Plasma",
    "agriculture_pct": "YlGn", "industry_pct": "PuBu", "services_pct": "Plasma",
    "life_expectancy": "RdYlGn", "literacy_rate": "RdYlGn", "hdi": "RdYlGn",
    "primary_completion_rate_pct": "RdYlGn", "school_enrollment_secondary_pct": "RdYlGn",
    "basic_sanitation_access_pct": "YlGn", "health_expenditure_per_capita": "YlGn",
    "education_expenditure_pct_gdp": "YlGn", "labor_force_participation_pct": "YlGn",
    "urban_population_pct": "PuBu", "population_mn": "PuBu",
    "unemployment_pct": "YlOrRd", "youth_unemployment_pct": "YlOrRd",
    "under5_mortality_per_1000": "YlOrRd", "fertility_rate": "YlOrRd", "gini_index": "YlOrRd",
    "internet_users_pct": "Cividis", "mobile_subscriptions_per_100": "Cividis",
    "fixed_broadband_per_100": "Cividis", "bank_account_ownership_pct": "RdYlGn",
    "high_tech_exports_pct": "Cividis", "rd_expenditure_pct_gdp": "Cividis",
    "researchers_per_million": "Cividis",
    "electricity_access_pct": "YlGn", "cereal_yield_kg_per_ha": "YlGn",
    "pm25_air_pollution": "Reds", "electric_power_losses_pct": "OrRd",
    "govt_effectiveness_index": "RdYlGn", "political_stability_index": "RdYlGn",
    "military_expenditure_pct_gdp": "OrRd", "military_expenditure_pct_govt": "OrRd",
    "control_of_corruption": "RdYlGn", "rule_of_law_index": "RdYlGn",
    "regulatory_quality": "RdYlGn", "voice_accountability": "RdYlGn",
    "transparency_corruption_score": "RdYlGn",
    "corruption_perception_index": "RdYlGn", "women_parliament_pct": "RdYlGn",
}


def get_expressive_colorscale(indicator_key: str) -> str:
    """Return a semantic, high-contrast color scale for an indicator."""
    if indicator_key in INDICATOR_COLORSCALE:
        return INDICATOR_COLORSCALE[indicator_key]
    return "YlOrRd" if indicator_key in INVERSE_INDICATORS else "Viridis"


# ═══════════════════════════════════════════════════════════════════════════
# INDICATOR EXPLANATIONS (bilingual) — key -> (en_desc, en_tip, fr_desc, fr_tip)
# ═══════════════════════════════════════════════════════════════════════════
INDICATOR_INFO = {
    "gdp_per_capita": ("Average economic output per person.", "Higher = wealthier population.",
                       "Production économique moyenne par personne.", "Plus élevé = population plus riche."),
    "gdp_per_capita_ppp": ("GDP per person adjusted for purchasing power.", "Better for comparing living standards.",
                           "PIB par habitant ajusté au pouvoir d'achat.", "Plus pertinent pour comparer les niveaux de vie."),
    "gdp_total_bn": ("Total size of the economy.", "Higher = larger economy (not necessarily richer people).",
                     "Taille totale de l'économie.", "Plus élevé = économie plus grande (pas forcément plus riche par habitant)."),
    "gdp_growth_pct": ("Annual growth rate of the economy.", "Positive = expanding; negative = recession.",
                       "Taux de croissance annuel de l'économie.", "Positif = expansion ; négatif = récession."),
    "gross_fixed_capital_formation_pct_gdp": ("Investment in fixed assets (machinery, infrastructure).", "Higher = more investment.",
                                              "Investissement en actifs fixes (machines, infrastructures).", "Plus élevé = plus d'investissement."),
    "trade_openness_pct_gdp": ("Total trade (exports + imports) as a share of GDP.", "Higher = more open economy.",
                               "Commerce total (exports + imports) rapporté au PIB.", "Plus élevé = économie plus ouverte."),
    "cpi_index_raw": ("Consumer Price Index, base 100 in 2010 — measures PRICE levels, NOT corruption.",
                      "100 = 2010 price level; higher = more cumulative inflation since 2010.",
                      "Indice des prix à la consommation, base 100 en 2010 — mesure les PRIX, PAS la corruption.",
                      "100 = niveau des prix de 2010 ; plus élevé = plus d'inflation cumulée depuis 2010."),
    "inflation": ("Annual percentage change in consumer prices.", "Moderate (2-3%) is healthy; very high erodes purchasing power.",
                  "Variation annuelle en % des prix à la consommation.", "Modérée (2-3 %) = saine ; très élevée = érode le pouvoir d'achat."),
    "debt_pct_gdp": ("Government debt as a share of GDP.", "Higher = heavier public debt burden.",
                     "Dette publique rapportée au PIB.", "Plus élevé = fardeau de la dette plus lourd."),
    "tax_revenue_pct_gdp": ("Tax revenue collected by the state as a share of GDP.", "Higher = greater fiscal capacity.",
                            "Recettes fiscales de l'État rapportées au PIB.", "Plus élevé = plus de capacité à financer les services publics."),
    "exports_pct_gdp": ("Exports of goods & services as a share of GDP.", "Higher = more export-oriented economy.",
                        "Exportations de biens et services rapportées au PIB.", "Plus élevé = économie plus tournée vers l'export."),
    "imports_pct_gdp": ("Imports of goods & services as a share of GDP.", "Not inherently bad; read together with exports.",
                        "Importations de biens et services rapportées au PIB.", "Pas forcément négatif ; à lire avec les exports."),
    "fdi_pct_gdp": ("Foreign direct investment inflows as a share of GDP.", "Higher = more attractive to foreign investors.",
                    "Investissements directs étrangers entrants rapportés au PIB.", "Plus élevé = plus attractif pour les investisseurs étrangers."),
    "current_account_pct_gdp": ("Net balance of trade, income and transfers vs GDP.", "Positive = net lender; negative = net borrower.",
                                "Solde net du commerce, des revenus et transferts rapporté au PIB.", "Positif = prêteur net ; négatif = emprunteur net."),
    "remittances_pct_gdp": ("Money sent home by migrants as a share of GDP.", "Higher = strong reliance on diaspora income.",
                            "Fonds envoyés par les migrants rapportés au PIB.", "Plus élevé = forte dépendance aux revenus de la diaspora."),
    "reserves_months_imports": ("Foreign exchange reserves expressed in months of imports.", "3+ months is a common safety threshold.",
                                "Réserves de change exprimées en mois d'importations.", "3 mois et plus = seuil de sécurité courant."),
    "exchange_rate": ("Local currency units per US dollar.", "Context-dependent; not comparable as good/bad on its own.",
                      "Unités de monnaie locale pour un dollar US.", "Dépend du contexte ; pas interprétable seul comme bon/mauvais."),
    "agriculture_pct": ("Agriculture share of GDP.", "High share often signals a developing economy.",
                        "Part de l'agriculture dans le PIB.", "Une part élevée signale souvent une économie en développement."),
    "industry_pct": ("Industry share of GDP (manufacturing, mining, construction).", "Reflects industrialization level.",
                     "Part de l'industrie dans le PIB (manufacture, mines, construction).", "Reflette le niveau d'industrialisation."),
    "services_pct": ("Services share of GDP.", "Dominant in advanced, service-based economies.",
                     "Part des services dans le PIB.", "Dominante dans les économies avancées tertiarisées."),
    "life_expectancy": ("Average number of years a newborn is expected to live.", "Higher = better health & living conditions.",
                        "Nombre moyen d'années qu'un nouveau-né est censé vivre.", "Plus élevé = meilleure santé et conditions de vie."),
    "literacy_rate": ("Share of adults (15+) who can read and write.", "Higher = more educated population.",
                      "Part des adultes (15 ans+) sachant lire et écrire.", "Plus élevé = population plus instruite."),
    "hdi": ("Composite index of life expectancy, education and income (0-1).", "Higher = more human development. >0.8 = very high.",
            "Indice composite espérance de vie, éducation et revenu (0-1).", "Plus élevé = plus de développement humain. >0,8 = très élevé."),
    "primary_completion_rate_pct": ("Share of children completing primary school.", "Higher = better basic education coverage.",
                                    "Part des enfants achevant l'école primaire.", "Plus élevé = meilleure couverture de l'éducation de base."),
    "school_enrollment_secondary_pct": ("Secondary school enrollment ratio (gross).", "Higher = broader access to secondary education.",
                                        "Taux brut de scolarisation dans le secondaire.", "Plus élevé = accès plus large au secondaire."),
    "under5_mortality_per_1000": ("Deaths of children under 5 per 1,000 live births.", "Lower = better child health.",
                                  "Décès d'enfants de moins de 5 ans pour 1 000 naissances.", "Plus faible = meilleure santé infantile."),
    "fertility_rate": ("Average number of children born per woman.", "~2.1 = replacement level; higher = faster population growth.",
                       "Nombre moyen d'enfants nés par femme.", "~2,1 = seuil de remplacement ; plus élevé = croissance démographique plus rapide."),
    "gini_index": ("Measure of income inequality (0 = equal, 100 = unequal).", "Lower = more equal income distribution.",
                   "Mesure des inégalités de revenu (0 = égalité, 100 = inégalité totale).", "Plus faible = répartition des revenus plus égalitaire."),
    "unemployment_pct": ("Share of the labor force without a job.", "Lower = tighter labor market.",
                         "Part de la population active sans emploi.", "Plus faible = marché du travail plus tendu."),
    "youth_unemployment_pct": ("Unemployment rate among young people (15-24).", "Lower = better youth job prospects.",
                               "Taux de chômage des jeunes (15-24 ans).", "Plus faible = meilleures perspectives d'emploi des jeunes."),
    "labor_force_participation_pct": ("Share of working-age people in the labor force.", "Higher = more of the population economically active.",
                                      "Part des personnes en âge de travailler sur le marché du travail.", "Plus élevé = plus de population économiquement active."),
    "urban_population_pct": ("Share of the population living in urban areas.", "Higher = more urbanized society.",
                             "Part de la population vivant en zone urbaine.", "Plus élevé = société plus urbanisée."),
    "basic_sanitation_access_pct": ("Share of people with access to basic sanitation.", "Higher = better public health infrastructure.",
                                    "Part de la population ayant accès à un assainissement de base.", "Plus élevé = meilleures infrastructures de santé publique."),
    "health_expenditure_per_capita": ("Health spending per person (USD).", "Higher = more resources devoted to health.",
                                      "Dépenses de santé par habitant (USD).", "Plus élevé = plus de ressources consacrées à la santé."),
    "education_expenditure_pct_gdp": ("Public education spending as a share of GDP.", "Higher = greater investment in education.",
                                      "Dépenses publiques d'éducation rapportées au PIB.", "Plus élevé = investissement plus fort dans l'éducation."),
    "population_mn": ("Total population (millions).", "Size of the population.",
                      "Population totale (millions).", "Taille de la population."),
    "internet_users_pct": ("Share of the population using the Internet.", "Higher = greater digital inclusion.",
                           "Part de la population utilisant Internet.", "Plus élevé = meilleure inclusion numérique."),
    "mobile_subscriptions_per_100": ("Mobile cellular subscriptions per 100 people.", "Can exceed 100 (multiple SIMs per person).",
                                     "Abonnements mobiles pour 100 habitants.", "Peut dépasser 100 (plusieurs SIM par personne)."),
    "fixed_broadband_per_100": ("Fixed broadband subscriptions per 100 people.", "Higher = better fixed connectivity.",
                                "Abonnements internet fixe pour 100 habitants.", "Plus élevé = meilleure connectivité fixe."),
    "bank_account_ownership_pct": ("Share of adults (15+) with a bank or mobile-money account (Global Findex).",
                                   "Higher = greater financial inclusion. Data only every 3 years.",
                                   "Part des adultes (15 ans+) ayant un compte bancaire ou mobile (Global Findex).",
                                   "Plus élevé = meilleure inclusion financière. Données tous les 3 ans seulement."),
    "high_tech_exports_pct": ("High-technology exports as a share of manufactured exports.", "Higher = more advanced export structure.",
                              "Exportations de haute technologie rapportées aux exportations manufacturières.", "Plus élevé = structure exportatrice plus avancée."),
    "rd_expenditure_pct_gdp": ("Research & development spending as a share of GDP.", "Higher = stronger innovation effort.",
                               "Dépenses de recherche-développement rapportées au PIB.", "Plus élevé = effort d'innovation plus intense."),
    "researchers_per_million": ("Number of researchers in R&D per million people.", "Higher = greater scientific capacity.",
                                "Nombre de chercheurs en R&D par million d'habitants.", "Plus élevé = capacité scientifique plus forte."),
    "pm25_air_pollution": ("Mean annual exposure to fine PM2.5 particles (µg/m³).", "WHO guideline ≈ 5 µg/m³; higher = worse air quality.",
                           "Exposition annuelle moyenne aux particules fines PM2,5 (µg/m³).", "Seuil OMS ≈ 5 µg/m³ ; plus élevé = moins bonne qualité de l'air."),
    "electricity_access_pct": ("Share of the population with access to electricity.", "Higher = better energy access.",
                               "Part de la population ayant accès à l'électricité.", "Plus élevé = meilleur accès à l'énergie."),
    "electric_power_losses_pct": ("Electricity lost in transmission & distribution (%).", "Lower = more efficient grid.",
                                  "Pertes électriques en transport et distribution (%).", "Plus faible = réseau plus efficace."),
    "cereal_yield_kg_per_ha": ("Cereal production per hectare (kg).", "Higher = more productive agriculture.",
                               "Production céréalière par hectare (kg).", "Plus élevé = agriculture plus productive."),
    "govt_effectiveness_index": ("Quality of public services & policy implementation (WGI, -2.5 to +2.5).", "Higher = more effective government.",
                                 "Qualité des services publics et de la mise en œuvre des politiques (WGI, -2,5 à +2,5).", "Plus élevé = État plus efficace."),
    "political_stability_index": ("Likelihood of political instability/violence (WGI, -2.5 to +2.5).", "Higher = more stable.",
                                  "Probabilité d'instabilité politique/violence (WGI, -2,5 à +2,5).", "Plus élevé = plus stable."),
    "rule_of_law_index": ("Confidence in rules, contracts & courts (WGI, -2.5 to +2.5).", "Higher = stronger rule of law.",
                          "Confiance dans les règles, contrats et tribunaux (WGI, -2,5 à +2,5).", "Plus élevé = État de droit plus solide."),
    "control_of_corruption": ("Extent to which public power is exercised for private gain (WGI, -2.5 to +2.5).", "Higher = less corruption.",
                              "Mesure dans laquelle le pouvoir public est exercé à des fins privées (WGI, -2,5 à +2,5).", "Plus élevé = moins de corruption."),
    "corruption_perception_index": ("Transparency International CPI: perceived public-sector corruption (0-100).", "Higher = cleaner (less corruption).",
                                    "CPI de Transparency International : corruption perçue du secteur public (0-100).", "Plus élevé = plus propre (moins de corruption)."),
    "regulatory_quality": ("Ability of government to design sound policies & regulations (WGI).", "Higher = better regulatory framework.",
                           "Capacité du gouvernement à concevoir de bonnes politiques et réglementations (WGI).", "Plus élevé = meilleur cadre réglementaire."),
    "voice_accountability": ("Citizens' ability to participate & freedom of expression (WGI).", "Higher = more democratic accountability.",
                             "Capacité des citoyens à participer et liberté d'expression (WGI).", "Plus élevé = responsabilité démocratique plus forte."),
    "transparency_corruption_score": ("CPIA rating on transparency & accountability (1 = low to 6 = high; IDA countries only).", "Higher = better governance rating.",
                                      "Note CPIA sur la transparence et la responsabilité (1 = faible à 6 = élevé ; pays IDA uniquement).", "Plus élevé = meilleure note de gouvernance."),
    "women_parliament_pct": ("Share of parliamentary seats held by women.", "Higher = greater gender representation.",
                             "Part des sièges parlementaires occupés par des femmes.", "Plus élevé = meilleure représentation des genres."),
    "military_expenditure_pct_gdp": ("Military spending as a share of GDP.", "Context-dependent; high values may signal tension.",
                                     "Dépenses militaires rapportées au PIB.", "Dépend du contexte ; des valeurs élevées peuvent signaler des tensions."),
    "military_expenditure_pct_govt": ("Military spending as a share of total government budget.", "Higher share = larger military priority.",
                                      "Dépenses militaires rapportées au budget total de l'État.", "Part plus élevée = priorité militaire plus forte."),
}


def indicator_info(key: str, lang: str, field: str = "desc") -> str:
    """Return a bilingual static explanation ('desc' or 'tip') for an indicator."""
    entry = INDICATOR_INFO.get(key)
    if not entry:
        return ""
    en_desc, en_tip, fr_desc, fr_tip = entry
    if lang == "fr":
        return fr_desc if field == "desc" else fr_tip
    return en_desc if field == "desc" else en_tip


def interpret_value(key: str, value, world_median, lang: str) -> str:
    """Return a short, DYNAMIC interpretation of a country's own value."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    fr = (lang == "fr")
    if key == "cpi_index_raw":
        delta = value - 100
        return (f"Prix {delta:+.0f} % vs 2010 (100 = niveau 2010)" if fr
                else f"Prices {delta:+.0f}% vs 2010 (100 = 2010 level)")
    if key == "hdi":
        cat = (("très élevé", "very high") if value >= 0.8 else
               ("élevé", "high") if value >= 0.7 else
               ("moyen", "medium") if value >= 0.55 else ("faible", "low"))
        return f"IDH {cat[0]}" if fr else f"HDI: {cat[1]}"
    if key in {"govt_effectiveness_index", "political_stability_index", "rule_of_law_index",
               "control_of_corruption", "regulatory_quality", "voice_accountability"}:
        cat = (("gouvernance forte", "strong governance") if value >= 1.0 else
               ("gouvernance moyenne", "moderate governance") if value >= 0 else
               ("gouvernance faible", "weak governance") if value >= -1.0 else
               ("gouvernance très faible", "very weak governance"))
        return cat[0] if fr else cat[1]
    if key == "corruption_perception_index":
        cat = (("très peu corrompu", "very clean") if value >= 75 else
               ("peu corrompu", "relatively clean") if value >= 50 else
               ("corruption élevée", "high corruption") if value >= 25 else
               ("corruption très élevée", "very high corruption"))
        return cat[0] if fr else cat[1]
    if key == "gini_index":
        cat = (("très inégalitaire", "very unequal") if value >= 45 else
               ("inégalitaire", "unequal") if value >= 35 else
               ("relativement égalitaire", "relatively equal"))
        return cat[0] if fr else cat[1]
    if world_median is None or (isinstance(world_median, float) and np.isnan(world_median)):
        return ""
    above_is_worse = key in INVERSE_INDICATORS
    if value > world_median:
        return ("au-dessus de la médiane mondiale (défavorable)" if fr and above_is_worse
                else "au-dessus de la médiane mondiale (favorable)" if fr
                else "above world median (unfavorable)" if above_is_worse
                else "above world median (favorable)")
    if value < world_median:
        return ("en dessous de la médiane mondiale (favorable)" if fr and above_is_worse
                else "en dessous de la médiane mondiale (défavorable)" if fr
                else "below world median (favorable)" if above_is_worse
                else "below world median (unfavorable)")
    return "≈ médiane mondiale" if fr else "≈ world median"


def show_indicator_info(key: str, lang: str) -> None:
    """Display a dynamic explanation panel for the selected indicator."""
    desc = indicator_info(key, lang, "desc")
    tip = indicator_info(key, lang, "tip")
    if not desc:
        return
    content = f"ℹ️ {desc}" + (f" &nbsp;·&nbsp; 📌 {tip}" if tip else "")
    st.markdown(f'<div class="indicator-banner">{content}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# COUNTRY NAME TRANSLATION (deterministic ISO3 -> FR; bypasses translations.py)
# ═══════════════════════════════════════════════════════════════════════════
ISO3_TO_FR = {
    "AFG": "Afghanistan", "ALB": "Albanie", "DZA": "Algérie", "ASM": "Samoa américaines",
    "AND": "Andorre", "AGO": "Angola", "AIA": "Anguilla", "ATG": "Antigua-et-Barbuda",
    "ARG": "Argentine", "ARM": "Arménie", "ABW": "Aruba", "AUS": "Australie", "AUT": "Autriche",
    "AZE": "Azerbaïdjan", "BHS": "Bahamas", "BHR": "Bahreïn", "BGD": "Bangladesh",
    "BRB": "Barbade", "BLR": "Bélarus", "BEL": "Belgique", "BLZ": "Belize", "BEN": "Bénin",
    "BMU": "Bermudes", "BTN": "Bhoutan", "BOL": "Bolivie", "BIH": "Bosnie-Herzégovine",
    "BWA": "Botswana", "BRA": "Brésil", "VGB": "Îles Vierges britanniques",
    "BRN": "Brunéi Darussalam", "BGR": "Bulgarie", "BFA": "Burkina Faso", "BDI": "Burundi",
    "CPV": "Cabo Verde", "KHM": "Cambodge", "CMR": "Cameroun", "CAN": "Canada",
    "CYM": "Îles Caïmans", "CAF": "République centrafricaine", "TCD": "Tchad", "CHL": "Chili",
    "CHI": "Îles Anglo-Normandes", "CHN": "Chine", "COL": "Colombie", "COM": "Comores",
    "COD": "Congo (Rép. dém.)", "COG": "Congo (Rép.)", "CRI": "Costa Rica",
    "CIV": "Côte d'Ivoire", "HRV": "Croatie", "CUB": "Cuba", "CUW": "Curaçao", "CYP": "Chypre",
    "CZE": "Tchéquie", "DNK": "Danemark", "DJI": "Djibouti", "DMA": "Dominique",
    "DOM": "République dominicaine", "ECU": "Équateur", "EGY": "Égypte", "SLV": "El Salvador",
    "GNQ": "Guinée équatoriale", "ERI": "Érythrée", "EST": "Estonie", "SWZ": "Eswatini",
    "ETH": "Éthiopie", "FRO": "Îles Féroé", "FJI": "Fidji", "FIN": "Finlande", "FRA": "France",
    "GUF": "Guyane", "PYF": "Polynésie française", "GAB": "Gabon", "GMB": "Gambie",
    "GEO": "Géorgie", "DEU": "Allemagne", "GHA": "Ghana", "GRC": "Grèce", "GRL": "Groenland",
    "GRD": "Grenade", "GUM": "Guam", "GTM": "Guatemala", "GIN": "Guinée",
    "GNB": "Guinée-Bissau", "GUY": "Guyana", "HTI": "Haïti", "HND": "Honduras",
    "HKG": "Hong Kong", "HUN": "Hongrie", "ISL": "Islande", "IND": "Inde", "IDN": "Indonésie",
    "IRN": "Iran", "IRQ": "Iraq", "IRL": "Irlande", "IMN": "Île de Man", "ISR": "Israël",
    "ITA": "Italie", "JAM": "Jamaïque", "JPN": "Japon", "JOR": "Jordanie", "KAZ": "Kazakhstan",
    "KEN": "Kenya", "KIR": "Kiribati", "PRK": "Corée du Nord", "KOR": "Corée du Sud",
    "XKX": "Kosovo", "KSV": "Kosovo", "KWT": "Koweït", "KGZ": "Kirghizistan", "LAO": "Laos",
    "LVA": "Lettonie", "LBN": "Liban", "LSO": "Lesotho", "LBR": "Libéria", "LBY": "Libye",
    "LIE": "Liechtenstein", "LTU": "Lituanie", "LUX": "Luxembourg", "MAC": "Macao",
    "MDG": "Madagascar", "MWI": "Malawi", "MYS": "Malaisie", "MDV": "Maldives", "MLI": "Mali",
    "MLT": "Malte", "MHL": "Îles Marshall", "MRT": "Mauritanie", "MUS": "Maurice", "MEX": "Mexique",
    "FSM": "Micronésie", "MDA": "Moldavie", "MCO": "Monaco", "MNG": "Mongolie",
    "MNE": "Monténégro", "MAR": "Maroc", "MOZ": "Mozambique", "MMR": "Myanmar", "NAM": "Namibie",
    "NRU": "Nauru", "NPL": "Népal", "NLD": "Pays-Bas", "NCL": "Nouvelle-Calédonie",
    "NZL": "Nouvelle-Zélande", "NIC": "Nicaragua", "NER": "Niger", "NGA": "Nigéria",
    "MKD": "Macédoine du Nord", "MNP": "Îles Mariannes du Nord", "NOR": "Norvège", "OMN": "Oman",
    "PAK": "Pakistan", "PLW": "Palaos", "PSE": "Palestine", "PAN": "Panama",
    "PNG": "Papouasie-Nouvelle-Guinée", "PRY": "Paraguay", "PER": "Pérou", "PHL": "Philippines",
    "POL": "Pologne", "PRT": "Portugal", "PRI": "Porto Rico", "QAT": "Qatar", "ROU": "Roumanie",
    "RUS": "Russie", "RWA": "Rwanda", "WSM": "Samoa", "SMR": "Saint-Marin",
    "STP": "Sao Tomé-et-Principe", "SAU": "Arabie saoudite", "SEN": "Sénégal", "SRB": "Serbie",
    "SYC": "Seychelles", "SLE": "Sierra Leone", "SGP": "Singapour",
    "SXM": "Saint-Martin (partie néerlandaise)", "SVK": "Slovaquie", "SVN": "Slovénie",
    "SLB": "Îles Salomon", "SOM": "Somalie", "ZAF": "Afrique du Sud", "SSD": "Soudan du Sud",
    "ESP": "Espagne", "LKA": "Sri Lanka", "KNA": "Saint-Kitts-et-Nevis", "LCA": "Sainte-Lucie",
    "MAF": "Saint-Martin (partie française)", "VCT": "Saint-Vincent-et-les-Grenadines",
    "SDN": "Soudan", "SUR": "Suriname", "SWE": "Suède", "CHE": "Suisse", "SYR": "Syrie",
    "TWN": "Taïwan", "TJK": "Tadjikistan", "TZA": "Tanzanie", "THA": "Thaïlande",
    "TLS": "Timor oriental", "TGO": "Togo", "TON": "Tonga", "TTO": "Trinité-et-Tobago",
    "TUN": "Tunisie", "TUR": "Türkiye", "TKM": "Turkménistan",
    "TCA": "Îles Turques-et-Caïques", "TUV": "Tuvalu", "UGA": "Ouganda", "UKR": "Ukraine",
    "ARE": "Émirats arabes unis", "GBR": "Royaume-Uni", "USA": "États-Unis", "URY": "Uruguay",
    "UZB": "Ouzbékistan", "VUT": "Vanuatu", "VEN": "Venezuela", "VNM": "Viet Nam",
    "VIR": "Îles Vierges américaines", "PSS": "Cisjordanie et Gaza", "YEM": "Yémen",
    "ZMB": "Zambie", "ZWE": "Zimbabwe",
}


def _fr_country_name(iso3):
    """French country name from an ISO3 code, or None."""
    if not iso3:
        return None
    iso3 = str(iso3).strip().upper()
    if iso3 in ISO3_TO_FR:
        return ISO3_TO_FR[iso3]
    if _HAS_PYCOUNTRY:
        try:
            c = pycountry.countries.get(alpha_3=iso3)
            if c is not None:
                return c.translations.get("fr")
        except Exception:
            pass
    return None


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load and normalize the aggregated dataset."""
    data_path = os.path.join("data", "world_economic.csv")
    if not os.path.exists(data_path):
        st.error(f"Dataset not found at `{data_path}`. Please run `data/fetch_data.py` first.")
        st.stop()
    df = pd.read_csv(data_path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    text_cols = ["iso3", "country", "region", "income_group", "capital"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})
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


def _en_label(key: str) -> str:
    """Stable English label used to order indicators deterministically."""
    return TRANSLATIONS.get("en", {}).get(key, key.replace("_", " ").title())


def ind_label(key: str, current_lang: str, with_pillar: bool = False) -> str:
    """Return a human-readable label for an indicator key."""
    label = t(key, current_lang)
    if label == key:
        label = key.replace("_", " ").title()
    if with_pillar:
        pillar = INDICATOR_TO_PILLAR.get(key)
        if pillar:
            return f"{t(PESTEL_LABEL_KEYS[pillar], current_lang)} — {label}"
    return label


def previous_year(years: list, current: int) -> int:
    """Return the most recent available year strictly before `current`."""
    earlier = [y for y in years if y < current]
    return max(earlier) if earlier else current


def safe_delta(current, previous):
    """Return current - previous only when both values are valid."""
    if pd.notna(current) and pd.notna(previous):
        return float(current) - float(previous)
    return None


def get_pestel_scores(df_target: pd.DataFrame, df_world: pd.DataFrame, year: int) -> dict:
    """Compute normalized PESTEL scores (0-100) for a target entity."""
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


# ═══════════════════════════════════════════════════════════════════════════
# LOAD DATA + COUNTRY NAME LOOKUP
# ═══════════════════════════════════════════════════════════════════════════
df_all = load_data()
df_all["country_fr"] = df_all["iso3"].map(_fr_country_name)
COUNTRY_NAME_TO_FR = {
    name: fr for name, fr in zip(df_all["country"], df_all["country_fr"]) if pd.notna(fr)
}


def cname(name, lang):
    """Country display name for the current language (deterministic ISO3 map)."""
    if lang != "fr":
        return name
    return COUNTRY_NAME_TO_FR.get(name, name)


INDICATOR_KEYS = [
    ind for pillar in PESTEL_PILLAR_ORDER
    for ind in sorted(PESTEL_INDICATORS[pillar], key=_en_label)
    if ind in df_all.columns
]
ALL_REGIONS = sorted(df_all["region"].dropna().unique()) if "region" in df_all.columns else []
ALL_COUNTRIES = sorted(df_all["country"].dropna().unique())
YEAR_MIN = int(df_all["year"].min())
YEAR_MAX = int(df_all["year"].max())
ALL_YEARS = sorted(df_all["year"].unique())


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Control Center
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    lang = st.radio("🌐 Language / Langue", ["EN", "FR"], horizontal=True, index=0,
                    key="lang_choice").lower()
    st.radio("🎨 Theme / Thème", ["☀️", "🌙"], horizontal=True, index=0,
             key="theme_choice", label_visibility="collapsed")

    st.markdown(f"## {t('sidebar_title', lang)}")
    st.caption(t("sidebar_caption", lang, n=df_all["country"].nunique(), ymin=YEAR_MIN, ymax=YEAR_MAX))
    st.divider()

    default_years = [y for y in ALL_YEARS if y >= 2010]
    sel_years = st.multiselect(t("years_label", lang), ALL_YEARS, default=default_years)
    if not sel_years:
        sel_years = ALL_YEARS
        st.warning(t("no_year_selected", lang))
    st.divider()

    sel_regions = st.multiselect(t("regions", lang), ALL_REGIONS, default=ALL_REGIONS,
                                 format_func=lambda x: t(x, lang))
    sel_income = st.multiselect(t("income_levels", lang), INCOME_ORDER, default=INCOME_ORDER,
                                format_func=lambda x: t(x, lang))
    st.divider()

    if st.button(t("refresh_btn", lang), width="stretch"):
        with st.spinner(t("refreshing", lang)):
            try:
                res = subprocess.run([sys.executable, os.path.join("data", "fetch_data.py")],
                                     capture_output=True, text=True, timeout=600)
                if res.returncode == 0:
                    st.cache_data.clear()
                    st.success(t("refresh_ok", lang))
                    st.rerun()
                else:
                    st.error(t("refresh_err", lang, e=res.stderr[:300]))
            except Exception as e:
                st.error(t("refresh_conn", lang, e=str(e)))
    st.divider()
    st.caption(t("source", lang))


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL FILTERS
# ═══════════════════════════════════════════════════════════════════════════
mask = (
    df_all["year"].isin(sel_years)
    & df_all["region"].isin(sel_regions)
    & df_all["income_group"].isin(sel_income)
)
df = df_all[mask].copy()

latest_year = int(df["year"].max()) if not df.empty else max(sel_years)
df_latest = df[df["year"] == latest_year]
prev_year = previous_year(sorted(sel_years), latest_year)
df_prev = df[df["year"] == prev_year]


# ═══════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"## {t('app_title', lang).upper()}")
st.caption(t("app_caption", lang, n=df["country"].nunique(), y0=min(sel_years), y1=max(sel_years), ly=latest_year))
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL KPIs
# ═══════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4, k5 = st.columns(5)
med_gdp = df_latest["gdp_per_capita"].median() if "gdp_per_capita" in df_latest else None
med_gdp_p = df_prev["gdp_per_capita"].median() if "gdp_per_capita" in df_prev else None
med_inf = df_latest["inflation"].median() if "inflation" in df_latest else None
med_inf_p = df_prev["inflation"].median() if "inflation" in df_prev else None
med_debt = df_latest["debt_pct_gdp"].median() if "debt_pct_gdp" in df_latest else None
med_debt_p = df_prev["debt_pct_gdp"].median() if "debt_pct_gdp" in df_prev else None
d_gdp = safe_delta(med_gdp, med_gdp_p)
d_inf = safe_delta(med_inf, med_inf_p)
d_debt = safe_delta(med_debt, med_debt_p)

k1.metric(ind_label("gdp_per_capita", lang), f"${med_gdp:,.0f}" if pd.notna(med_gdp) else "N/A",
          f"{d_gdp:+,.0f}" if d_gdp is not None else "")
k2.metric(ind_label("inflation", lang), f"{med_inf:.1f}%" if pd.notna(med_inf) else "N/A",
          f"{d_inf:+.1f} pp" if d_inf is not None else "", delta_color="inverse")
k3.metric(ind_label("debt_pct_gdp", lang), f"{med_debt:.1f}%" if pd.notna(med_debt) else "N/A",
          f"{d_debt:+.1f} pp" if d_debt is not None else "", delta_color="inverse")

hi_countries = sorted(df_latest.loc[df_latest["income_group"] == "High income", "country"].dropna().unique())
lo_countries = sorted(df_latest.loc[df_latest["income_group"] == "Low income", "country"].dropna().unique())

k4.metric(
    t("kpi_hi", lang),
    str(len(hi_countries)),
    help=" · ".join(cname(c, lang) for c in hi_countries),
)
k5.metric(
    t("kpi_lo", lang),
    str(len(lo_countries)),
    help=" · ".join(cname(c, lang) for c in lo_countries),
)
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════
tab_map, tab_trend, tab_country, tab_compare, tab_struct, tab_data = st.tabs([
    t("tab_map", lang), t("tab_trend", lang), t("tab_country", lang),
    t("tab_compare", lang), t("tab_struct", lang), t("tab_data", lang),
])


# ── TAB 1: WORLD MAP ──────────────────────────────────────────────────────
with tab_map:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        map_ind = st.selectbox(t("map_indicator", lang), INDICATOR_KEYS,
                               format_func=lambda x: ind_label(x, lang, with_pillar=True), key="map_ind")
    with c2:
        map_type = st.radio(t("map_type", lang), ["choropleth", "bubble"],
                            format_func=lambda x: t(x, lang), horizontal=True)
    with c3:
        map_year = st.selectbox(t("ref_year", lang), sorted(sel_years, reverse=True), index=0, key="map_yr")

    show_indicator_info(map_ind, lang)

    size_choice_key = None
    if map_type == "bubble":
        size_options = [map_ind]
        if "population_mn" in df.columns and map_ind != "population_mn":
            size_options.append("population_mn")
        size_choice_key = st.radio(t("bubble_size_label", lang), size_options,
                                   format_func=lambda x: ind_label(x, lang), index=0, horizontal=True)

    df_map = df[df["year"] == map_year].dropna(subset=[map_ind]).copy()
    ilabel = ind_label(map_ind, lang)
    cscale = get_expressive_colorscale(map_ind)
    df_map["_cname"] = df_map["country"].map(lambda n: cname(n, lang))
    world_median_map = (df_all[df_all["year"] == map_year][map_ind].median()
                        if map_ind in df_all.columns else None)
    df_map["_interpret"] = df_map[map_ind].apply(
        lambda v: interpret_value(map_ind, v, world_median_map, lang))

    if map_type == "choropleth":
        zmin, zmax = None, None
        if not df_map.empty and df_map[map_ind].nunique() > 1:
            zmin = float(np.percentile(df_map[map_ind], 2))
            zmax = float(np.percentile(df_map[map_ind], 98))
            if zmax <= zmin:
                zmin, zmax = None, None
        fig_map = go.Figure(go.Choropleth(
            locations=df_map["iso3"], z=df_map[map_ind], text=df_map["_cname"],
            customdata=df_map[[map_ind, "region", "income_group", "_interpret"]].values,
            zmin=zmin, zmax=zmax,
            hovertemplate=("<b>%{text}</b><br>"
                           + f"{ilabel}: %{{customdata[0]:,.2f}}<br>"
                           + "<b>%{customdata[3]}</b><br>"
                           + f"{t('region', lang)}: %{{customdata[1]}}<br>"
                           + f"{t('income_level', lang)}: %{{customdata[2]}}<br><extra></extra>"),
            colorscale=cscale,
            colorbar=dict(title=ilabel, len=0.6, thickness=15, tickfont=dict(size=10)),
            marker_line_color="#78909c", marker_line_width=0.6,
        ))
        fig_map.update_layout(
            title=dict(text=f"{ilabel} — {map_year}", font=dict(size=15)),
            geo=dict(**GEO_STYLE, projection_type="natural earth"),
            margin=dict(t=50, b=0, l=0, r=0), height=520,
        )
    else:
        size_col = size_choice_key if size_choice_key else map_ind
        df_map["_size"] = df_map[size_col].fillna(0).clip(lower=0)
        fig_map = go.Figure()
        for ig in INCOME_ORDER:
            sub = df_map[df_map["income_group"] == ig]
            if sub.empty or sub["_size"].max() <= 0:
                continue
            fig_map.add_trace(go.Scattergeo(
                locations=sub["iso3"],
                marker=dict(size=sub["_size"], sizemode="area",
                            sizeref=2. * sub["_size"].max() / (42 ** 2), sizemin=4,
                            color=INCOME_COLORS[ig], opacity=0.85,
                            line=dict(color="white", width=0.5)),
                text=sub["_cname"],
                customdata=sub[[map_ind, "region", size_col, "_interpret"]].values,
                hovertemplate=("<b>%{text}</b><br>"
                               + f"{ilabel}: %{{customdata[0]:,.2f}}<br>"
                               + "<b>%{customdata[3]}</b><br>"
                               + f"{t('region', lang)}: %{{customdata[1]}}<br>"
                               + f"{ind_label(size_col, lang)}: %{{customdata[2]:,.2f}}<br><extra></extra>"),
                name=t(ig, lang),
            ))
        fig_map.update_layout(
            title=dict(text=f"{ilabel} — {map_year}", font=dict(size=15)),
            geo=dict(**GEO_STYLE, projection_type="natural earth"),
            margin=dict(t=50, b=0, l=0, r=0), height=520,
            legend=dict(orientation="h", y=-0.1, font_size=11),
        )
    st.plotly_chart(fig_map, width="stretch")

    st.markdown(t("median_by_region", lang, ind=ilabel, y=map_year))
    if not df_map.empty and "region" in df_map.columns:
        reg_med = df_map.groupby("region")[map_ind].median().round(2).sort_values(ascending=False).reset_index()
        cols_r = st.columns(min(len(reg_med), 7))
        for i, row in reg_med.iterrows():
            if i < len(cols_r):
                cols_r[i].metric(t(row["region"], lang), f"{row[map_ind]:,.1f}")


# ── TAB 2: TRENDS ─────────────────────────────────────────────────────────
with tab_trend:
    t1, t2 = st.columns([2, 1])
    with t1:
        trend_ind = st.selectbox(t("indicator", lang), INDICATOR_KEYS,
                                 format_func=lambda x: ind_label(x, lang, with_pillar=True), key="tr_ind")
    with t2:
        group_col = st.radio(t("group_by", lang), ["income_group", "region"],
                             format_func=lambda x: t("income_level" if x == "income_group" else "region", lang),
                             horizontal=True)
    show_indicator_info(trend_ind, lang)

    group_label_key = "income_level" if group_col == "income_group" else "region"
    color_map_ = INCOME_COLORS if group_col == "income_group" else REGION_COLORS
    cat_order_ = INCOME_ORDER if group_col == "income_group" else ALL_REGIONS
    df_tr = df.groupby(["year", group_col])[trend_ind].median().reset_index().rename(columns={trend_ind: "value"})
    df_tr["group_label"] = df_tr[group_col].map(lambda x: t(x, lang))
    display_color_map = {t(k, lang): v for k, v in color_map_.items()}
    display_order = [t(x, lang) for x in cat_order_]
    fig_tr = px.line(
        df_tr, x="year", y="value", color="group_label",
        color_discrete_map=display_color_map, category_orders={"group_label": display_order}, markers=True,
        labels={"year": t("year_label", lang), "value": ind_label(trend_ind, lang), "group_label": ""},
        title=t("trend_title", lang, ind=ind_label(trend_ind, lang),
                grp=t(group_label_key, lang).lower(), y0=min(sel_years), y1=max(sel_years)),
    )
    fig_tr.update_traces(line_width=2.5, marker_size=5)
    fig_tr.update_layout(margin=dict(t=50, b=20, l=10, r=10), hovermode="x unified",
                         legend=dict(orientation="h", y=-0.3, font_size=11), height=420)
    for event_year, label_key in [(2008, "ev_2008"), (2020, "ev_2020"), (2022, "ev_2022")]:
        if min(sel_years) <= event_year <= max(sel_years):
            fig_tr.add_vline(x=event_year, line_dash="dot", line_color="#94a3b8", line_width=1)
            fig_tr.add_annotation(x=event_year, y=1, yref="paper",
                                  text=t(label_key, lang).replace("\n", "<br>"),
                                  showarrow=False, yanchor="top", font=dict(size=10, color="#64748b"))
    st.plotly_chart(fig_tr, width="stretch")

    st.markdown("---")
    st.markdown(f"**📌 {t('scatter_title', lang)}**")
    s1, s2, s3 = st.columns(3)
    with s1:
        x_ind = st.selectbox(t("x_axis", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang), index=0, key="sx")
    with s2:
        y_ind = st.selectbox(t("y_axis", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang),
                             index=min(2, len(INDICATOR_KEYS) - 1), key="sy")
    with s3:
        sc_yr = st.selectbox(t("year_label", lang), sorted(sel_years, reverse=True), index=0, key="syr")
    df_sc = df[df["year"] == sc_yr].dropna(subset=[x_ind, y_ind]).copy()
    size_col = "gdp_total_bn" if "gdp_total_bn" in df_sc.columns else None
    if size_col:
        df_sc = df_sc.dropna(subset=[size_col])
    if not df_sc.empty:
        use_trendline = ("ols" if (len(df_sc) >= 3 and df_sc[x_ind].nunique() > 1
                                   and df_sc[y_ind].nunique() > 1) else None)
        df_sc["income_label"] = df_sc["income_group"].map(lambda x: t(x, lang))
        df_sc["_cname"] = df_sc["country"].map(lambda n: cname(n, lang))
        fig_sc = px.scatter(
            df_sc, x=x_ind, y=y_ind, color="income_label",
            color_discrete_map={t(k, lang): v for k, v in INCOME_COLORS.items()},
            category_orders={"income_label": [t(v, lang) for v in INCOME_ORDER]},
            size=size_col, size_max=45, hover_name="_cname", trendline=use_trendline,
            labels={x_ind: ind_label(x_ind, lang), y_ind: ind_label(y_ind, lang), "income_label": t("income_level", lang)},
            title=t("scatter_chart_title", lang, xi=ind_label(x_ind, lang), yi=ind_label(y_ind, lang), y=sc_yr),
        )
        fig_sc.update_layout(margin=dict(t=50, b=20, l=10, r=10), legend=dict(orientation="h", y=-0.25), height=430)
        st.plotly_chart(fig_sc, width="stretch")
    else:
        st.info(t("no_data", lang))


# ── TAB 3: COUNTRY PROFILE ────────────────────────────────────────────────
with tab_country:
    default_idx = ALL_COUNTRIES.index("Cameroon") if "Cameroon" in ALL_COUNTRIES else 0
    sel_country = st.selectbox(t("select_country", lang), ALL_COUNTRIES, index=default_idx,
                               key="cp_country", format_func=lambda n: cname(n, lang))
    df_c = df[df["country"] == sel_country].sort_values("year")
    if df_c.empty:
        st.warning(t("no_data", lang))
    else:
        meta_row = df_c.dropna(subset=["latitude", "longitude"]).head(1)
        lat = float(meta_row["latitude"].iloc[0]) if not meta_row.empty else 0.0
        lon = float(meta_row["longitude"].iloc[0]) if not meta_row.empty else 0.0
        income_grp = str(df_c["income_group"].iloc[-1])
        region_val = str(df_c["region"].iloc[-1])
        years_c = sorted(df_c["year"].unique())
        latest_year_c = years_c[-1]
        prev_year_c = previous_year(years_c, latest_year_c)
        latest_c = df_c[df_c["year"] == latest_year_c].iloc[0]
        prev_c = df_c[df_c["year"] == prev_year_c].iloc[0]

        st.markdown(f"### 🏳️ {cname(sel_country, lang)}")
        ov1, ov2, ov3, ov4, ov5 = st.columns(5)
        ov1.metric(t("income_group_label", lang), t(income_grp, lang))
        ov2.metric(t("region_label", lang), t(region_val, lang))
        world_med = (df_all[df_all["year"] == latest_year_c]["gdp_per_capita"].median()
                     if "gdp_per_capita" in df_all.columns else None)
        gdp_val = latest_c.get("gdp_per_capita", None)
        gdp_delta = safe_delta(gdp_val, prev_c.get("gdp_per_capita", None))
        help_text = (f"{t('vs_world', lang)}: {gdp_val - world_med:+,.0f}"
                     if (world_med is not None and pd.notna(gdp_val) and pd.notna(world_med)) else "")
        ov3.metric(ind_label("gdp_per_capita", lang), f"${gdp_val:,.0f}" if pd.notna(gdp_val) else "N/A",
                   f"{gdp_delta:+,.0f}" if gdp_delta is not None else "", help=help_text)
        inf_val = latest_c.get("inflation", None)
        inf_delta = safe_delta(inf_val, prev_c.get("inflation", None))
        ov4.metric(ind_label("inflation", lang), f"{inf_val:.1f}%" if pd.notna(inf_val) else "N/A",
                   f"{inf_delta:+.1f} pp" if inf_delta is not None else "", delta_color="inverse")
        debt_val = latest_c.get("debt_pct_gdp", None)
        debt_delta = safe_delta(debt_val, prev_c.get("debt_pct_gdp", None))
        ov5.metric(ind_label("debt_pct_gdp", lang), f"{debt_val:.1f}%" if pd.notna(debt_val) else "N/A",
                   f"{debt_delta:+.1f} pp" if debt_delta is not None else "", delta_color="inverse")
        st.divider()

        map_col, donut_col = st.columns([1.5, 1])
        with map_col:
            geo_centered = dict(**GEO_STYLE, projection_type="natural earth",
                                center=dict(lon=lon, lat=lat), projection_scale=2.5)
            df_geo = df_all[df_all["year"] == int(latest_year_c)].copy()
            hl_color = INCOME_COLORS.get(income_grp, "#1D9E75")
            fig_geo = go.Figure()
            other = df_geo[df_geo["country"] != sel_country]
            fig_geo.add_trace(go.Choropleth(
                locations=other["iso3"], z=[0.5] * len(other),
                colorscale=[[0, "#cfd8dc"], [1, "#cfd8dc"]],
                showscale=False, marker_line_color="#90a4ae", marker_line_width=0.4, hoverinfo="skip"))
            sel_geo = df_geo[df_geo["country"] == sel_country]
            if not sel_geo.empty:
                fig_geo.add_trace(go.Choropleth(
                    locations=sel_geo["iso3"], z=[1],
                    colorscale=[[0, hl_color], [1, hl_color]],
                    showscale=False, marker_line_color="white", marker_line_width=2.5,
                    text=[cname(sel_country, lang)],
                    hovertemplate=(f"<b>{cname(sel_country, lang)}</b><br>"
                                   f"{t('income_group_label', lang)}: {t(income_grp, lang)}<extra></extra>")))
            fig_geo.update_layout(title=dict(text=t("country_map_title", lang, c=cname(sel_country, lang)), font=dict(size=13)),
                                  geo=geo_centered, margin=dict(t=45, b=0, l=0, r=0), height=320)
            st.plotly_chart(fig_geo, width="stretch")
        with donut_col:
            agr = latest_c.get("agriculture_pct", None)
            ind_ = latest_c.get("industry_pct", None)
            svc = latest_c.get("services_pct", None)
            if all(pd.notna(v) for v in [agr, ind_, svc]):
                fig_donut = go.Figure(go.Pie(
                    labels=[t("Agriculture", lang), t("Industry", lang), t("Services", lang)],
                    values=[agr, ind_, svc], hole=0.55,
                    marker_colors=[SECTOR_COLORS["Agriculture"], SECTOR_COLORS["Industry"], SECTOR_COLORS["Services"]],
                    textinfo="label+percent", hovertemplate="%{label}: %{value:.1f}%<extra></extra>"))
                fig_donut.update_layout(title=dict(text=t("sector_breakdown", lang, y=int(latest_year_c)), font=dict(size=13)),
                                        margin=dict(t=45, b=10, l=10, r=10),
                                        legend=dict(orientation="h", y=-0.2, font_size=11), height=320)
                st.plotly_chart(fig_donut, width="stretch")
        st.divider()

        st.markdown(f"#### 📊 {t('country_analytics_title', lang)}")
        col1, col2 = st.columns(2)
        with col1:
            year_radar = int(latest_year_c)
            world_med_df = df_all[df_all["year"] == year_radar]
            region_med_df = df_all[(df_all["year"] == year_radar) & (df_all["region"] == region_val)]
            country_scores = get_pestel_scores(df_c, df_all, year_radar)
            region_scores = get_pestel_scores(region_med_df, df_all, year_radar)
            world_scores = get_pestel_scores(world_med_df, df_all, year_radar)
            categories = [t(PESTEL_LABEL_KEYS[p], lang) for p in PESTEL_PILLAR_ORDER]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[country_scores[p] for p in PESTEL_PILLAR_ORDER],
                                                theta=categories, fill="toself", name=cname(sel_country, lang)))
            fig_radar.add_trace(go.Scatterpolar(r=[region_scores.get(p, 0) for p in PESTEL_PILLAR_ORDER],
                                                theta=categories, fill="toself", name=t("region_median", lang)))
            fig_radar.add_trace(go.Scatterpolar(r=[world_scores.get(p, 0) for p in PESTEL_PILLAR_ORDER],
                                                theta=categories, fill="toself", name=t("world_median", lang)))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True,
                                    title=dict(text=t("pestel_performance_radar", lang), font=dict(size=13)),
                                    margin=dict(l=40, r=40, t=60, b=40), height=380)
            st.plotly_chart(fig_radar, width="stretch")
        with col2:
            exports_val = latest_c.get("exports_pct_gdp", None)
            imports_val = latest_c.get("imports_pct_gdp", None)
            balance_val = latest_c.get("current_account_pct_gdp", None)
            if all(pd.notna(v) for v in [exports_val, imports_val, balance_val]):
                fig_wf = go.Figure(go.Waterfall(
                    name="Trade Balance", orientation="v", measure=["relative", "relative", "total"],
                    x=[t("exports", lang), t("imports", lang), t("current_account", lang)],
                    y=[exports_val, -imports_val, balance_val],
                    text=[f"+{exports_val:.1f}%", f"-{imports_val:.1f}%", f"{balance_val:.1f}%"],
                    textposition="outside", connector={"line": {"color": "rgb(100,116,139)"}}))
                fig_wf.update_layout(title=t("trade_balance_waterfall", lang), height=380,
                                     margin=dict(l=20, r=20, t=40, b=20), yaxis_title=t("pct_gdp", lang))
                st.plotly_chart(fig_wf, width="stretch")
            else:
                st.info(t("trade_data_unavailable", lang))

        col3, col4 = st.columns(2)
        with col3:
            df_s = df_c[["year", "agriculture_pct", "industry_pct", "services_pct"]].dropna()
            if not df_s.empty:
                df_s_melt = df_s.melt(id_vars="year", value_vars=["agriculture_pct", "industry_pct", "services_pct"],
                                      var_name="sector_key", value_name="value")
                df_s_melt["sector"] = df_s_melt["sector_key"].map(lambda k: t(SECTOR_LABEL_KEYS[k], lang))
                fig_area = px.area(
                    df_s_melt, x="year", y="value", color="sector", groupnorm="percent",
                    labels={"year": t("year_label", lang), "value": t("share_of_gdp", lang), "sector": t("sector", lang)},
                    title=t("sector_evolution_title", lang),
                    color_discrete_map={t("Agriculture", lang): SECTOR_COLORS["Agriculture"],
                                        t("Industry", lang): SECTOR_COLORS["Industry"],
                                        t("Services", lang): SECTOR_COLORS["Services"]})
                fig_area.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=-0.2))
                st.plotly_chart(fig_area, width="stretch")
            else:
                st.info(t("sector_data_unavailable", lang))
        with col4:
            indicators_hm = ["gdp_per_capita", "inflation", "debt_pct_gdp", "unemployment_pct",
                             "life_expectancy", "electricity_access_pct", "internet_users_pct", "pm25_air_pollution"]
            avail_hm = [i for i in indicators_hm if i in df_c.columns]
            if avail_hm and len(df_c) > 1:
                df_hm = df_c[["year"] + avail_hm].set_index("year").tail(10)
                df_norm = (df_hm - df_hm.min()) / (df_hm.max() - df_hm.min() + 1e-9)
                df_norm.columns = [ind_label(c, lang) for c in df_norm.columns]
                fig_hm = px.imshow(df_norm.T,
                                   labels=dict(x=t("year_label", lang), y=t("indicator", lang), color=t("normalized_score", lang)),
                                   title=t("indicator_trends_title", lang),
                                   color_continuous_scale="RdBu_r", aspect="auto", zmin=0, zmax=1)
                fig_hm.update_layout(height=380, margin=dict(l=60, r=20, t=50, b=20))
                st.plotly_chart(fig_hm, width="stretch")
            else:
                st.info(t("heatmap_unavailable", lang))

        if "gdp_per_capita" in df_c.columns and "inflation" in df_c.columns:
            fig_comb = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comb.add_trace(go.Scatter(x=df_c["year"], y=df_c["gdp_per_capita"],
                                          name=ind_label("gdp_per_capita", lang),
                                          line=dict(color="#0067C0", width=2)), secondary_y=False)
            fig_comb.add_trace(go.Scatter(x=df_c["year"], y=df_c["inflation"],
                                          name=ind_label("inflation", lang),
                                          line=dict(color="#d97706", width=2, dash="dot")), secondary_y=True)
            fig_comb.update_layout(title=t("gdp_inflation_title", lang), legend=dict(orientation="h", y=-0.2),
                                   margin=dict(t=40, b=20, l=10, r=10), height=300)
            fig_comb.update_yaxes(title_text=ind_label("gdp_per_capita", lang), secondary_y=False, showgrid=False)
            fig_comb.update_yaxes(title_text=ind_label("inflation", lang), secondary_y=True, showgrid=False)
            st.plotly_chart(fig_comb, width="stretch")

        MINI_SPECS = [
            ("unemployment_pct", "gauge", [0, 30], "#dc2626"),
            ("gdp_growth_pct", "delta", None, None),
            ("primary_completion_rate_pct", "gauge", [0, 100], "#0067C0"),
            ("life_expectancy", "gauge", [40, 90], "#059669"),
            ("internet_users_pct", "gauge", [0, 100], "#7c3aed"),
            ("electricity_access_pct", "gauge", [0, 100], "#d97706"),
        ]
        MINI_LABELS = {
            "unemployment_pct": ("Unemployment", "Chômage"),
            "gdp_growth_pct": ("GDP growth", "Croissance PIB"),
            "primary_completion_rate_pct": ("Primary completion", "Achèvement primaire"),
            "life_expectancy": ("Life expectancy", "Espérance de vie"),
            "internet_users_pct": ("Internet users", "Internet"),
            "electricity_access_pct": ("Electricity access", "Accès élec."),
        }
        mini_cols = st.columns(len(MINI_SPECS))
        for col, (key, mode, grange, gcolor) in zip(mini_cols, MINI_SPECS):
            val = latest_c.get(key, None)
            if not pd.notna(val):
                continue
            en_l, fr_l = MINI_LABELS.get(key, (key, key))
            label = fr_l if lang == "fr" else en_l
            with col:
                if mode == "gauge":
                    fig_mini = go.Figure(go.Indicator(
                        mode="number+gauge", value=val,
                        title={"text": label, "font": {"size": 9}},
                        domain={"x": [0, 1], "y": [0, 1]},
                        gauge={"axis": {"range": grange, "tickfont": {"size": 8}},
                               "bar": {"color": gcolor}, "borderwidth": 0},
                        number={"font": {"size": 15}, "valueformat": ".1f"}))
                else:
                    prev_val = prev_c.get(key, 0)
                    fig_mini = go.Figure(go.Indicator(
                        mode="number+delta", value=val,
                        title={"text": label, "font": {"size": 9}},
                        number={"font": {"size": 15}, "valueformat": ".1f"},
                        delta={"reference": prev_val if pd.notna(prev_val) else 0,
                               "valueformat": ".1f", "font": {"size": 10}}))
                fig_mini.update_layout(height=150, margin=dict(l=8, r=8, t=30, b=6))
                st.plotly_chart(fig_mini, width="stretch")


# ── TAB 4: COMPARE COUNTRIES ──────────────────────────────────────────────
with tab_compare:
    defaults = [c for c in ["Cameroon", "France", "China", "Nigeria", "Brazil",
                            "Germany", "India", "United States"] if c in ALL_COUNTRIES]
    sel_ctry = st.multiselect(t("select_countries", lang), ALL_COUNTRIES, default=defaults,
                              max_selections=12, format_func=lambda n: cname(n, lang))
    comp_ind = st.selectbox(t("indicator", lang), INDICATOR_KEYS,
                            format_func=lambda x: ind_label(x, lang, with_pillar=True), key="cp_ind")
    show_indicator_info(comp_ind, lang)
    if not sel_ctry:
        st.info(t("select_least_one", lang))
    else:
        df_cp = df[df["country"].isin(sel_ctry)].copy()
        df_cp["_cname"] = df_cp["country"].map(lambda n: cname(n, lang))
        fig_cp = px.line(df_cp, x="year", y=comp_ind, color="_cname",
                         color_discrete_sequence=px.colors.qualitative.Set2, markers=True,
                         labels={"year": t("year_label", lang), comp_ind: ind_label(comp_ind, lang), "_cname": ""},
                         title=f"{ind_label(comp_ind, lang)} — {min(sel_years)}–{max(sel_years)}")
        fig_cp.update_layout(margin=dict(t=50, b=20, l=10, r=10), hovermode="x unified",
                             legend=dict(orientation="h", y=-0.25), height=400)
        st.plotly_chart(fig_cp, width="stretch")
        latest_year_cp = int(df_cp["year"].max())
        prev_year_cp = previous_year(sorted(df_cp["year"].unique()), latest_year_cp)
        df_latest_cp = df_cp[df_cp["year"] == latest_year_cp].dropna(subset=[comp_ind])
        if not df_latest_cp.empty:
            ascending = comp_ind in INVERSE_INDICATORS
            df_rank = df_latest_cp.sort_values(comp_ind, ascending=ascending)
            fig_rank = px.bar(df_rank, x="_cname", y=comp_ind, color="_cname",
                              color_discrete_sequence=px.colors.qualitative.Set2,
                              labels={"_cname": t("col_country", lang), comp_ind: ind_label(comp_ind, lang)},
                              title=t("ranking_title", lang, ind=ind_label(comp_ind, lang), y=latest_year_cp))
            fig_rank.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10), height=400)
            st.plotly_chart(fig_rank, width="stretch")
            df_prev_cp = df_cp[df_cp["year"] == prev_year_cp][["country", comp_ind]]
            summary = df_latest_cp[["country", comp_ind]].merge(df_prev_cp, on="country", how="left", suffixes=("_cur", "_prev"))
            summary[t("delta", lang)] = summary[f"{comp_ind}_cur"] - summary[f"{comp_ind}_prev"]
            summary = summary.rename(columns={"country": t("col_country", lang), f"{comp_ind}_cur": ind_label(comp_ind, lang)})
            summary = summary[[t("col_country", lang), ind_label(comp_ind, lang), t("delta", lang)]]
            summary[t("col_country", lang)] = summary[t("col_country", lang)].map(lambda n: cname(n, lang))
            st.markdown(f"**{t('summary_table', lang, y=latest_year_cp)}**")
            st.dataframe(summary, width="stretch", hide_index=True)


# ── TAB 5: ECONOMIC STRUCTURE ─────────────────────────────────────────────
with tab_struct:
    c_left, c_right = st.columns(2)
    with c_left:
        sect_cols = [s for s in ["agriculture_pct", "industry_pct", "services_pct"] if s in df.columns]
        if sect_cols:
            df_tree = df[df["year"] == latest_year].groupby(["region", "income_group"])[sect_cols].median().round(1).reset_index()
            df_tree_m = df_tree.melt(id_vars=["region", "income_group"], value_vars=sect_cols, var_name="sector", value_name="pct")
            df_tree_m["sector"] = df_tree_m["sector"].map(lambda k: t(SECTOR_LABEL_KEYS[k], lang))
            df_tree_m["income_group"] = df_tree_m["income_group"].map(lambda x: t(x, lang))
            df_tree_m["region"] = df_tree_m["region"].map(lambda x: t(x, lang))
            fig_tree = px.treemap(df_tree_m, path=["region", "income_group", "sector"], values="pct", color="pct",
                                  color_continuous_scale="RdYlGn", title=t("treemap_title", lang, y=latest_year))
            fig_tree.update_layout(margin=dict(t=50, b=0, l=0, r=0), height=420)
            st.plotly_chart(fig_tree, width="stretch")
    with c_right:
        if "gdp_per_capita" in df.columns:
            df_vio = df[df["year"] == latest_year].dropna(subset=["gdp_per_capita"]).copy()
            df_vio = df_vio[df_vio["gdp_per_capita"] > 0]
            df_vio["income_label"] = df_vio["income_group"].map(lambda x: t(x, lang))
            df_vio["_cname"] = df_vio["country"].map(lambda n: cname(n, lang))
            fig_vio = px.violin(df_vio, x="income_label", y="gdp_per_capita", color="income_label",
                                color_discrete_map={t(k, lang): v for k, v in INCOME_COLORS.items()},
                                category_orders={"income_label": [t(v, lang) for v in INCOME_ORDER]},
                                box=True, points="all", hover_name="_cname",
                                labels={"income_label": "", "gdp_per_capita": ind_label("gdp_per_capita", lang)},
                                title=t("violin_title", lang, y=latest_year))
            fig_vio.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10),
                                  yaxis_type="log", yaxis_title=t("gdp_log", lang), height=420)
            st.plotly_chart(fig_vio, width="stretch")

    st.markdown("---")
    rank_ind = st.selectbox(t("ranking_indicator", lang), INDICATOR_KEYS,
                            format_func=lambda x: ind_label(x, lang, with_pillar=True), key="rank_ind")
    show_indicator_info(rank_ind, lang)
    df_rank_struct = df[df["year"] == latest_year].dropna(subset=[rank_ind]).copy()
    if not df_rank_struct.empty:
        df_rank_struct["_cname"] = df_rank_struct["country"].map(lambda n: cname(n, lang))
        ascending = rank_ind in INVERSE_INDICATORS
        top10 = df_rank_struct.sort_values(rank_ind, ascending=ascending).head(10)
        bottom10 = df_rank_struct.sort_values(rank_ind, ascending=not ascending).head(10)
        r1, r2 = st.columns(2)
        with r1:
            fig_top = px.bar(top10, x="_cname", y=rank_ind, color="_cname",
                             color_discrete_sequence=px.colors.qualitative.Set2,
                             labels={"_cname": "", rank_ind: ind_label(rank_ind, lang)},
                             title=t("top10", lang, ind=ind_label(rank_ind, lang), y=latest_year))
            fig_top.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10), height=380)
            st.plotly_chart(fig_top, width="stretch")
        with r2:
            fig_bot = px.bar(bottom10, x="_cname", y=rank_ind, color="_cname",
                             color_discrete_sequence=px.colors.qualitative.Pastel1,
                             labels={"_cname": "", rank_ind: ind_label(rank_ind, lang)},
                             title=t("bottom10", lang, ind=ind_label(rank_ind, lang), y=latest_year))
            fig_bot.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10), height=380)
            st.plotly_chart(fig_bot, width="stretch")


# ── TAB 6: DATA EXPLORER ──────────────────────────────────────────────────
with tab_data:
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        search = st.text_input(t("search_country", lang), "")
    with d2:
        filter_reg = st.multiselect(t("filter_region", lang), ALL_REGIONS, default=[], key="dt_reg",
                                    format_func=lambda x: t(x, lang))
    with d3:
        data_year = st.selectbox(t("year_label", lang), sorted(sel_years, reverse=True), index=0, key="dt_yr")
    with d4:
        pestel_options = ["all"] + PESTEL_PILLAR_ORDER
        pestel_choice = st.selectbox(t("pestel_pillar_label", lang), pestel_options,
                                     format_func=lambda x: t("pestel_all", lang) if x == "all"
                                     else t(PESTEL_LABEL_KEYS[x], lang), index=0)
    df_view = df[df["year"] == data_year].copy()
    if search:
        df_view = df_view[df_view["country"].str.contains(search, case=False, na=False)]
    if filter_reg:
        df_view = df_view[df_view["region"].isin(filter_reg)]
    if pestel_choice == "all":
        selected_keys = [k for k in INDICATOR_KEYS if k in df_view.columns]
    else:
        selected_keys = [k for k in PESTEL_INDICATORS[pestel_choice] if k in df_view.columns]

    display_cols = ["country", "region", "income_group"] + selected_keys
    label_mapping = {k: ind_label(k, lang) for k in INDICATOR_KEYS}
    label_mapping.update({"country": t("col_country", lang), "region": t("col_region", lang),
                          "income_group": t("income_level", lang)})
    df_display = df_view[display_cols].rename(columns=label_mapping).reset_index(drop=True)
    df_display.index += 1

    country_col = t("col_country", lang)
    if country_col in df_display.columns:
        df_display[country_col] = df_display[country_col].map(lambda n: cname(n, lang))
    region_col = t("col_region", lang)
    if region_col in df_display.columns:
        df_display[region_col] = df_display[region_col].map(lambda n: t(n, lang))
    income_col_label = t("income_level", lang)
    if income_col_label in df_display.columns:
        df_display[income_col_label] = df_display[income_col_label].map(lambda n: t(n, lang))

    st.caption(t("showing", lang, n=len(df_display), y=data_year))

    all_indicator_keys = [k for k in INDICATOR_KEYS if k in df_view.columns]
    num_cols = [label_mapping[k] for k in all_indicator_keys if label_mapping[k] in df_display.columns]
    inverse_labels = {ind_label(k, lang) for k in INVERSE_INDICATORS if k in INDICATOR_KEYS}
    pos_cols = [c for c in num_cols if c not in inverse_labels]
    neg_cols = [c for c in num_cols if c in inverse_labels]
    NULL_STYLE = "background-color: var(--null-bg); color: var(--null-text); font-style: italic;"

    def _is_null(val) -> bool:
        if val is None:
            return True
        if isinstance(val, float) and np.isnan(val):
            return True
        try:
            if pd.isna(val):
                return True
        except (TypeError, ValueError):
            pass
        if isinstance(val, str) and val.strip() in ("", "nan", "None", "NA", "N/A"):
            return True
        return False

    def gradient_skip_nulls(series: pd.Series, cmap: str = "YlGnBu") -> list:
        """Color gradient with automatic text color based on cell luminance."""
        numeric = pd.to_numeric(series, errors="coerce")
        valid = numeric.dropna()
        if valid.empty:
            return [NULL_STYLE] * len(series)
        vmin, vmax = valid.min(), valid.max()
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        cmap_fn = plt.get_cmap(cmap)
        result = []
        for val in numeric:
            if pd.isna(val):
                result.append(NULL_STYLE)
            else:
                rgba = cmap_fn(norm(val))
                bg = mcolors.to_hex(rgba)
                lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                fg = "#0f172a" if lum > 0.45 else "#ffffff"
                result.append(f"background-color: {bg}; color: {fg}; font-weight: 500;")
        return result

    def style_income_group(val) -> str:
        if _is_null(val):
            return NULL_STYLE
        s_lower = str(val).lower()
        hi_labels = {t("High income", "en").lower(), t("High income", "fr").lower()}
        um_labels = {t("Upper middle income", "en").lower(), t("Upper middle income", "fr").lower()}
        lm_labels = {t("Lower middle income", "en").lower(), t("Lower middle income", "fr").lower()}
        lo_labels = {t("Low income", "en").lower(), t("Low income", "fr").lower()}
        if any(l in s_lower for l in hi_labels) or "high" in s_lower:
            return "background-color:#d1fae5;color:#065f46;font-weight:600;"
        if any(l in s_lower for l in um_labels) or "upper" in s_lower:
            return "background-color:#fef3c7;color:#92400e;font-weight:600;"
        if any(l in s_lower for l in lm_labels) or "lower" in s_lower:
            return "background-color:#ffedd5;color:#9a3412;font-weight:600;"
        if any(l in s_lower for l in lo_labels) or s_lower == "low income":
            return "background-color:#fee2e2;color:#991b1b;font-weight:600;"
        return ""

    def style_text_cells(val) -> str:
        return NULL_STYLE if _is_null(val) else ""

    styled_df = df_display.style
    for col in pos_cols:
        styled_df = styled_df.apply(gradient_skip_nulls, cmap="YlGnBu", subset=[col], axis=0)
    for col in neg_cols:
        styled_df = styled_df.apply(gradient_skip_nulls, cmap="YlOrRd", subset=[col], axis=0)
    income_col = label_mapping.get("income_group", "")
    if income_col and income_col in df_display.columns:
        styled_df = styled_df.map(style_income_group, subset=[income_col])
    text_cols = [c for c in df_display.columns if c not in num_cols and c != income_col]
    if text_cols:
        styled_df = styled_df.map(style_text_cells, subset=text_cols)
    if num_cols:
        styled_df = styled_df.format("{:,.2f}", subset=num_cols, na_rep="—")
    st.dataframe(styled_df, width="stretch", height=520)

    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(t("export_csv", lang, n=len(df_display), y=data_year), data=csv,
                       file_name=f"world_economic_{data_year}.csv", mime="text/csv")


# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════
st.divider()
st.caption(t("footer", lang))


# ═══════════════════════════════════════════════════════════════════════════
# HOVER TOOLTIPS ON KPI CARDS (title + value), injected via st.iframe
# Runs in a same-origin iframe; reads each card's label/value from the parent
# DOM and shows a floating bubble that follows the cursor.
# ═══════════════════════════════════════════════════════════════════════════
_TOOLTIP_JS = r"""
(function(){
  var doc = window.parent && window.parent.document;
  if(!doc) return;
  var tip = doc.getElementById('__kpi_tip__');
  if(!tip){
    tip = doc.createElement('div');
    tip.id = '__kpi_tip__';
    tip.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;opacity:0;'
      + 'transform:translateY(6px);transition:opacity .15s ease,transform .15s ease;max-width:300px;'
      + 'padding:9px 13px;border-radius:11px;background:rgba(13,22,38,.97);color:#eaf1fb;'
      + 'border:1px solid rgba(46,141,224,.45);box-shadow:0 12px 30px rgba(8,16,32,.45);'
      + 'backdrop-filter:blur(6px);font:600 12.5px/1.45 Manrope,system-ui,sans-serif;letter-spacing:.01em;';
    doc.body.appendChild(tip);
  }
  function textOf(card){
    if(card.matches && card.matches('[data-testid="stMetric"]')){
      var l = card.querySelector('[data-testid="stMetricLabel"]');
      var v = card.querySelector('[data-testid="stMetricValue"]');
      var d = card.querySelector('[data-testid="stMetricDelta"]');
      var s = (l ? l.innerText.trim() : '');
      if(v) s += '  ·  ' + v.innerText.trim();
      if(d && d.innerText.trim()) s += '  (' + d.innerText.trim() + ')';
      return s;
    }
    var p = card.querySelector('p');
    return (p ? p.innerText : card.innerText).trim();
  }
  function place(e){
    var r = tip.getBoundingClientRect();
    var x = e.clientX + 16, y = e.clientY + 18;
    if(x + r.width + 8 > window.innerWidth) x = e.clientX - r.width - 16;
    if(y + r.height + 8 > window.innerHeight) y = window.innerHeight - r.height - 8;
    tip.style.left = Math.max(8, x) + 'px';
    tip.style.top = Math.max(8, y) + 'px';
  }
  function bind(el){
    if(el.__tb) return; el.__tb = 1; el.style.cursor = 'default';
    el.addEventListener('mouseenter', function(e){
      var tx = textOf(el);
      if(!tx){ tip.style.opacity = '0'; return; }
      tip.textContent = tx; tip.style.opacity = '1'; tip.style.transform = 'translateY(0)'; place(e);
    });
    el.addEventListener('mousemove', function(e){ if(tip.style.opacity === '1') place(e); });
    el.addEventListener('mouseleave', function(){ tip.style.opacity = '0'; tip.style.transform = 'translateY(6px)'; });
  }
  function scan(){
    var n = doc.querySelectorAll('[data-testid="stMetric"], [data-testid="stPopoverButton"] button, button[data-testid="stPopoverButton"]');
    for(var i = 0; i < n.length; i++) bind(n[i]);
  }
  scan(); setTimeout(scan, 300); setTimeout(scan, 1200);
  new MutationObserver(function(){ scan(); }).observe(doc.body, {childList:true, subtree:true});
})();
"""

try:
    _base = os.path.dirname(os.path.abspath(__file__))
    _assets = os.path.join(_base, "assets")
    os.makedirs(_assets, exist_ok=True)
    _hover_path = os.path.join(_assets, f"_kpi_hover_{lang}.html")
    with open(_hover_path, "w", encoding="utf-8") as _fh:
        _fh.write("<script>" + _TOOLTIP_JS + "</script>")
    st.iframe(os.path.join("assets", f"_kpi_hover_{lang}.html"), height=0)
except Exception:
    pass