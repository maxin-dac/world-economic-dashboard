"""Indicator metadata, interpretation and info banners."""
import numpy as np
import pandas as pd
import streamlit as st
from translations import t
from core.constants import INVERSE_INDICATORS
# INDICATOR EXPLANATIONS (bilingual) - key -> (en_desc, en_tip, fr_desc, fr_tip)
# ═══════════════════════════════════════════════════════════════════════════
INDICATOR_INFO = {
    "gdp_per_capita": ("Average economic output per person.", "Higher = wealthier population.", "Production économique moyenne par personne.", "Plus élevé = population plus riche."),
    "gdp_per_capita_ppp": ("GDP per person adjusted for purchasing power.", "Better for comparing living standards.", "PIB par habitant ajusté au pouvoir d'achat.", "Plus pertinent pour comparer les niveaux de vie."),
    "gdp_total_bn": ("Total size of the economy.", "Higher = larger economy (not necessarily richer people).", "Taille totale de l'économie.", "Plus élevé = économie plus grande (pas forcément plus riche par habitant)."),
    "gdp_growth_pct": ("Annual growth rate of the economy.", "Positive = expanding; negative = recession.", "Taux de croissance annuel de l'économie.", "Positif = expansion ; négatif = récession."),
    "gross_fixed_capital_formation_pct_gdp": ("Investment in fixed assets (machinery, infrastructure).", "Higher = more investment.", "Investissement en actifs fixes (machines, infrastructures).", "Plus élevé = plus d'investissement."),
    "trade_openness_pct_gdp": ("Total trade (exports + imports) as a share of GDP.", "Higher = more open economy.", "Commerce total (exports + imports) rapporté au PIB.", "Plus élevé = économie plus ouverte."),
    "cpi_index_raw": ("Consumer Price Index, base 100 in 2010 - measures PRICE levels, NOT corruption.", "100 = 2010 price level; higher = more cumulative inflation since 2010.", "Indice des prix à la consommation, base 100 en 2010 - mesure les PRIX, PAS la corruption.", "100 = niveau des prix de 2010 ; plus élevé = plus d'inflation cumulée depuis 2010."),
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
