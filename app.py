"""
Global Economic Intelligence Dashboard
Real World Bank + Our World in Data · 217 countries · 2000-2024
Code is 100% in English. All user-facing text is bilingual (EN/FR).
"""
import os
import sys
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

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GLOBAL ECONOMIC DASHBOARD",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Plotly Template (light theme only) ─────────────────────────────────────
def _build_template() -> go.layout.Template:
    tpl = go.layout.Template()
    tpl.layout.paper_bgcolor = "rgba(0,0,0,0)"
    tpl.layout.plot_bgcolor = "rgba(0,0,0,0)"
    tpl.layout.font.family = "Manrope, system-ui, sans-serif"
    tpl.layout.font.size = 12
    tpl.layout.font.color = "#475569"
    tpl.layout.title.font.family = "Manrope, system-ui, sans-serif"
    tpl.layout.title.font.size = 16
    tpl.layout.title.font.weight = 700
    tpl.layout.title.font.color = "#0f172a"
    tpl.layout.xaxis.gridcolor = "rgba(100,116,139,0.12)"
    tpl.layout.yaxis.gridcolor = "rgba(100,116,139,0.12)"
    tpl.layout.transition = dict(duration=450, easing="cubic-in-out")
    return tpl

pio.templates["app_theme"] = _build_template()
pio.templates.default = "app_theme"

# ── Load external CSS ──────────────────────────────────────────────────────
import pathlib

CSS_PATH = pathlib.Path(__file__).parent / "assets" / "style.css"

if CSS_PATH.exists():
    try:
        css_content = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error loading CSS: {e}")
else:
    st.error(f" CSS file not found at: {CSS_PATH}")
    st.info("Expected location: assets/style.css")

# ── Constants ───────────────────────────────────────────────────────────────
INCOME_ORDER = ["High income", "Upper middle income", "Lower middle income", "Low income"]
INCOME_COLORS = {"High income": "#1a9850", "Upper middle income": "#fee08b", "Lower middle income": "#f46d43", "Low income": "#d73027"}
REGION_COLORS = {"East Asia & Pacific": "#1D9E75", "Europe & Central Asia": "#3778C2", "Latin America & Caribbean": "#E67E22", "Middle East & North Africa": "#9B59B6", "North America": "#17A589", "South Asia": "#F39C12", "Sub-Saharan Africa": "#E24B4A"}
SECTOR_COLORS = {"Agriculture": "#1D9E75", "Industry": "#3778C2", "Services": "#E67E22"}
SECTOR_LABEL_KEYS = {"agriculture_pct": "Agriculture", "industry_pct": "Industry", "services_pct": "Services"}
GEO_STYLE = dict(showframe=False, showcoastlines=True, coastlinecolor="#b0bec5", showland=True, landcolor="#f0f0f0", showocean=True, oceancolor="#e0f2fe", showlakes=True, lakecolor="#e0f2fe", showcountries=True, countrycolor="#b0bec5", countrywidth=0.6)

PESTEL_PILLAR_ORDER = ["political", "economic", "social", "technological", "environmental", "legal"]
PESTEL_LABEL_KEYS = {"political": "pestel_political", "economic": "pestel_economic", "social": "pestel_social", "technological": "pestel_technological", "environmental": "pestel_environmental", "legal": "pestel_legal"}
PESTEL_INDICATORS = {
    "political": ["govt_effectiveness_index", "military_expenditure_pct_gdp", "military_expenditure_pct_govt", "political_stability_index"],
    "economic": ["agriculture_pct", "cpi_index_raw", "current_account_pct_gdp", "debt_pct_gdp", "exchange_rate", "exports_pct_gdp", "fdi_pct_gdp", "gdp_growth_pct", "gdp_per_capita", "gdp_per_capita_ppp", "gdp_total_bn", "gross_fixed_capital_formation_pct_gdp", "imports_pct_gdp", "industry_pct", "inflation", "remittances_pct_gdp", "reserves_months_imports", "services_pct", "tax_revenue_pct_gdp", "trade_openness_pct_gdp"],
    "social": ["basic_sanitation_access_pct", "education_expenditure_pct_gdp", "fertility_rate", "gini_index", "health_expenditure_per_capita", "hdi", "labor_force_participation_pct", "life_expectancy", "literacy_rate", "population_mn", "primary_completion_rate_pct", "school_enrollment_secondary_pct", "under5_mortality_per_1000", "unemployment_pct", "urban_population_pct", "youth_unemployment_pct"],
    "technological": ["bank_account_ownership_pct", "fixed_broadband_per_100", "high_tech_exports_pct", "internet_users_pct", "mobile_subscriptions_per_100", "rd_expenditure_pct_gdp", "researchers_per_million"],
    "environmental": ["cereal_yield_kg_per_ha", "co2_per_capita", "electric_power_losses_pct", "electricity_access_pct", "ghg_emissions_kt_co2eq", "pm25_air_pollution"],
    "legal": ["control_of_corruption", "corruption_perception_index", "regulatory_quality", "rule_of_law_index", "transparency_corruption_score", "voice_accountability", "women_parliament_pct"],
}
INDICATOR_TO_PILLAR = {ind: p for p, inds in PESTEL_INDICATORS.items() for ind in inds}
CORE_INDICATORS = {ind: ind for group in PESTEL_INDICATORS.values() for ind in group}
INVERSE_INDICATORS = {"inflation", "cpi_index_raw", "debt_pct_gdp", "imports_pct_gdp", "unemployment_pct", "youth_unemployment_pct", "pm25_air_pollution", "military_expenditure_pct_gdp", "military_expenditure_pct_govt", "gini_index", "under5_mortality_per_1000", "fertility_rate", "electric_power_losses_pct", "co2_per_capita", "ghg_emissions_kt_co2eq"}

INDICATOR_COLORSCALE = {"gdp_per_capita": "Viridis", "gdp_growth_pct": "RdYlGn", "inflation": "YlOrRd", "debt_pct_gdp": "YlOrRd", "agriculture_pct": "YlGn", "industry_pct": "PuBu", "services_pct": "Plasma", "life_expectancy": "RdYlGn", "hdi": "RdYlGn", "unemployment_pct": "YlOrRd", "internet_users_pct": "Cividis", "co2_per_capita": "Reds", "govt_effectiveness_index": "RdYlGn"}

def get_expressive_colorscale(indicator_key: str) -> str:
    return INDICATOR_COLORSCALE.get(indicator_key, "YlOrRd" if indicator_key in INVERSE_INDICATORS else "Viridis")

# ═══════════════════════════════════════════════════════════════════════════
# INDICATOR EXPLANATIONS (bilingual) — key -> (en_desc, en_tip, fr_desc, fr_tip)
# ═══════════════════════════════════════════════════════════════════════════
INDICATOR_INFO = {
    "gdp_per_capita": ("Average economic output per person.", "Higher = wealthier population.", "Production économique moyenne par personne.", "Plus élevé = population plus riche."),
    "gdp_per_capita_ppp": ("GDP per person adjusted for purchasing power.", "Better for comparing living standards.", "PIB par habitant ajusté au pouvoir d'achat.", "Plus pertinent pour comparer les niveaux de vie."),
    "gdp_total_bn": ("Total size of the economy.", "Higher = larger economy (not necessarily richer people).", "Taille totale de l'économie.", "Plus élevé = économie plus grande (pas forcément plus riche par habitant)."),
    "gdp_growth_pct": ("Annual growth rate of the economy.", "Positive = expanding; negative = recession.", "Taux de croissance annuel de l'économie.", "Positif = expansion ; négatif = récession."),
    "gross_fixed_capital_formation_pct_gdp": ("Investment in fixed assets (machinery, infrastructure).", "Higher = more investment.", "Investissement en actifs fixes (machines, infrastructures).", "Plus élevé = plus d'investissement."),
    "trade_openness_pct_gdp": ("Total trade (exports + imports) as a share of GDP.", "Higher = more open economy.", "Commerce total (exports + imports) rapporté au PIB.", "Plus élevé = économie plus ouverte."),
    "cpi_index_raw": ("Consumer Price Index, base 100 in 2010 — measures PRICE levels, NOT corruption.", "100 = 2010 price level; higher = more cumulative inflation since 2010.", "Indice des prix à la consommation, base 100 en 2010 — mesure les PRIX, PAS la corruption.", "100 = niveau des prix de 2010 ; plus élevé = plus d'inflation cumulée depuis 2010."),
    "inflation": ("Annual percentage change in consumer prices.", "Moderate (2-3%) is healthy; very high erodes purchasing power.", "Variation annuelle en % des prix à la consommation.", "Modérée (2-3 %) = saine ; très élevée = érode le pouvoir d'achat."),
    "debt_pct_gdp": ("Government debt as a share of GDP.", "Higher = heavier public debt burden.", "Dette publique rapportée au PIB.", "Plus élevé = fardeau de la dette plus lourd."),
    "tax_revenue_pct_gdp": ("Tax revenue collected by the state as a share of GDP.", "Higher = greater fiscal capacity.", "Recettes fiscales de l'État rapportées au PIB.", "Plus élevé = plus de capacité à financer les services publics."),
    "exports_pct_gdp": ("Exports of goods & services as a share of GDP.", "Higher = more export-oriented economy.", "Exportations de biens et services rapportées au PIB.", "Plus élevé = économie plus tournée vers l'export."),
    "imports_pct_gdp": ("Imports of goods & services as a share of GDP.", "Not inherently bad; read together with exports.", "Importations de biens et services rapportées au PIB.", "Pas forcément négatif ; à lire avec les exports."),
    "fdi_pct_gdp": ("Foreign direct investment inflows as a share of GDP.", "Higher = more attractive to foreign investors.", "Investissements directs étrangers entrants rapportés au PIB.", "Plus élevé = plus attractif pour les investisseurs étrangers."),
    "current_account_pct_gdp": ("Net balance of trade, income and transfers vs GDP.", "Positive = net lender; negative = net borrower.", "Solde net du commerce, des revenus et transferts rapporté au PIB.", "Positif = prêteur net ; négatif = emprunteur net."),
    "remittances_pct_gdp": ("Money sent home by migrants as a share of GDP.", "Higher = strong reliance on diaspora income.", "Fonds envoyés par les migrants rapportés au PIB.", "Plus élevé = forte dépendance aux revenus de la diaspora."),
    "reserves_months_imports": ("Foreign exchange reserves expressed in months of imports.", "3+ months is a common safety threshold.", "Réserves de change exprimées en mois d'importations.", "3 mois et plus = seuil de sécurité courant."),
    "exchange_rate": ("Local currency units per US dollar.", "Context-dependent; not comparable as good/bad on its own.", "Unités de monnaie locale pour un dollar US.", "Dépend du contexte ; pas interprétable seul comme bon/mauvais."),
    "agriculture_pct": ("Agriculture share of GDP.", "High share often signals a developing economy.", "Part de l'agriculture dans le PIB.", "Une part élevée signale souvent une économie en développement."),
    "industry_pct": ("Industry share of GDP (manufacturing, mining, construction).", "Reflects industrialization level.", "Part de l'industrie dans le PIB (manufacture, mines, construction).", "Reflette le niveau d'industrialisation."),
    "services_pct": ("Services share of GDP.", "Dominant in advanced, service-based economies.", "Part des services dans le PIB.", "Dominante dans les économies avancées tertiarisées."),
    "life_expectancy": ("Average number of years a newborn is expected to live.", "Higher = better health & living conditions.", "Nombre moyen d'années qu'un nouveau-né est censé vivre.", "Plus élevé = meilleure santé et conditions de vie."),
    "literacy_rate": ("Share of adults (15+) who can read and write.", "Higher = more educated population.", "Part des adultes (15 ans+) sachant lire et écrire.", "Plus élevé = population plus instruite."),
    "hdi": ("Composite index of life expectancy, education and income (0-1).", "Higher = more human development. >0.8 = very high.", "Indice composite espérance de vie, éducation et revenu (0-1).", "Plus élevé = plus de développement humain. >0,8 = très élevé."),
    "primary_completion_rate_pct": ("Share of children completing primary school.", "Higher = better basic education coverage.", "Part des enfants achevant l'école primaire.", "Plus élevé = meilleure couverture de l'éducation de base."),
    "school_enrollment_secondary_pct": ("Secondary school enrollment ratio (gross).", "Higher = broader access to secondary education.", "Taux brut de scolarisation dans le secondaire.", "Plus élevé = accès plus large au secondaire."),
    "under5_mortality_per_1000": ("Deaths of children under 5 per 1,000 live births.", "Lower = better child health.", "Décès d'enfants de moins de 5 ans pour 1 000 naissances.", "Plus faible = meilleure santé infantile."),
    "fertility_rate": ("Average number of children born per woman.", "~2.1 = replacement level; higher = faster population growth.", "Nombre moyen d'enfants nés par femme.", "~2,1 = seuil de remplacement ; plus élevé = croissance démographique plus rapide."),
    "gini_index": ("Measure of income inequality (0 = equal, 100 = unequal).", "Lower = more equal income distribution.", "Mesure des inégalités de revenu (0 = égalité, 100 = inégalité totale).", "Plus faible = répartition des revenus plus égalitaire."),
    "unemployment_pct": ("Share of the labor force without a job.", "Lower = tighter labor market.", "Part de la population active sans emploi.", "Plus faible = marché du travail plus tendu."),
    "youth_unemployment_pct": ("Unemployment rate among young people (15-24).", "Lower = better youth job prospects.", "Taux de chômage des jeunes (15-24 ans).", "Plus faible = meilleures perspectives d'emploi des jeunes."),
    "labor_force_participation_pct": ("Share of working-age people in the labor force.", "Higher = more of the population economically active.", "Part des personnes en âge de travailler sur le marché du travail.", "Plus élevé = plus de population économiquement active."),
    "urban_population_pct": ("Share of the population living in urban areas.", "Higher = more urbanized society.", "Part de la population vivant en zone urbaine.", "Plus élevé = société plus urbanisée."),
    "basic_sanitation_access_pct": ("Share of people with access to basic sanitation.", "Higher = better public health infrastructure.", "Part de la population ayant accès à un assainissement de base.", "Plus élevé = meilleures infrastructures de santé publique."),
    "health_expenditure_per_capita": ("Health spending per person (USD).", "Higher = more resources devoted to health.", "Dépenses de santé par habitant (USD).", "Plus élevé = plus de ressources consacrées à la santé."),
    "education_expenditure_pct_gdp": ("Public education spending as a share of GDP.", "Higher = greater investment in education.", "Dépenses publiques d'éducation rapportées au PIB.", "Plus élevé = investissement plus fort dans l'éducation."),
    "population_mn": ("Total population (millions).", "Size of the population.", "Population totale (millions).", "Taille de la population."),
    "internet_users_pct": ("Share of the population using the Internet.", "Higher = greater digital inclusion.", "Part de la population utilisant Internet.", "Plus élevé = meilleure inclusion numérique."),
    "mobile_subscriptions_per_100": ("Mobile cellular subscriptions per 100 people.", "Can exceed 100 (multiple SIMs per person).", "Abonnements mobiles pour 100 habitants.", "Peut dépasser 100 (plusieurs SIM par personne)."),
    "fixed_broadband_per_100": ("Fixed broadband subscriptions per 100 people.", "Higher = better fixed connectivity.", "Abonnements internet fixe pour 100 habitants.", "Plus élevé = meilleure connectivité fixe."),
    "bank_account_ownership_pct": ("Share of adults (15+) with a bank or mobile-money account (Global Findex).", "Higher = greater financial inclusion. Data only every 3 years.", "Part des adultes (15 ans+) ayant un compte bancaire ou mobile (Global Findex).", "Plus élevé = meilleure inclusion financière. Données tous les 3 ans seulement."),
    "high_tech_exports_pct": ("High-technology exports as a share of manufactured exports.", "Higher = more advanced export structure.", "Exportations de haute technologie rapportées aux exportations manufacturières.", "Plus élevé = structure exportatrice plus avancée."),
    "rd_expenditure_pct_gdp": ("Research & development spending as a share of GDP.", "Higher = stronger innovation effort.", "Dépenses de recherche-développement rapportées au PIB.", "Plus élevé = effort d'innovation plus intense."),
    "researchers_per_million": ("Number of researchers in R&D per million people.", "Higher = greater scientific capacity.", "Nombre de chercheurs en R&D par million d'habitants.", "Plus élevé = capacité scientifique plus forte."),
    "patent_applications_total": ("Total patent applications filed worldwide.", "Higher = greater inventive activity.", "Total des demandes de brevets déposées dans le monde.", "Plus élevé = plus grande activité inventive."),
    "co2_per_capita": ("CO₂ emissions per person (tonnes).", "Lower = smaller carbon footprint.", "Émissions de CO₂ par habitant (tonnes).", "Plus faible = empreinte carbone plus réduite."),
    "ghg_emissions_kt_co2eq": ("Total greenhouse gas emissions in kilotonnes of CO₂ equivalent.", "Lower = lower climate impact.", "Émissions totales de gaz à effet de serre en kilotonnes d'équivalent CO₂.", "Plus faible = moindre impact climatique."),
    "pm25_air_pollution": ("Mean annual exposure to fine PM2.5 particles (µg/m³).", "WHO guideline ≈ 5 µg/m³; higher = worse air quality.", "Exposition annuelle moyenne aux particules fines PM2,5 (µg/m³).", "Seuil OMS ≈ 5 µg/m³ ; plus élevé = moins bonne qualité de l'air."),
    "electricity_access_pct": ("Share of the population with access to electricity.", "Higher = better energy access.", "Part de la population ayant accès à l'électricité.", "Plus élevé = meilleur accès à l'énergie."),
    "electric_power_losses_pct": ("Electricity lost in transmission & distribution (%).", "Lower = more efficient grid.", "Pertes électriques en transport et distribution (%).", "Plus faible = réseau plus efficace."),
    "cereal_yield_kg_per_ha": ("Cereal production per hectare (kg).", "Higher = more productive agriculture.", "Production céréalière par hectare (kg).", "Plus élevé = agriculture plus productive."),
    "govt_effectiveness_index": ("Quality of public services & policy implementation (WGI, -2.5 to +2.5).", "Higher = more effective government.", "Qualité des services publics et de la mise en œuvre des politiques (WGI, -2,5 à +2,5).", "Plus élevé = État plus efficace."),
    "political_stability_index": ("Likelihood of political instability/violence (WGI, -2.5 to +2.5).", "Higher = more stable.", "Probabilité d'instabilité politique/violence (WGI, -2,5 à +2,5).", "Plus élevé = plus stable."),
    "rule_of_law_index": ("Confidence in rules, contracts & courts (WGI, -2.5 to +2.5).", "Higher = stronger rule of law.", "Confiance dans les règles, contrats et tribunaux (WGI, -2,5 à +2,5).", "Plus élevé = État de droit plus solide."),
    "control_of_corruption": ("Extent to which public power is exercised for private gain (WGI, -2.5 to +2.5).", "Higher = less corruption.", "Mesure dans laquelle le pouvoir public est exercé à des fins privées (WGI, -2,5 à +2,5).", "Plus élevé = moins de corruption."),
    "corruption_perception_index": ("Transparency International CPI: perceived public-sector corruption (0-100).", "Higher = cleaner (less corruption).", "CPI de Transparency International : corruption perçue du secteur public (0-100).", "Plus élevé = plus propre (moins de corruption)."),
    "regulatory_quality": ("Ability of government to design sound policies & regulations (WGI).", "Higher = better regulatory framework.", "Capacité du gouvernement à concevoir de bonnes politiques et réglementations (WGI).", "Plus élevé = meilleur cadre réglementaire."),
    "voice_accountability": ("Citizens' ability to participate & freedom of expression (WGI).", "Higher = more democratic accountability.", "Capacité des citoyens à participer et liberté d'expression (WGI).", "Plus élevé = responsabilité démocratique plus forte."),
    "transparency_corruption_score": ("CPIA rating on transparency & accountability (1 = low to 6 = high; IDA countries only).", "Higher = better governance rating.", "Note CPIA sur la transparence et la responsabilité (1 = faible à 6 = élevé ; pays IDA uniquement).", "Plus élevé = meilleure note de gouvernance."),
    "women_parliament_pct": ("Share of parliamentary seats held by women.", "Higher = greater gender representation.", "Part des sièges parlementaires occupés par des femmes.", "Plus élevé = meilleure représentation des genres."),
    "military_expenditure_pct_gdp": ("Military spending as a share of GDP.", "Context-dependent; high values may signal tension.", "Dépenses militaires rapportées au PIB.", "Dépend du contexte ; des valeurs élevées peuvent signaler des tensions."),
    "military_expenditure_pct_govt": ("Military spending as a share of total government budget.", "Higher share = larger military priority.", "Dépenses militaires rapportées au budget total de l'État.", "Part plus élevée = priorité militaire plus forte."),
    "days_to_start_business": ("Average number of days required to start a business.", "Lower = easier entrepreneurial environment.", "Nombre moyen de jours nécessaires pour créer une entreprise.", "Plus faible = environnement entrepreneurial plus facile."),
}

def indicator_info(key: str, lang: str, field: str = "desc") -> str:
    entry = INDICATOR_INFO.get(key)
    if not entry: return ""
    en_desc, en_tip, fr_desc, fr_tip = entry
    if lang == "fr": return fr_desc if field == "desc" else fr_tip
    return en_desc if field == "desc" else en_tip

def interpret_value(key: str, value, world_median, lang: str) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)): return ""
    fr = (lang == "fr")
    if key == "cpi_index_raw":
        delta = value - 100
        return (f"Prix {delta:+.0f} % vs 2010 (100 = niveau 2010)" if fr else f"Prices {delta:+.0f}% vs 2010 (100 = 2010 level)")
    if key == "hdi":
        cat = (("très élevé", "very high") if value >= 0.8 else ("élevé", "high") if value >= 0.7 else ("moyen", "medium") if value >= 0.55 else ("faible", "low"))
        return f"IDH {cat[0]}" if fr else f"HDI: {cat[1]}"
    if key in {"govt_effectiveness_index", "political_stability_index", "rule_of_law_index", "control_of_corruption", "regulatory_quality", "voice_accountability"}:
        cat = (("gouvernance forte", "strong governance") if value >= 1.0 else ("gouvernance moyenne", "moderate governance") if value >= 0 else ("gouvernance faible", "weak governance") if value >= -1.0 else ("gouvernance très faible", "very weak governance"))
        return cat[0] if fr else cat[1]
    if key == "corruption_perception_index":
        cat = (("très peu corrompu", "very clean") if value >= 75 else ("peu corrompu", "relatively clean") if value >= 50 else ("corruption élevée", "high corruption") if value >= 25 else ("corruption très élevée", "very high corruption"))
        return cat[0] if fr else cat[1]
    if key == "gini_index":
        cat = (("très inégalitaire", "very unequal") if value >= 45 else ("inégalitaire", "unequal") if value >= 35 else ("relativement égalitaire", "relatively equal"))
        return cat[0] if fr else cat[1]
    if world_median is None or (isinstance(world_median, float) and np.isnan(world_median)): return ""
    above_is_worse = key in INVERSE_INDICATORS
    if value > world_median: return ("au-dessus de la médiane mondiale (défavorable)" if fr and above_is_worse else "au-dessus de la médiane mondiale (favorable)" if fr else "above world median (unfavorable)" if above_is_worse else "above world median (favorable)")
    if value < world_median: return ("en dessous de la médiane mondiale (favorable)" if fr and above_is_worse else "en dessous de la médiane mondiale (défavorable)" if fr else "below world median (favorable)" if above_is_worse else "below world median (unfavorable)")
    return "≈ médiane mondiale" if fr else "≈ world median"

def show_indicator_info(key: str, lang: str) -> None:
    desc = indicator_info(key, lang, "desc")
    tip = indicator_info(key, lang, "tip")
    if not desc: return
    content = f"ℹ️ {desc}" + (f" &nbsp;·&nbsp; 📌 {tip}" if tip else "")
    st.markdown(f'<div class="indicator-banner">{content}</div>', unsafe_allow_html=True)

# ── Country name translation (static ISO3 table) ───────────────────────────
ISO3_TO_FR = {
    "AFG": "Afghanistan", "ALB": "Albanie", "DZA": "Algérie", "ASM": "Samoa américaines", "AND": "Andorre", "AGO": "Angola", "AIA": "Anguilla", "ATG": "Antigua-et-Barbuda", "ARG": "Argentine", "ARM": "Arménie", "ABW": "Aruba", "AUS": "Australie", "AUT": "Autriche", "AZE": "Azerbaïdjan", "BHS": "Bahamas", "BHR": "Bahreïn", "BGD": "Bangladesh", "BRB": "Barbade", "BLR": "Bélarus", "BEL": "Belgique", "BLZ": "Belize", "BEN": "Bénin", "BMU": "Bermudes", "BTN": "Bhoutan", "BOL": "Bolivie", "BIH": "Bosnie-Herzégovine", "BWA": "Botswana", "BRA": "Brésil", "VGB": "Îles Vierges britanniques", "BRN": "Brunéi Darussalam", "BGR": "Bulgarie", "BFA": "Burkina Faso", "BDI": "Burundi", "CPV": "Cabo Verde", "KHM": "Cambodge", "CMR": "Cameroun", "CAN": "Canada", "CYM": "Îles Caïmans", "CAF": "République centrafricaine", "TCD": "Tchad", "CHL": "Chili", "CHI": "Îles Anglo-Normandes", "CHN": "Chine", "COL": "Colombie", "COM": "Comores", "COD": "Congo (Rép. dém.)", "COG": "Congo (Rép.)", "CRI": "Costa Rica", "CIV": "Côte d'Ivoire", "HRV": "Croatie", "CUB": "Cuba", "CUW": "Curaçao", "CYP": "Chypre", "CZE": "Tchéquie", "DNK": "Danemark", "DJI": "Djibouti", "DMA": "Dominique", "DOM": "République dominicaine", "ECU": "Équateur", "EGY": "Égypte", "SLV": "El Salvador", "GNQ": "Guinée équatoriale", "ERI": "Érythrée", "EST": "Estonie", "SWZ": "Eswatini", "ETH": "Éthiopie", "FRO": "Îles Féroé", "FJI": "Fidji", "FIN": "Finlande", "FRA": "France", "GUF": "Guyane", "PYF": "Polynésie française", "GAB": "Gabon", "GMB": "Gambie", "GEO": "Géorgie", "DEU": "Allemagne", "GHA": "Ghana", "GRC": "Grèce", "GRL": "Groenland", "GRD": "Grenade", "GUM": "Guam", "GTM": "Guatemala", "GIN": "Guinée", "GNB": "Guinée-Bissau", "GUY": "Guyana", "HTI": "Haïti", "HND": "Honduras", "HKG": "Hong Kong", "HUN": "Hongrie", "ISL": "Islande", "IND": "Inde", "IDN": "Indonésie", "IRN": "Iran", "IRQ": "Iraq", "IRL": "Irlande", "IMN": "Île de Man", "ISR": "Israël", "ITA": "Italie", "JAM": "Jamaïque", "JPN": "Japon", "JOR": "Jordanie", "KAZ": "Kazakhstan", "KEN": "Kenya", "KIR": "Kiribati", "PRK": "Corée du Nord", "KOR": "Corée du Sud", "XKX": "Kosovo", "KSV": "Kosovo", "KWT": "Koweït", "KGZ": "Kirghizistan", "LAO": "Laos", "LVA": "Lettonie", "LBN": "Liban", "LSO": "Lesotho", "LBR": "Libéria", "LBY": "Libye", "LIE": "Liechtenstein", "LTU": "Lituanie", "LUX": "Luxembourg", "MAC": "Macao", "MDG": "Madagascar", "MWI": "Malawi", "MYS": "Malaisie", "MDV": "Maldives", "MLI": "Mali", "MLT": "Malte", "MHL": "Îles Marshall", "MRT": "Mauritanie", "MUS": "Maurice", "MEX": "Mexique", "FSM": "Micronésie", "MDA": "Moldavie", "MCO": "Monaco", "MNG": "Mongolie", "MNE": "Monténégro", "MAR": "Maroc", "MOZ": "Mozambique", "MMR": "Myanmar", "NAM": "Namibie", "NRU": "Nauru", "NPL": "Népal", "NLD": "Pays-Bas", "NCL": "Nouvelle-Calédonie", "NZL": "Nouvelle-Zélande", "NIC": "Nicaragua", "NER": "Niger", "NGA": "Nigéria", "MKD": "Macédoine du Nord", "MNP": "Îles Mariannes du Nord", "NOR": "Norvège", "OMN": "Oman", "PAK": "Pakistan", "PLW": "Palaos", "PSE": "Palestine", "PAN": "Panama", "PNG": "Papouasie-Nouvelle-Guinée", "PRY": "Paraguay", "PER": "Pérou", "PHL": "Philippines", "POL": "Pologne", "PRT": "Portugal", "PRI": "Porto Rico", "QAT": "Qatar", "ROU": "Roumanie", "RUS": "Russie", "RWA": "Rwanda", "WSM": "Samoa", "SMR": "Saint-Marin", "STP": "Sao Tomé-et-Principe", "SAU": "Arabie saoudite", "SEN": "Sénégal", "SRB": "Serbie", "SYC": "Seychelles", "SLE": "Sierra Leone", "SGP": "Singapour", "SXM": "Saint-Martin (partie néerlandaise)", "SVK": "Slovaquie", "SVN": "Slovénie", "SLB": "Îles Salomon", "SOM": "Somalie", "ZAF": "Afrique du Sud", "SSD": "Soudan du Sud", "ESP": "Espagne", "LKA": "Sri Lanka", "KNA": "Saint-Kitts-et-Nevis", "LCA": "Sainte-Lucie", "MAF": "Saint-Martin (partie française)", "VCT": "Saint-Vincent-et-les-Grenadines", "SDN": "Soudan", "SUR": "Suriname", "SWE": "Suède", "CHE": "Suisse", "SYR": "Syrie", "TWN": "Taïwan", "TJK": "Tadjikistan", "TZA": "Tanzanie", "THA": "Thaïlande", "TLS": "Timor oriental", "TGO": "Togo", "TON": "Tonga", "TTO": "Trinité-et-Tobago", "TUN": "Tunisie", "TUR": "Türkiye", "TKM": "Turkménistan", "TCA": "Îles Turques-et-Caïques", "TUV": "Tuvalu", "UGA": "Ouganda", "UKR": "Ukraine", "ARE": "Émirats arabes unis", "GBR": "Royaume-Uni", "USA": "États-Unis", "URY": "Uruguay", "UZB": "Ouzbékistan", "VUT": "Vanuatu", "VEN": "Venezuela", "VNM": "Viet Nam", "VIR": "Îles Vierges américaines", "PSS": "Cisjordanie et Gaza", "YEM": "Yémen", "ZMB": "Zambie", "ZWE": "Zimbabwe",
}

def cname(name, lang):
    if lang != "fr": return name
    iso3 = df_all.loc[df_all["country"] == name, "iso3"].iloc[0] if name in df_all["country"].values else None
    if iso3 and iso3 in ISO3_TO_FR: return ISO3_TO_FR[iso3]
    return name

# ── Helpers ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
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
        if col in df.columns: df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})
    if "iso3" in df.columns: df["iso3"] = df["iso3"].str.upper()
    available = [c for c in CORE_INDICATORS if c in df.columns]
    meta_cols = ["iso3", "country", "region", "income_group", "latitude", "longitude"]
    keep = [c for c in meta_cols if c in df.columns] + ["year"] + available
    df = df[keep].copy()
    for col in available: df[col] = pd.to_numeric(df[col], errors="coerce")
    if "income_group" in df.columns: df["income_group"] = pd.Categorical(df["income_group"], categories=INCOME_ORDER, ordered=True)
    return df

def _en_label(key: str) -> str: return TRANSLATIONS.get("en", {}).get(key, key.replace("_", " ").title())
def ind_label(key: str, current_lang: str, with_pillar: bool = False) -> str:
    label = t(key, current_lang)
    if label == key: label = key.replace("_", " ").title()
    if with_pillar:
        pillar = INDICATOR_TO_PILLAR.get(key)
        if pillar: return f"{t(PESTEL_LABEL_KEYS[pillar], current_lang)} — {label}"
    return label
def previous_year(years: list, current: int) -> int:
    earlier = [y for y in years if y < current]
    return max(earlier) if earlier else current
def safe_delta(current, previous):
    if pd.notna(current) and pd.notna(previous): return float(current) - float(previous)
    return None

def get_pestel_scores(df_target: pd.DataFrame, df_world: pd.DataFrame, year: int) -> dict:
    world_year = df_world[df_world["year"] == year]
    target_year = df_target[df_target["year"] == year]
    scores = {}
    for pillar in PESTEL_PILLAR_ORDER:
        norms = []
        for ind in PESTEL_INDICATORS[pillar]:
            if ind not in target_year.columns or ind not in world_year.columns: continue
            value = target_year[ind].median(skipna=True)
            w_min = world_year[ind].min(skipna=True)
            w_max = world_year[ind].max(skipna=True)
            if pd.isna(value) or pd.isna(w_min) or pd.isna(w_max) or w_max <= w_min: continue
            norm = (value - w_min) / (w_max - w_min)
            if ind in INVERSE_INDICATORS: norm = 1.0 - norm
            norms.append(float(np.clip(norm, 0.0, 1.0)))
        scores[pillar] = round(100.0 * np.mean(norms), 1) if norms else 0.0
    return scores

# ── Load data ──────────────────────────────────────────────────────────────
df_all = load_data()
INDICATOR_KEYS = [ind for pillar in PESTEL_PILLAR_ORDER for ind in sorted(PESTEL_INDICATORS[pillar], key=_en_label) if ind in df_all.columns]
ALL_REGIONS = sorted(df_all["region"].dropna().unique()) if "region" in df_all.columns else []
ALL_COUNTRIES = sorted(df_all["country"].dropna().unique())
YEAR_MIN = int(df_all["year"].min())
YEAR_MAX = int(df_all["year"].max())
ALL_YEARS = sorted(df_all["year"].unique())

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    lang = st.radio("🌐 Language / Langue", ["EN", "FR"], horizontal=True, index=0, key="lang_choice").lower()
    st.markdown(f"## {t('sidebar_title', lang)}")
    default_years = [y for y in ALL_YEARS if y >= 2010]
    sel_years = st.multiselect(t("years_label", lang), ALL_YEARS, default=default_years)
    if not sel_years:
        sel_years = ALL_YEARS
        st.warning(t("no_year_selected", lang))
    sel_regions = st.multiselect(t("regions", lang), ALL_REGIONS, default=ALL_REGIONS, format_func=lambda x: t(x, lang))
    sel_income = st.multiselect(t("income_levels", lang), INCOME_ORDER, default=INCOME_ORDER, format_func=lambda x: t(x, lang))
    st.divider()
    if st.button(t("refresh_btn", lang), width="stretch"):
        with st.spinner(t("refreshing", lang)):
            try:
                res = subprocess.run([sys.executable, os.path.join("data", "fetch_data.py")], capture_output=True, text=True, timeout=600)
                if res.returncode == 0:
                    st.cache_data.clear()
                    st.success(t("refresh_ok", lang))
                    st.rerun()
                else: st.error(t("refresh_err", lang, e=res.stderr[:300]))
            except Exception as e: st.error(t("refresh_conn", lang, e=str(e)))
    st.divider()
    st.caption(t("source", lang))

# ── Global filters ──────────────────────────────────────────────────────────
mask = (df_all["year"].isin(sel_years) & df_all["region"].isin(sel_regions) & df_all["income_group"].isin(sel_income))
df = df_all[mask].copy()
latest_year = int(df["year"].max()) if not df.empty else max(sel_years)
df_latest = df[df["year"] == latest_year]
prev_year = previous_year(sorted(sel_years), latest_year)
df_prev = df[df["year"] == prev_year]

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"## {t('app_title', lang).upper()}")
st.caption(f"{t('app_caption', lang, n=df['country'].nunique(), y0=min(sel_years), y1=max(sel_years), ly=latest_year)} · {t('data_lag_note', lang)}")
st.divider()

# ── Global KPIs with tooltips ───────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

med_gdp = df_latest["gdp_per_capita"].median() if "gdp_per_capita" in df_latest else None
med_gdp_p = df_prev["gdp_per_capita"].median() if "gdp_per_capita" in df_prev else None
med_inf = df_latest["inflation"].median() if "inflation" in df_latest else None
med_inf_p = df_prev["inflation"].median() if "inflation" in df_prev else None
med_debt = df_latest["debt_pct_gdp"].median() if "debt_pct_gdp" in df_latest else None
med_debt_p = df_prev["debt_pct_gdp"].median() if "debt_pct_gdp" in df_prev else None
med_unemp = df_latest["unemployment_pct"].median() if "unemployment_pct" in df_latest else None
med_unemp_p = df_prev["unemployment_pct"].median() if "unemployment_pct" in df_prev else None

d_gdp = safe_delta(med_gdp, med_gdp_p)
d_inf = safe_delta(med_inf, med_inf_p)
d_debt = safe_delta(med_debt, med_debt_p)
d_unemp = safe_delta(med_unemp, med_unemp_p)

med_life = df_latest["life_expectancy"].median() if "life_expectancy" in df_latest else None
med_life_p = df_prev["life_expectancy"].median() if "life_expectancy" in df_prev else None
d_life = safe_delta(med_life, med_life_p)

gdp_tooltip = f"{ind_label('gdp_per_capita', lang)}: ${med_gdp:,.0f}" if pd.notna(med_gdp) else "N/A"
inf_tooltip = f"{ind_label('inflation', lang)}: {med_inf:.1f}%" if pd.notna(med_inf) else "N/A"
debt_tooltip = f"{ind_label('debt_pct_gdp', lang)}: {med_debt:.1f}%" if pd.notna(med_debt) else "N/A"
unemp_tooltip = f"{ind_label('unemployment_pct', lang)}: {med_unemp:.1f}%" if pd.notna(med_unemp) else "N/A"
life_tooltip = f"{ind_label('life_expectancy', lang)}: {med_life:.1f} ans" if pd.notna(med_life) else "N/A"

k1.metric(ind_label("gdp_per_capita", lang), f"${med_gdp:,.0f}" if pd.notna(med_gdp) else "N/A", f"{d_gdp:+,.0f}" if d_gdp is not None else "", help=gdp_tooltip)
k2.metric(ind_label("inflation", lang), f"{med_inf:.1f}%" if pd.notna(med_inf) else "N/A", f"{d_inf:+.1f} pp" if d_inf is not None else "", delta_color="inverse", help=inf_tooltip)
k3.metric(ind_label("debt_pct_gdp", lang), f"{med_debt:.1f}%" if pd.notna(med_debt) else "N/A", f"{d_debt:+.1f} pp" if d_debt is not None else "", delta_color="inverse", help=debt_tooltip)
k4.metric(ind_label("unemployment_pct", lang), f"{med_unemp:.1f}%" if pd.notna(med_unemp) else "N/A",
          f"{d_unemp:+.1f} pp" if d_unemp is not None else "", delta_color="inverse", help=unemp_tooltip)
k5.metric(ind_label("life_expectancy", lang), 
          f"{med_life:.1f}" if pd.notna(med_life) else "N/A",
          f"{d_life:+.1f}" if d_life is not None else "", 
          help=life_tooltip)
st.divider()

# ── Tabs navigation ─────────────────────────────────────────────────────────
tab_map, tab_trend, tab_country, tab_compare, tab_struct, tab_data = st.tabs([t("tab_map", lang), t("tab_trend", lang), t("tab_country", lang), t("tab_compare", lang), t("tab_struct", lang), t("tab_data", lang)])

# ── TAB 1: WORLD MAP ────────────────────────────────────────────────────────
with tab_map:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: map_ind = st.selectbox(t("map_indicator", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang, with_pillar=True), key="map_ind")
    with c2: map_type = st.radio(t("map_type", lang), ["choropleth", "bubble"], format_func=lambda x: t(x, lang), horizontal=True)
    with c3: map_year = st.selectbox(t("ref_year", lang), sorted(sel_years, reverse=True), index=0, key="map_yr")
    show_indicator_info(map_ind, lang)
    
    size_choice_key = None
    if map_type == "bubble":
        size_options = [map_ind]
        if "population_mn" in df.columns and map_ind != "population_mn": size_options.append("population_mn")
        size_choice_key = st.radio(t("bubble_size_label", lang), size_options, format_func=lambda x: ind_label(x, lang), index=0, horizontal=True)

    df_map = df[df["year"] == map_year].dropna(subset=[map_ind]).copy()
    ilabel = ind_label(map_ind, lang)
    cscale = get_expressive_colorscale(map_ind)
    df_map["_cname"] = df_map["country"].map(lambda n: cname(n, lang))
    world_median_map = (df_all[df_all["year"] == map_year][map_ind].median() if map_ind in df_all.columns else None)
    df_map["_interpret"] = df_map[map_ind].apply(lambda v: interpret_value(map_ind, v, world_median_map, lang))

    if map_type == "choropleth":
        zmin, zmax = None, None
        if not df_map.empty and df_map[map_ind].nunique() > 1:
            zmin = float(np.percentile(df_map[map_ind], 2))
            zmax = float(np.percentile(df_map[map_ind], 98))
            if zmax <= zmin: zmin, zmax = None, None
        fig_map = go.Figure(go.Choropleth(locations=df_map["iso3"], z=df_map[map_ind], text=df_map["_cname"], customdata=df_map[[map_ind, "region", "income_group", "_interpret"]].values, zmin=zmin, zmax=zmax, hovertemplate=("<b>%{text}</b><br>" + f"{ilabel}: %{{customdata[0]:,.2f}}<br>" + "<b>%{customdata[3]}</b><br>" + f"{t('region', lang)}: %{{customdata[1]}}<br>" + f"{t('income_level', lang)}: %{{customdata[2]}}<br><extra></extra>"), colorscale=cscale, colorbar=dict(title=ilabel, len=0.6, thickness=15, tickfont=dict(size=10)), marker_line_color="#78909c", marker_line_width=0.6))
        fig_map.update_layout(title=dict(text=f"{ilabel} — {map_year}", font=dict(size=15)), geo=dict(**GEO_STYLE, projection_type="natural earth"), margin=dict(t=50, b=0, l=0, r=0), height=520)
    else:
        size_col = size_choice_key if size_choice_key else map_ind
        df_map["_size"] = df_map[size_col].fillna(0).clip(lower=0)
        fig_map = go.Figure()
        for ig in INCOME_ORDER:
            sub = df_map[df_map["income_group"] == ig]
            if sub.empty or sub["_size"].max() <= 0: continue
            fig_map.add_trace(go.Scattergeo(locations=sub["iso3"], marker=dict(size=sub["_size"], sizemode="area", sizeref=2. * sub["_size"].max() / (42 ** 2), sizemin=4, color=INCOME_COLORS[ig], opacity=0.85, line=dict(color="white", width=0.5)), text=sub["_cname"], customdata=sub[[map_ind, "region", size_col, "_interpret"]].values, hovertemplate=("<b>%{text}</b><br>" + f"{ilabel}: %{{customdata[0]:,.2f}}<br>" + "<b>%{customdata[3]}</b><br>" + f"{t('region', lang)}: %{{customdata[1]}}<br>" + f"{ind_label(size_col, lang)}: %{{customdata[2]:,.2f}}<br><extra></extra>"), name=t(ig, lang)))
        fig_map.update_layout(title=dict(text=f"{ilabel} — {map_year}", font=dict(size=15)), geo=dict(**GEO_STYLE, projection_type="natural earth"), margin=dict(t=50, b=0, l=0, r=0), height=520, legend=dict(orientation="h", y=-0.1, font_size=11))
    st.plotly_chart(fig_map, width="stretch")

    st.markdown(t("median_by_region", lang, ind=ilabel, y=map_year))
    if not df_map.empty and "region" in df_map.columns:
        reg_med = df_map.groupby("region")[map_ind].median().round(2).sort_values(ascending=False).reset_index()
        cols_r = st.columns(min(len(reg_med), 7))
        for i, row in reg_med.iterrows():
            if i < len(cols_r):
                region_tooltip = f"{t(row['region'], lang)} · {ilabel}: {row[map_ind]:,.1f}"
                cols_r[i].metric(t(row["region"], lang), f"{row[map_ind]:,.1f}", help=region_tooltip)

# ── TAB 2: TRENDS ───────────────────────────────────────────────────────────
with tab_trend:
    t1, t2 = st.columns([2, 1])
    with t1: trend_ind = st.selectbox(t("indicator", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang, with_pillar=True), key="tr_ind")
    with t2: group_col = st.radio(t("group_by", lang), ["income_group", "region"], format_func=lambda x: t("income_level" if x == "income_group" else "region", lang), horizontal=True)
    show_indicator_info(trend_ind, lang)
    
    group_label_key = "income_level" if group_col == "income_group" else "region"
    color_map_ = INCOME_COLORS if group_col == "income_group" else REGION_COLORS
    cat_order_ = INCOME_ORDER if group_col == "income_group" else ALL_REGIONS
    df_tr = df.groupby(["year", group_col])[trend_ind].median().reset_index().rename(columns={trend_ind: "value"})
    df_tr["group_label"] = df_tr[group_col].map(lambda x: t(x, lang))
    display_color_map = {t(k, lang): v for k, v in color_map_.items()}
    display_order = [t(x, lang) for x in cat_order_]
    
    fig_tr = px.line(df_tr, x="year", y="value", color="group_label", color_discrete_map=display_color_map, category_orders={"group_label": display_order}, markers=True, labels={"year": t("year_label", lang), "value": ind_label(trend_ind, lang), "group_label": ""}, title=t("trend_title", lang, ind=ind_label(trend_ind, lang), grp=t(group_label_key, lang).lower(), y0=min(sel_years), y1=max(sel_years)))
    fig_tr.update_traces(line_width=2.5, marker_size=5)
    fig_tr.update_layout(margin=dict(t=50, b=20, l=10, r=10), hovermode="x unified", legend=dict(orientation="h", y=-0.3, font_size=11), height=420)
    for event_year, label_key in [(2008, "ev_2008"), (2020, "ev_2020"), (2022, "ev_2022")]:
        if min(sel_years) <= event_year <= max(sel_years):
            fig_tr.add_vline(x=event_year, line_dash="dot", line_color="#94a3b8", line_width=1)
            fig_tr.add_annotation(x=event_year, y=1, yref="paper", text=t(label_key, lang).replace("\n", "<br>"), showarrow=False, yanchor="top", font=dict(size=10, color="#64748b"))
    st.plotly_chart(fig_tr, width="stretch")

    st.markdown("---")
    st.markdown(f"**📌 {t('scatter_title', lang)}**")
    s1, s2, s3 = st.columns(3)
    with s1: x_ind = st.selectbox(t("x_axis", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang), index=0, key="sx")
    with s2: y_ind = st.selectbox(t("y_axis", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang), index=min(2, len(INDICATOR_KEYS) - 1), key="sy")
    with s3: sc_yr = st.selectbox(t("year_label", lang), sorted(sel_years, reverse=True), index=0, key="syr")
    
    df_sc = df[df["year"] == sc_yr].dropna(subset=[x_ind, y_ind]).copy()
    size_col = "gdp_total_bn" if "gdp_total_bn" in df_sc.columns else None
    if size_col: df_sc = df_sc.dropna(subset=[size_col])
    if not df_sc.empty:
        use_trendline = ("ols" if (len(df_sc) >= 3 and df_sc[x_ind].nunique() > 1 and df_sc[y_ind].nunique() > 1) else None)
        df_sc["income_label"] = df_sc["income_group"].map(lambda x: t(x, lang))
        df_sc["_cname"] = df_sc["country"].map(lambda n: cname(n, lang))
        fig_sc = px.scatter(df_sc, x=x_ind, y=y_ind, color="income_label", color_discrete_map={t(k, lang): v for k, v in INCOME_COLORS.items()}, category_orders={"income_label": [t(v, lang) for v in INCOME_ORDER]}, size=size_col, size_max=45, hover_name="_cname", trendline=use_trendline, labels={x_ind: ind_label(x_ind, lang), y_ind: ind_label(y_ind, lang), "income_label": t("income_level", lang)}, title=t("scatter_chart_title", lang, xi=ind_label(x_ind, lang), yi=ind_label(y_ind, lang), y=sc_yr))
        fig_sc.update_layout(margin=dict(t=50, b=20, l=10, r=10), legend=dict(orientation="h", y=-0.25), height=430)
        st.plotly_chart(fig_sc, width="stretch")
    else: st.info(t("no_data", lang))

# ── TAB 3: COUNTRY PROFILE ──────────────────────────────────────────────────
with tab_country:
    default_idx = ALL_COUNTRIES.index("Cameroon") if "Cameroon" in ALL_COUNTRIES else 0
    sel_country = st.selectbox(t("select_country", lang), ALL_COUNTRIES, index=default_idx, key="cp_country", format_func=lambda n: cname(n, lang))
    df_c = df[df["country"] == sel_country].sort_values("year")
    if df_c.empty: st.warning(t("no_data", lang))
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
        
        ov1.metric(t("income_group_label", lang), t(income_grp, lang), help=f"{t('income_group_label', lang)}: {t(income_grp, lang)}")
        ov2.metric(t("region_label", lang), t(region_val, lang), help=f"{t('region_label', lang)}: {t(region_val, lang)}")
        
        world_med = (df_all[df_all["year"] == latest_year_c]["gdp_per_capita"].median() if "gdp_per_capita" in df_all.columns else None)
        gdp_val = latest_c.get("gdp_per_capita", None)
        gdp_delta = safe_delta(gdp_val, prev_c.get("gdp_per_capita", None))
        help_text = (f"{t('vs_world', lang)}: {gdp_val - world_med:+,.0f}" if (world_med is not None and pd.notna(gdp_val) and pd.notna(world_med)) else f"{ind_label('gdp_per_capita', lang)}: ${gdp_val:,.0f}" if pd.notna(gdp_val) else "N/A")
        ov3.metric(ind_label("gdp_per_capita", lang), f"${gdp_val:,.0f}" if pd.notna(gdp_val) else "N/A", f"{gdp_delta:+,.0f}" if gdp_delta is not None else "", help=help_text)
        
        inf_val = latest_c.get("inflation", None)
        inf_delta = safe_delta(inf_val, prev_c.get("inflation", None))
        ov4.metric(ind_label("inflation", lang), f"{inf_val:.1f}%" if pd.notna(inf_val) else "N/A", f"{inf_delta:+.1f} pp" if inf_delta is not None else "", delta_color="inverse", help=f"{ind_label('inflation', lang)}: {inf_val:.1f}%" if pd.notna(inf_val) else "N/A")
        
        debt_val = latest_c.get("debt_pct_gdp", None)
        debt_delta = safe_delta(debt_val, prev_c.get("debt_pct_gdp", None))
        ov5.metric(ind_label("debt_pct_gdp", lang), f"{debt_val:.1f}%" if pd.notna(debt_val) else "N/A", f"{debt_delta:+.1f} pp" if debt_delta is not None else "", delta_color="inverse", help=f"{ind_label('debt_pct_gdp', lang)}: {debt_val:.1f}%" if pd.notna(debt_val) else "N/A")
        
        st.divider()

        map_col, donut_col = st.columns([1.5, 1])
        with map_col:
            geo_centered = dict(**GEO_STYLE, projection_type="natural earth", center=dict(lon=lon, lat=lat), projection_scale=2.5)
            df_geo = df_all[df_all["year"] == int(latest_year_c)].copy()
            hl_color = INCOME_COLORS.get(income_grp, "#1D9E75")
            fig_geo = go.Figure()
            other = df_geo[df_geo["country"] != sel_country]
            fig_geo.add_trace(go.Choropleth(locations=other["iso3"], z=[0.5] * len(other), colorscale=[[0, "#cfd8dc"], [1, "#cfd8dc"]], showscale=False, marker_line_color="#90a4ae", marker_line_width=0.4, hoverinfo="skip"))
            sel_geo = df_geo[df_geo["country"] == sel_country]
            if not sel_geo.empty:
                fig_geo.add_trace(go.Choropleth(locations=sel_geo["iso3"], z=[1], colorscale=[[0, hl_color], [1, hl_color]], showscale=False, marker_line_color="white", marker_line_width=2.5, text=[cname(sel_country, lang)], hovertemplate=(f"<b>{cname(sel_country, lang)}</b><br>" f"{t('income_group_label', lang)}: {t(income_grp, lang)}<extra></extra>")))
            fig_geo.update_layout(title=dict(text=t("country_map_title", lang, c=cname(sel_country, lang)), font=dict(size=13)), geo=geo_centered, margin=dict(t=45, b=0, l=0, r=0), height=320)
            st.plotly_chart(fig_geo, width="stretch")
        with donut_col:
            agr = latest_c.get("agriculture_pct", None)
            ind_ = latest_c.get("industry_pct", None)
            svc = latest_c.get("services_pct", None)
            if all(pd.notna(v) for v in [agr, ind_, svc]):
                fig_donut = go.Figure(go.Pie(labels=[t("Agriculture", lang), t("Industry", lang), t("Services", lang)], values=[agr, ind_, svc], hole=0.55, marker_colors=[SECTOR_COLORS["Agriculture"], SECTOR_COLORS["Industry"], SECTOR_COLORS["Services"]], textinfo="label+percent", hovertemplate="%{label}: %{value:.1f}%<extra></extra>"))
                fig_donut.update_layout(title=dict(text=t("sector_breakdown", lang, y=int(latest_year_c)), font=dict(size=13)), margin=dict(t=45, b=10, l=10, r=10), legend=dict(orientation="h", y=-0.2, font_size=11), height=320)
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
            fig_radar.add_trace(go.Scatterpolar(r=[country_scores[p] for p in PESTEL_PILLAR_ORDER], theta=categories, fill="toself", name=cname(sel_country, lang)))
            fig_radar.add_trace(go.Scatterpolar(r=[region_scores.get(p, 0) for p in PESTEL_PILLAR_ORDER], theta=categories, fill="toself", name=t("region_median", lang)))
            fig_radar.add_trace(go.Scatterpolar(r=[world_scores.get(p, 0) for p in PESTEL_PILLAR_ORDER], theta=categories, fill="toself", name=t("world_median", lang)))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, title=dict(text=t("pestel_performance_radar", lang), font=dict(size=13)), margin=dict(l=40, r=40, t=60, b=40), height=380)
            st.plotly_chart(fig_radar, width="stretch")
        with col2:
            exports_val = latest_c.get("exports_pct_gdp", None)
            imports_val = latest_c.get("imports_pct_gdp", None)
            balance_val = latest_c.get("current_account_pct_gdp", None)
            if all(pd.notna(v) for v in [exports_val, imports_val, balance_val]):
                fig_wf = go.Figure(go.Waterfall(name="Trade Balance", orientation="v", measure=["relative", "relative", "total"], x=[t("exports", lang), t("imports", lang), t("current_account", lang)], y=[exports_val, -imports_val, balance_val], text=[f"+{exports_val:.1f}%", f"-{imports_val:.1f}%", f"{balance_val:.1f}%"], textposition="outside", connector={"line": {"color": "rgb(100,116,139)"}}))
                fig_wf.update_layout(title=t("trade_balance_waterfall", lang), height=380, margin=dict(l=20, r=20, t=40, b=20), yaxis_title=t("pct_gdp", lang))
                st.plotly_chart(fig_wf, width="stretch")
            else: st.info(t("trade_data_unavailable", lang))

        col3, col4 = st.columns(2)
        with col3:
            df_s = df_c[["year", "agriculture_pct", "industry_pct", "services_pct"]].dropna()
            if not df_s.empty:
                df_s_melt = df_s.melt(id_vars="year", value_vars=["agriculture_pct", "industry_pct", "services_pct"], var_name="sector_key", value_name="value")
                df_s_melt["sector"] = df_s_melt["sector_key"].map(lambda k: t(SECTOR_LABEL_KEYS[k], lang))
                fig_area = px.area(df_s_melt, x="year", y="value", color="sector", groupnorm="percent", labels={"year": t("year_label", lang), "value": t("share_of_gdp", lang), "sector": t("sector", lang)}, title=t("sector_evolution_title", lang), color_discrete_map={t("Agriculture", lang): SECTOR_COLORS["Agriculture"], t("Industry", lang): SECTOR_COLORS["Industry"], t("Services", lang): SECTOR_COLORS["Services"]})
                fig_area.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=-0.2))
                st.plotly_chart(fig_area, width="stretch")
            else: st.info(t("sector_data_unavailable", lang))
        with col4:
            indicators_hm = ["gdp_per_capita", "inflation", "debt_pct_gdp", "unemployment_pct", "life_expectancy", "electricity_access_pct", "internet_users_pct", "pm25_air_pollution"]
            avail_hm = [i for i in indicators_hm if i in df_c.columns]
            if avail_hm and len(df_c) > 1:
                df_hm = df_c[["year"] + avail_hm].set_index("year").tail(10)
                df_norm = (df_hm - df_hm.min()) / (df_hm.max() - df_hm.min() + 1e-9)
                df_norm.columns = [ind_label(c, lang) for c in df_norm.columns]
                fig_hm = px.imshow(df_norm.T, labels=dict(x=t("year_label", lang), y=t("indicator", lang), color=t("normalized_score", lang)), title=t("indicator_trends_title", lang), color_continuous_scale="RdBu_r", aspect="auto", zmin=0, zmax=1)
                fig_hm.update_layout(height=380, margin=dict(l=60, r=20, t=50, b=20))
                st.plotly_chart(fig_hm, width="stretch")
            else: st.info(t("heatmap_unavailable", lang))

        if "gdp_per_capita" in df_c.columns and "inflation" in df_c.columns:
            fig_comb = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comb.add_trace(go.Scatter(x=df_c["year"], y=df_c["gdp_per_capita"], name=ind_label("gdp_per_capita", lang), line=dict(color="#0067C0", width=2)), secondary_y=False)
            fig_comb.add_trace(go.Scatter(x=df_c["year"], y=df_c["inflation"], name=ind_label("inflation", lang), line=dict(color="#d97706", width=2, dash="dot")), secondary_y=True)
            fig_comb.update_layout(title=t("gdp_inflation_title", lang), legend=dict(orientation="h", y=-0.2), margin=dict(t=40, b=20, l=10, r=10), height=300)
            fig_comb.update_yaxes(title_text=ind_label("gdp_per_capita", lang), secondary_y=False, showgrid=False)
            fig_comb.update_yaxes(title_text=ind_label("inflation", lang), secondary_y=True, showgrid=False)
            st.plotly_chart(fig_comb, width="stretch")

        MINI_SPECS = [("unemployment_pct", "gauge", [0, 30], "#dc2626"), ("gdp_growth_pct", "delta", None, None), ("primary_completion_rate_pct", "gauge", [0, 100], "#0067C0"), ("life_expectancy", "gauge", [40, 90], "#059669"), ("internet_users_pct", "gauge", [0, 100], "#7c3aed"), ("electricity_access_pct", "gauge", [0, 100], "#d97706")]
        MINI_LABELS = {"unemployment_pct": ("Unemployment", "Chômage"), "gdp_growth_pct": ("GDP growth", "Croissance PIB"), "primary_completion_rate_pct": ("Primary completion", "Achèvement primaire"), "life_expectancy": ("Life expectancy", "Espérance de vie"), "internet_users_pct": ("Internet users", "Internet"), "electricity_access_pct": ("Electricity access", "Accès élec.")}
        mini_cols = st.columns(len(MINI_SPECS))
        for col, (key, mode, grange, gcolor) in zip(mini_cols, MINI_SPECS):
            val = latest_c.get(key, None)
            if not pd.notna(val): continue
            en_l, fr_l = MINI_LABELS.get(key, (key, key))
            label = fr_l if lang == "fr" else en_l
            with col:
                if mode == "gauge":
                    fig_mini = go.Figure(go.Indicator(mode="number+gauge", value=val, title={"text": label, "font": {"size": 9}}, domain={"x": [0, 1], "y": [0, 1]}, gauge={"axis": {"range": grange, "tickfont": {"size": 8}}, "bar": {"color": gcolor}, "borderwidth": 0}, number={"font": {"size": 15}, "valueformat": ".1f"}))
                else:
                    prev_val = prev_c.get(key, 0)
                    fig_mini = go.Figure(go.Indicator(mode="number+delta", value=val, title={"text": label, "font": {"size": 9}}, number={"font": {"size": 15}, "valueformat": ".1f"}, delta={"reference": prev_val if pd.notna(prev_val) else 0, "valueformat": ".1f", "font": {"size": 10}}))
                fig_mini.update_layout(height=150, margin=dict(l=8, r=8, t=30, b=6))
                st.plotly_chart(fig_mini, width="stretch")

# ── TAB 4: COMPARE COUNTRIES ────────────────────────────────────────────────
with tab_compare:
    defaults = [c for c in ["Cameroon", "France", "China", "Nigeria", "Brazil", "Germany", "India", "United States"] if c in ALL_COUNTRIES]
    sel_ctry = st.multiselect(t("select_countries", lang), ALL_COUNTRIES, default=defaults, max_selections=12, format_func=lambda n: cname(n, lang))
    comp_ind = st.selectbox(t("indicator", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang, with_pillar=True), key="cp_ind")
    show_indicator_info(comp_ind, lang)
    if not sel_ctry: st.info(t("select_least_one", lang))
    else:
        df_cp = df[df["country"].isin(sel_ctry)].copy()
        df_cp["_cname"] = df_cp["country"].map(lambda n: cname(n, lang))
        fig_cp = px.line(df_cp, x="year", y=comp_ind, color="_cname", color_discrete_sequence=px.colors.qualitative.Set2, markers=True, labels={"year": t("year_label", lang), comp_ind: ind_label(comp_ind, lang), "_cname": ""}, title=f"{ind_label(comp_ind, lang)} — {min(sel_years)}–{max(sel_years)}")
        fig_cp.update_layout(margin=dict(t=50, b=20, l=10, r=10), hovermode="x unified", legend=dict(orientation="h", y=-0.25), height=400)
        st.plotly_chart(fig_cp, width="stretch")
        
        latest_year_cp = int(df_cp["year"].max())
        prev_year_cp = previous_year(sorted(df_cp["year"].unique()), latest_year_cp)
        df_latest_cp = df_cp[df_cp["year"] == latest_year_cp].dropna(subset=[comp_ind])
        if not df_latest_cp.empty:
            ascending = comp_ind in INVERSE_INDICATORS
            df_rank = df_latest_cp.sort_values(comp_ind, ascending=ascending)
            fig_rank = px.bar(df_rank, x="_cname", y=comp_ind, color="_cname", color_discrete_sequence=px.colors.qualitative.Set2, labels={"_cname": t("col_country", lang), comp_ind: ind_label(comp_ind, lang)}, title=t("ranking_title", lang, ind=ind_label(comp_ind, lang), y=latest_year_cp))
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

# ── TAB 5: ECONOMIC STRUCTURE ───────────────────────────────────────────────
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
            fig_tree = px.treemap(df_tree_m, path=["region", "income_group", "sector"], values="pct", color="pct", color_continuous_scale="RdYlGn", title=t("treemap_title", lang, y=latest_year))
            fig_tree.update_layout(margin=dict(t=50, b=0, l=0, r=0), height=420)
            st.plotly_chart(fig_tree, width="stretch")
    with c_right:
        if "gdp_per_capita" in df.columns:
            df_vio = df[df["year"] == latest_year].dropna(subset=["gdp_per_capita"]).copy()
            df_vio = df_vio[df_vio["gdp_per_capita"] > 0]
            df_vio["income_label"] = df_vio["income_group"].map(lambda x: t(x, lang))
            df_vio["_cname"] = df_vio["country"].map(lambda n: cname(n, lang))
            fig_vio = px.violin(df_vio, x="income_label", y="gdp_per_capita", color="income_label", color_discrete_map={t(k, lang): v for k, v in INCOME_COLORS.items()}, category_orders={"income_label": [t(v, lang) for v in INCOME_ORDER]}, box=True, points="all", hover_name="_cname", labels={"income_label": "", "gdp_per_capita": ind_label("gdp_per_capita", lang)}, title=t("violin_title", lang, y=latest_year))
            fig_vio.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10), yaxis_type="log", yaxis_title=t("gdp_log", lang), height=420)
            st.plotly_chart(fig_vio, width="stretch")
            
    st.markdown("---")
    rank_ind = st.selectbox(t("ranking_indicator", lang), INDICATOR_KEYS, format_func=lambda x: ind_label(x, lang, with_pillar=True), key="rank_ind")
    show_indicator_info(rank_ind, lang)
    df_rank_struct = df[df["year"] == latest_year].dropna(subset=[rank_ind]).copy()
    if not df_rank_struct.empty:
        df_rank_struct["_cname"] = df_rank_struct["country"].map(lambda n: cname(n, lang))
        ascending = rank_ind in INVERSE_INDICATORS
        top10 = df_rank_struct.sort_values(rank_ind, ascending=ascending).head(10)
        bottom10 = df_rank_struct.sort_values(rank_ind, ascending=not ascending).head(10)
        r1, r2 = st.columns(2)
        with r1:
            fig_top = px.bar(top10, x="_cname", y=rank_ind, color="_cname", color_discrete_sequence=px.colors.qualitative.Set2, labels={"_cname": "", rank_ind: ind_label(rank_ind, lang)}, title=t("top10", lang, ind=ind_label(rank_ind, lang), y=latest_year))
            fig_top.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10), height=380)
            st.plotly_chart(fig_top, width="stretch")
        with r2:
            fig_bot = px.bar(bottom10, x="_cname", y=rank_ind, color="_cname", color_discrete_sequence=px.colors.qualitative.Pastel1, labels={"_cname": "", rank_ind: ind_label(rank_ind, lang)}, title=t("bottom10", lang, ind=ind_label(rank_ind, lang), y=latest_year))
            fig_bot.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10), height=380)
            st.plotly_chart(fig_bot, width="stretch")

# ── TAB 6: DATA EXPLORER ────────────────────────────────────────────────────
with tab_data:
    d1, d2, d3, d4 = st.columns(4)
    with d1: search = st.text_input(t("search_country", lang), "")
    with d2: filter_reg = st.multiselect(t("filter_region", lang), ALL_REGIONS, default=[], key="dt_reg", format_func=lambda x: t(x, lang))
    with d3: data_year = st.selectbox(t("year_label", lang), sorted(sel_years, reverse=True), index=0, key="dt_yr")
    with d4:
        pestel_options = ["all"] + PESTEL_PILLAR_ORDER
        pestel_choice = st.selectbox(t("pestel_pillar_label", lang), pestel_options, format_func=lambda x: t("pestel_all", lang) if x == "all" else t(PESTEL_LABEL_KEYS[x], lang), index=0)
        
    df_view = df[df["year"] == data_year].copy()
    if search: df_view = df_view[df_view["country"].str.contains(search, case=False, na=False)]
    if filter_reg: df_view = df_view[df_view["region"].isin(filter_reg)]
    
    if pestel_choice == "all": selected_keys = [k for k in INDICATOR_KEYS if k in df_view.columns]
    else: selected_keys = [k for k in PESTEL_INDICATORS[pestel_choice] if k in df_view.columns]
    
    display_cols = ["country", "region", "income_group"] + selected_keys
    label_mapping = {k: ind_label(k, lang) for k in INDICATOR_KEYS}
    label_mapping.update({"country": t("col_country", lang), "region": t("col_region", lang), "income_group": t("income_level", lang)})
    df_display = df_view[display_cols].rename(columns=label_mapping).reset_index(drop=True)
    df_display.index += 1
    country_col = t("col_country", lang)
    if country_col in df_display.columns: df_display[country_col] = df_display[country_col].map(lambda n: cname(n, lang))
    st.caption(t("showing", lang, n=len(df_display), y=data_year))
    
    all_indicator_keys = [k for k in INDICATOR_KEYS if k in df_view.columns]
    num_cols = [label_mapping[k] for k in all_indicator_keys if label_mapping[k] in df_display.columns]
    inverse_labels = {ind_label(k, lang) for k in INVERSE_INDICATORS if k in INDICATOR_KEYS}
    pos_cols = [c for c in num_cols if c not in inverse_labels]
    neg_cols = [c for c in num_cols if c in inverse_labels]
    NULL_STYLE = "background-color: #f1f5f9; color: #94a3b8; font-style: italic;"
    
    def _is_null(val) -> bool:
        if val is None: return True
        if isinstance(val, float) and np.isnan(val): return True
        try:
            if pd.isna(val): return True
        except (TypeError, ValueError): pass
        if isinstance(val, str) and val.strip() in ("", "nan", "None", "NA", "N/A"): return True
        return False

    def gradient_skip_nulls(series: pd.Series, cmap: str = "YlGnBu") -> list:
        numeric = pd.to_numeric(series, errors="coerce")
        valid = numeric.dropna()
        if valid.empty: return [NULL_STYLE] * len(series)
        vmin, vmax = valid.min(), valid.max()
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        cmap_fn = plt.get_cmap(cmap)
        result = []
        for val in numeric:
            if pd.isna(val): result.append(NULL_STYLE)
            else:
                rgba = cmap_fn(norm(val))
                bg = mcolors.to_hex(rgba)
                lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                fg = "#0f172a" if lum > 0.45 else "#ffffff"
                result.append(f"background-color: {bg}; color: {fg}; font-weight: 500;")
        return result

    def style_income_group(val) -> str:
        if _is_null(val): return NULL_STYLE
        s_lower = str(val).lower()
        hi_labels = {t("High income", "en").lower(), t("High income", "fr").lower()}
        um_labels = {t("Upper middle income", "en").lower(), t("Upper middle income", "fr").lower()}
        lm_labels = {t("Lower middle income", "en").lower(), t("Lower middle income", "fr").lower()}
        lo_labels = {t("Low income", "en").lower(), t("Low income", "fr").lower()}
        if any(l in s_lower for l in hi_labels) or "high" in s_lower: return "background-color:#d1fae5;color:#065f46;font-weight:600;"
        if any(l in s_lower for l in um_labels) or "upper" in s_lower: return "background-color:#fef3c7;color:#92400e;font-weight:600;"
        if any(l in s_lower for l in lm_labels) or "lower" in s_lower: return "background-color:#ffedd5;color:#9a3412;font-weight:600;"
        if any(l in s_lower for l in lo_labels) or s_lower == "low income": return "background-color:#fee2e2;color:#991b1b;font-weight:600;"
        return ""

    def style_text_cells(val) -> str: return NULL_STYLE if _is_null(val) else ""

    styled_df = df_display.style
    for col in pos_cols: styled_df = styled_df.apply(gradient_skip_nulls, cmap="YlGnBu", subset=[col], axis=0)
    for col in neg_cols: styled_df = styled_df.apply(gradient_skip_nulls, cmap="YlOrRd", subset=[col], axis=0)
    income_col = label_mapping.get("income_group", "")
    if income_col and income_col in df_display.columns: styled_df = styled_df.map(style_income_group, subset=[income_col])
    text_cols = [c for c in df_display.columns if c not in num_cols and c != income_col]
    if text_cols: styled_df = styled_df.map(style_text_cells, subset=text_cols)
    if num_cols: styled_df = styled_df.format("{:,.2f}", subset=num_cols, na_rep="—")
    st.dataframe(styled_df, width="stretch", height=520)
    
    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(t("export_csv", lang, n=len(df_display), y=data_year), data=csv, file_name=f"world_economic_{data_year}.csv", mime="text/csv")

# ── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.caption(t("footer", lang))