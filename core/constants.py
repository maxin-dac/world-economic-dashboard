"""Static configuration: orders, colors, geo style, PESTEL mapping."""
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
    "environmental": ["cereal_yield_kg_per_ha", "electric_power_losses_pct", "electricity_access_pct", "pm25_air_pollution"],
    "legal": ["control_of_corruption", "corruption_perception_index", "regulatory_quality", "rule_of_law_index", "transparency_corruption_score", "voice_accountability", "women_parliament_pct"],
}
INDICATOR_TO_PILLAR = {ind: p for p, inds in PESTEL_INDICATORS.items() for ind in inds}
CORE_INDICATORS = {ind: ind for group in PESTEL_INDICATORS.values() for ind in group}
INVERSE_INDICATORS = {"inflation", "cpi_index_raw", "debt_pct_gdp", "imports_pct_gdp", "unemployment_pct", "youth_unemployment_pct", "pm25_air_pollution", "military_expenditure_pct_gdp", "military_expenditure_pct_govt", "gini_index", "under5_mortality_per_1000", "fertility_rate", "electric_power_losses_pct"}

INDICATOR_COLORSCALE = {"gdp_per_capita": "Viridis", "gdp_growth_pct": "RdYlGn", "inflation": "YlOrRd", "debt_pct_gdp": "YlOrRd", "agriculture_pct": "YlGn", "industry_pct": "PuBu", "services_pct": "Plasma", "life_expectancy": "RdYlGn", "hdi": "RdYlGn", "unemployment_pct": "YlOrRd", "internet_users_pct": "Cividis", "govt_effectiveness_index": "RdYlGn"}

def get_expressive_colorscale(indicator_key: str) -> str:
    return INDICATOR_COLORSCALE.get(indicator_key, "YlOrRd" if indicator_key in INVERSE_INDICATORS else "Viridis")
