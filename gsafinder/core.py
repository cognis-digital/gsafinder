"""Core engine for GSAFINDER.

Real scoring logic over federal opportunity records. No network, no stubs.

An opportunity record (SAM.gov / eBuy / FedConnect normalized) looks like:
    {
        "notice_id": "SP4701-26-R-0042",
        "title": "Cloud Hosting and Managed Services",
        "agency": "GSA FAS",
        "naics": "518210",
        "set_aside": "SDVOSB",        # or TOTAL_SB, 8A, WOSB, NONE, ...
        "sins": ["54151S", "518210C"],  # GSA Schedule SINs referenced
        "response_due": "2026-06-20",   # ISO date
        "posted": "2026-06-02",
        "description": "...",
        "source": "eBuy"               # SAM | eBuy | FedConnect
    }

A vendor profile looks like:
    {
        "name": "Acme Federal LLC",
        "naics": ["518210", "541512"],
        "sins": ["54151S"],
        "set_asides": ["SDVOSB", "TOTAL_SB"],
        "keywords": ["cloud", "cybersecurity", "zero trust"]
    }
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

# Set-aside types that a small business is generically eligible for when it
# holds the corresponding socioeconomic certification. A profile listing one
# of these is also eligible for the broader categories it subsumes.
_SET_ASIDE_IMPLIES = {
    "SDVOSB": {"SDVOSB", "VOSB", "TOTAL_SB", "SB"},
    "VOSB": {"VOSB", "TOTAL_SB", "SB"},
    "8A": {"8A", "TOTAL_SB", "SB"},
    "WOSB": {"WOSB", "TOTAL_SB", "SB"},
    "EDWOSB": {"EDWOSB", "WOSB", "TOTAL_SB", "SB"},
    "HUBZONE": {"HUBZONE", "TOTAL_SB", "SB"},
    "TOTAL_SB": {"TOTAL_SB", "SB"},
    "SB": {"SB"},
}

# Open competition values that anyone may bid.
_OPEN_SET_ASIDES = {"", "NONE", "FULL_AND_OPEN", "FAO", "UNRESTRICTED"}


def _norm(value: str) -> str:
    return (value or "").strip().upper()


@dataclass
class Opportunity:
    notice_id: str
    title: str
    agency: str = ""
    naics: str = ""
    set_aside: str = ""
    sins: list[str] = field(default_factory=list)
    response_due: str = ""
    posted: str = ""
    description: str = ""
    source: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Opportunity":
        if not d.get("notice_id"):
            raise ValueError("opportunity record missing 'notice_id'")
        if not d.get("title"):
            raise ValueError(f"opportunity {d.get('notice_id')!r} missing 'title'")
        sins = d.get("sins") or []
        if isinstance(sins, str):
            sins = [s.strip() for s in sins.split(",") if s.strip()]
        return cls(
            notice_id=str(d["notice_id"]),
            title=str(d["title"]),
            agency=str(d.get("agency", "")),
            naics=str(d.get("naics", "")),
            set_aside=str(d.get("set_aside", "")),
            sins=[str(s) for s in sins],
            response_due=str(d.get("response_due", "")),
            posted=str(d.get("posted", "")),
            description=str(d.get("description", "")),
            source=str(d.get("source", "")),
        )


@dataclass
class VendorProfile:
    name: str = "vendor"
    naics: list[str] = field(default_factory=list)
    sins: list[str] = field(default_factory=list)
    set_asides: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VendorProfile":
        return cls(
            name=str(d.get("name", "vendor")),
            naics=[str(x) for x in (d.get("naics") or [])],
            sins=[str(x) for x in (d.get("sins") or [])],
            set_asides=[str(x) for x in (d.get("set_asides") or [])],
            keywords=[str(x) for x in (d.get("keywords") or [])],
        )

    def eligible_set_asides(self) -> set[str]:
        """All set-aside codes this vendor may bid, expanded via implications."""
        out: set[str] = set(_OPEN_SET_ASIDES)
        for sa in self.set_asides:
            out |= _SET_ASIDE_IMPLIES.get(_norm(sa), {_norm(sa)})
        return out


@dataclass
class ScoredOpportunity:
    opportunity: Opportunity
    score: float
    eligible: bool
    reasons: list[str]
    days_left: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "notice_id": self.opportunity.notice_id,
            "title": self.opportunity.title,
            "agency": self.opportunity.agency,
            "source": self.opportunity.source,
            "naics": self.opportunity.naics,
            "set_aside": self.opportunity.set_aside,
            "sins": self.opportunity.sins,
            "response_due": self.opportunity.response_due,
            "days_left": self.days_left,
            "score": round(self.score, 1),
            "eligible": self.eligible,
            "reasons": self.reasons,
        }


def _parse_date(value: str) -> _dt.date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return _dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def days_until(value: str, today: _dt.date | None = None) -> int | None:
    """Whole days from `today` until an ISO/US date string, or None if unparseable."""
    due = _parse_date(value)
    if due is None:
        return None
    today = today or _dt.date.today()
    return (due - today).days


def _keyword_hits(opp: Opportunity, keywords: Iterable[str]) -> list[str]:
    haystack = f"{opp.title}\n{opp.description}".lower()
    hits = []
    for kw in keywords:
        kw_l = kw.strip().lower()
        if not kw_l:
            continue
        # whole-word/phrase match so "AI" doesn't match "maintain"
        if re.search(r"(?<!\w)" + re.escape(kw_l) + r"(?!\w)", haystack):
            hits.append(kw)
    return hits


def score_opportunity(
    opp: Opportunity,
    profile: VendorProfile,
    today: _dt.date | None = None,
) -> ScoredOpportunity:
    """Score one opportunity against a vendor profile.

    Scoring (0-100 base, plus urgency bonus):
      NAICS exact match ............ +35
      SIN overlap .................. +25 (capped)
      set-aside eligibility ........ +15 (required; ineligible => score 0)
      keyword relevance ............ up to +25
      urgency (open & due soon) .... up to +10 bonus
    """
    reasons: list[str] = []
    profile_naics = {n.strip() for n in profile.naics if n.strip()}
    eligible_sa = profile.eligible_set_asides()
    opp_sa = _norm(opp.set_aside) or "NONE"

    # Eligibility gate.
    eligible = opp_sa in eligible_sa
    if not eligible:
        reasons.append(f"INELIGIBLE: set-aside {opp_sa} not held by vendor")
        days_left = days_until(opp.response_due, today)
        return ScoredOpportunity(opp, 0.0, False, reasons, days_left)

    score = 0.0

    if opp.naics and opp.naics in profile_naics:
        score += 35
        reasons.append(f"NAICS {opp.naics} matches vendor capability")
    elif opp.naics:
        reasons.append(f"NAICS {opp.naics} outside vendor codes")

    profile_sins = {s.strip().upper() for s in profile.sins if s.strip()}
    opp_sins = {s.strip().upper() for s in opp.sins if s.strip()}
    sin_overlap = sorted(profile_sins & opp_sins)
    if sin_overlap:
        score += min(25, 12.5 * len(sin_overlap))
        reasons.append("SIN match: " + ", ".join(sin_overlap))

    if opp_sa in _OPEN_SET_ASIDES:
        reasons.append("open competition (full & open)")
    else:
        score += 15
        reasons.append(f"set-aside eligible: {opp_sa}")

    hits = _keyword_hits(opp, profile.keywords)
    if hits:
        score += min(25, 8.0 * len(hits))
        reasons.append("keyword hits: " + ", ".join(hits))

    days_left = days_until(opp.response_due, today)
    if days_left is not None:
        if days_left < 0:
            reasons.append(f"CLOSED {abs(days_left)}d ago")
            score = max(0.0, score - 30)
        elif days_left <= 7:
            score += 10
            reasons.append(f"urgent: {days_left}d to respond")
        elif days_left <= 14:
            score += 5
            reasons.append(f"{days_left}d to respond")
        else:
            reasons.append(f"{days_left}d to respond")

    return ScoredOpportunity(opp, score, True, reasons, days_left)


def survey(
    opportunities: Iterable[Opportunity],
    profile: VendorProfile,
    min_score: float = 0.0,
    eligible_only: bool = False,
    today: _dt.date | None = None,
) -> list[ScoredOpportunity]:
    """Score and rank a batch of opportunities (highest score first)."""
    scored = [score_opportunity(o, profile, today) for o in opportunities]
    results = [
        s
        for s in scored
        if s.score >= min_score and (s.eligible or not eligible_only)
    ]
    results.sort(
        key=lambda s: (s.score, -(s.days_left if s.days_left is not None else 9999)),
        reverse=True,
    )
    return results


def load_opportunities(path: str) -> list[Opportunity]:
    """Load opportunities from a JSON file (list, or {\"opportunities\": [...]})."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("opportunities", data.get("results", []))
    if not isinstance(data, list):
        raise ValueError("opportunities file must be a JSON list or contain one")
    return [Opportunity.from_dict(d) for d in data]


def load_profile(path: str) -> VendorProfile:
    """Load a vendor profile from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("profile file must be a JSON object")
    return VendorProfile.from_dict(data)
