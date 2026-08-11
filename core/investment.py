"""Investment attractiveness score, red flags, CAGR.
Thin compatibility layer: re-exports from core.analytics so both
import paths (core.analytics / core.investment) work identically."""
from core.analytics import (
    compute_investment_score,
    detect_red_flags,
    compute_cagr,
)

__all__ = ["compute_investment_score", "detect_red_flags", "compute_cagr"]
