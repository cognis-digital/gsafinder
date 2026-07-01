"""Behavioral tests for the added demo fixtures (12-14, 17) and to_dict shape.

No network. Each new fixture encodes a specific scoring or eligibility property;
these assert those properties hold against the real loader + survey path so the
fixtures cannot silently drift.
"""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsafinder.core import (  # noqa: E402
    Opportunity,
    ScoredOpportunity,
    VendorProfile,
    load_opportunities,
    load_profile,
    score_opportunity,
    survey,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS = os.path.join(ROOT, "demos")
TODAY = dt.date(2026, 6, 21)


def _run(demo):
    d = os.path.join(DEMOS, demo)
    opps = load_opportunities(os.path.join(d, "opportunities.json"))
    prof = load_profile(os.path.join(d, "profile.json"))
    return survey(opps, prof, today=TODAY)


class TestAllIneligibleFixture(unittest.TestCase):
    def test_nothing_eligible(self):
        ranked = _run("12-all-ineligible")
        self.assertTrue(all(not r.eligible for r in ranked))

    def test_all_score_zero(self):
        self.assertTrue(all(r.score == 0.0 for r in _run("12-all-ineligible")))

    def test_eligible_only_is_empty(self):
        d = os.path.join(DEMOS, "12-all-ineligible")
        opps = load_opportunities(os.path.join(d, "opportunities.json"))
        prof = load_profile(os.path.join(d, "profile.json"))
        self.assertEqual(survey(opps, prof, eligible_only=True, today=TODAY), [])


class TestTieBreakFixture(unittest.TestCase):
    def test_scores_tie(self):
        ranked = _run("13-tie-break")
        self.assertEqual(ranked[0].score, ranked[1].score)

    def test_sooner_deadline_first(self):
        ranked = _run("13-tie-break")
        self.assertEqual(ranked[0].opportunity.notice_id, "TIE-SOON-0001")
        self.assertLess(ranked[0].days_left, ranked[1].days_left)


class TestSinOverlapFixture(unittest.TestCase):
    def test_sin_bonus_is_capped(self):
        r = {x.opportunity.notice_id: x for x in _run("14-sin-overlap")}
        many, one, none = r["SIN-MANY-0001"], r["SIN-ONE-0002"], r["SIN-NONE-0003"]
        # cap holds: the 3-SIN gap over 1-SIN equals the 1-SIN gap over none
        self.assertEqual(many.score - one.score, one.score - none.score)

    def test_non_overlap_has_no_sin_reason(self):
        r = {x.opportunity.notice_id: x for x in _run("14-sin-overlap")}
        self.assertFalse(any("SIN match" in x for x in r["SIN-NONE-0003"].reasons))


class TestDateFormatsFixture(unittest.TestCase):
    def test_three_dates_parse_two_degrade(self):
        r = {x.opportunity.notice_id: x for x in _run("17-date-formats")}
        parsed = [x for x in r.values() if x.days_left is not None]
        undated = [x for x in r.values() if x.days_left is None]
        self.assertEqual(len(parsed), 3)
        self.assertEqual(len(undated), 2)

    def test_us_format_resolves(self):
        r = {x.opportunity.notice_id: x for x in _run("17-date-formats")}
        self.assertEqual(r["DATE-US-0002"].days_left, 14)

    def test_bad_and_missing_are_none(self):
        r = {x.opportunity.notice_id: x for x in _run("17-date-formats")}
        self.assertIsNone(r["DATE-BAD-0004"].days_left)
        self.assertIsNone(r["DATE-MISSING-0005"].days_left)


class TestScoredToDict(unittest.TestCase):
    PROFILE = VendorProfile(set_asides=["SDVOSB"], naics=["518210"], keywords=["cloud"])

    def _one(self):
        opp = Opportunity.from_dict(
            {"notice_id": "N", "title": "cloud", "naics": "518210",
             "set_aside": "SDVOSB", "sins": ["54151S"], "response_due": "2026-07-01",
             "agency": "GSA", "source": "eBuy"}
        )
        return score_opportunity(opp, self.PROFILE, TODAY)

    def test_to_dict_keys(self):
        d = self._one().to_dict()
        for k in ("notice_id", "title", "agency", "source", "naics", "set_aside",
                  "sins", "response_due", "days_left", "score", "eligible", "reasons"):
            self.assertIn(k, d)

    def test_score_rounded_one_decimal(self):
        d = self._one().to_dict()
        self.assertEqual(d["score"], round(d["score"], 1))

    def test_eligible_is_bool(self):
        self.assertIsInstance(self._one().to_dict()["eligible"], bool)

    def test_reasons_is_list(self):
        self.assertIsInstance(self._one().to_dict()["reasons"], list)

    def test_scored_opportunity_is_dataclass_instance(self):
        self.assertIsInstance(self._one(), ScoredOpportunity)


if __name__ == "__main__":
    unittest.main()
