"""Shared helpers for the gsafinder demo scenarios.

Every scenario drives the tool's *real* API (``gsafinder.core``) against the
bundled, real-format sample fixtures under ``demos/<name>/``. Nothing here
touches the network: SAM.gov / eBuy / FedConnect are never called. The fixtures
are normalized opportunity records in the exact shape the loader expects, so the
demos exercise the same code path as ``gsafinder survey``.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys

# allow `python demos/NN_name.py` from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsafinder.core import (  # noqa: E402
    ScoredOpportunity,
    load_opportunities,
    load_profile,
    survey,
    to_csv,
)

DEMOS_DIR = os.path.dirname(os.path.abspath(__file__))

# A fixed "today" so the narrated output (days-left, urgency) is reproducible.
# The bundled fixtures use mid-2026 response dates.
TODAY = _dt.date(2026, 6, 21)


def load_fixture(name: str):
    """Load the (opportunities, profile) pair for a bundled demo fixture."""
    d = os.path.join(DEMOS_DIR, name)
    opps = load_opportunities(os.path.join(d, "opportunities.json"))
    profile = load_profile(os.path.join(d, "profile.json"))
    return opps, profile


def run_survey(name: str, **kwargs) -> list[ScoredOpportunity]:
    """Load a fixture and run the real ``survey()`` ranker against it."""
    opps, profile = load_fixture(name)
    return survey(opps, profile, today=TODAY, **kwargs)


def rule(title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def print_ranked(ranked: list[ScoredOpportunity], limit: int | None = None) -> None:
    """Narrated table of scored opportunities (mirrors the CLI table)."""
    rows = ranked if limit is None else ranked[:limit]
    if not rows:
        print("   (no matching opportunities)")
        return
    hdr = f"   {'SCORE':>5}  {'ELIG':<4}  {'DAYS':>4}  {'SET-ASIDE':<10}  TITLE"
    print(hdr)
    print("   " + "-" * (len(hdr) - 3))
    for r in rows:
        d = r.to_dict()
        days = "--" if d["days_left"] is None else str(d["days_left"])
        elig = "yes" if d["eligible"] else "no"
        print(
            f"   {d['score']:>5.1f}  {elig:<4}  {days:>4}  "
            f"{(d['set_aside'] or 'open'):<10}  {d['title'][:46]}"
        )


__all__ = [
    "TODAY",
    "ScoredOpportunity",
    "load_fixture",
    "run_survey",
    "rule",
    "print_ranked",
    "to_csv",
]
