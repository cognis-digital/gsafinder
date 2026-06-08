"""GSAFINDER - GSA Schedule opportunity surveyor.

Surveys federal solicitation records (SAM.gov, eBuy, FedConnect style)
and scores them for fit against a vendor profile: matching NAICS codes,
GSA Schedule / SIN alignment, set-aside eligibility, keyword relevance,
and response-window urgency.

Standard library only. Zero install.
"""
from .core import (
    Opportunity,
    VendorProfile,
    ScoredOpportunity,
    load_opportunities,
    load_profile,
    survey,
    score_opportunity,
    days_until,
)

TOOL_NAME = "gsafinder"
TOOL_VERSION = "1.0.0"

__all__ = [
    "TOOL_NAME",
    "TOOL_VERSION",
    "Opportunity",
    "VendorProfile",
    "ScoredOpportunity",
    "load_opportunities",
    "load_profile",
    "survey",
    "score_opportunity",
    "days_until",
]
