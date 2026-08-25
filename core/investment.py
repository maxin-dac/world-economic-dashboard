

"""Investment attractiveness score, red flags, CAGR.
Thin compatibility layer: re-exports from core.analytics so both
import paths (core.analytics / core.investment) work identically."""
from core.analytics import (
    compute_investment_score,
    detect_red_flags,
    compute_cagr,
    INVESTMENT_INDICATORS,
)

__all__ = ["compute_investment_score", "detect_red_flags", "compute_cagr", "INVESTMENT_INDICATORS"]
from core.constants import INVERSE_INDICATORS as _GI
INVESTMENT_INVERSE = set(_GI) & set(INVESTMENT_INDICATORS)
