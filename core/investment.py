INVESTMENT_INDICATORS = {'gdp_per_capita': 0.25, 'gdp_growth_pct': 0.15, 'inflation': 0.1, 'debt_pct_gdp': 0.1, 'unemployment_pct': 0.1, 'current_account_pct_gdp': 0.1, 'fdi_net_pct_gdp': 0.1, 'trade_pct_gdp': 0.1}

"""Investment attractiveness score, red flags, CAGR.
Thin compatibility layer: re-exports from core.analytics so both
import paths (core.analytics / core.investment) work identically."""
from core.analytics import (
    compute_investment_score,
    detect_red_flags,
    compute_cagr,
)

__all__ = ["compute_investment_score", "detect_red_flags", "compute_cagr"]
from core.constants import INVERSE_INDICATORS as _GI
INVESTMENT_INVERSE = set(_GI) & set(INVESTMENT_INDICATORS)
