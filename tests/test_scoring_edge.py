"""Edge-case and error-path tests for scoring, eligibility, and the ladder.

No network. These exercise the boundaries the smoke tests skip: the set-aside
implication ladder for every certification, the SIN-overlap cap, keyword
whole-word precision, deadline buckets at their exact thresholds, and the
survey() sort/tie-break contract.
"""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsafinder.core import (  # noqa: E402
    Opportunity,
    VendorProfile,
    days_until,
    score_opportunity,
    survey,
)

TODAY = dt.date(2026, 6, 21)


def _opp(**kw):
    base = dict(notice_id="N", title="T", naics="", set_aside="NONE")
    base.update(kw)
    return Opportunity.from_dict(base)


class TestSetAsideLadder(unittest.TestCase):
    """Every certification unlocks exactly the categories it should."""

    def _elig(self, *certs):
        return VendorProfile(set_asides=list(certs)).eligible_set_asides()

    def test_sdvosb_subsumes_vosb_and_sb(self):
        e = self._elig("SDVOSB")
        self.assertIn("SDVOSB", e)
        self.assertIn("VOSB", e)
        self.assertIn("TOTAL_SB", e)
        self.assertIn("SB", e)

    def test_edwosb_subsumes_wosb(self):
        e = self._elig("EDWOSB")
        self.assertIn("WOSB", e)
        self.assertIn("EDWOSB", e)

    def test_edwosb_does_not_reach_sdvosb(self):
        self.assertNotIn("SDVOSB", self._elig("EDWOSB"))

    def test_8a_does_not_reach_hubzone(self):
        self.assertNotIn("HUBZONE", self._elig("8A"))

    def test_8a_does_not_reach_wosb(self):
        self.assertNotIn("WOSB", self._elig("8A"))

    def test_hubzone_reaches_total_sb(self):
        self.assertIn("TOTAL_SB", self._elig("HUBZONE"))

    def test_vosb_does_not_reach_sdvosb(self):
        self.assertNotIn("SDVOSB", self._elig("VOSB"))

    def test_total_sb_only_reaches_sb(self):
        e = self._elig("TOTAL_SB")
        self.assertIn("SB", e)
        self.assertNotIn("SDVOSB", e)
        self.assertNotIn("WOSB", e)

    def test_no_certs_still_allows_open(self):
        e = self._elig()
        self.assertIn("NONE", e)
        self.assertIn("FULL_AND_OPEN", e)
        self.assertNotIn("SDVOSB", e)

    def test_multiple_certs_union(self):
        e = self._elig("SDVOSB", "8A")
        self.assertIn("SDVOSB", e)
        self.assertIn("8A", e)

    def test_unknown_cert_maps_to_itself(self):
        e = self._elig("SBA_MENTOR_PROTEGE")
        self.assertIn("SBA_MENTOR_PROTEGE", e)

    def test_cert_case_insensitive(self):
        self.assertIn("SDVOSB", VendorProfile(set_asides=["sdvosb"]).eligible_set_asides())


class TestEligibilityGate(unittest.TestCase):
    PROFILE = VendorProfile(set_asides=["SDVOSB"], naics=["518210"])

    def test_ineligible_short_circuits_to_zero(self):
        s = score_opportunity(_opp(set_aside="8A", naics="518210"), self.PROFILE, TODAY)
        self.assertFalse(s.eligible)
        self.assertEqual(s.score, 0.0)

    def test_ineligible_still_reports_days_left(self):
        s = score_opportunity(
            _opp(set_aside="8A", response_due="2026-07-01"), self.PROFILE, TODAY
        )
        self.assertEqual(s.days_left, 10)

    def test_ineligible_reason_is_first(self):
        s = score_opportunity(_opp(set_aside="WOSB"), self.PROFILE, TODAY)
        self.assertTrue(s.reasons[0].startswith("INELIGIBLE"))

    def test_empty_set_aside_treated_as_open(self):
        s = score_opportunity(_opp(set_aside=""), self.PROFILE, TODAY)
        self.assertTrue(s.eligible)

    def test_unrestricted_alias_is_open(self):
        for alias in ("UNRESTRICTED", "FULL_AND_OPEN", "FAO"):
            s = score_opportunity(_opp(set_aside=alias), self.PROFILE, TODAY)
            self.assertTrue(s.eligible, alias)

    def test_set_aside_whitespace_normalized(self):
        s = score_opportunity(_opp(set_aside="  sdvosb "), self.PROFILE, TODAY)
        self.assertTrue(s.eligible)


class TestNaicsScoring(unittest.TestCase):
    PROFILE = VendorProfile(set_asides=["SDVOSB"], naics=["518210", "541512"])

    def test_naics_exact_match_adds_35(self):
        s = score_opportunity(_opp(naics="518210", set_aside="NONE"), self.PROFILE, TODAY)
        self.assertEqual(s.score, 35.0)

    def test_naics_miss_adds_nothing(self):
        s = score_opportunity(_opp(naics="999999", set_aside="NONE"), self.PROFILE, TODAY)
        self.assertEqual(s.score, 0.0)

    def test_missing_naics_no_reason(self):
        s = score_opportunity(_opp(naics="", set_aside="NONE"), self.PROFILE, TODAY)
        self.assertFalse(any("NAICS" in r for r in s.reasons))

    def test_naics_miss_records_reason(self):
        s = score_opportunity(_opp(naics="999999", set_aside="NONE"), self.PROFILE, TODAY)
        self.assertTrue(any("outside vendor codes" in r for r in s.reasons))


class TestSinScoring(unittest.TestCase):
    PROFILE = VendorProfile(
        set_asides=["SDVOSB"], sins=["54151S", "54151HACS", "541330ENG"]
    )

    def test_single_sin_adds_12_5(self):
        s = score_opportunity(
            _opp(set_aside="NONE", sins=["54151S"]), self.PROFILE, TODAY
        )
        self.assertEqual(s.score, 12.5)

    def test_two_sins_add_25(self):
        s = score_opportunity(
            _opp(set_aside="NONE", sins=["54151S", "54151HACS"]), self.PROFILE, TODAY
        )
        self.assertEqual(s.score, 25.0)

    def test_three_sins_capped_at_25(self):
        s = score_opportunity(
            _opp(set_aside="NONE", sins=["54151S", "54151HACS", "541330ENG"]),
            self.PROFILE,
            TODAY,
        )
        self.assertEqual(s.score, 25.0)

    def test_sin_match_case_insensitive(self):
        s = score_opportunity(
            _opp(set_aside="NONE", sins=["54151s"]), self.PROFILE, TODAY
        )
        self.assertTrue(any("SIN match" in r for r in s.reasons))

    def test_non_overlapping_sin_no_reason(self):
        s = score_opportunity(
            _opp(set_aside="NONE", sins=["99999Z"]), self.PROFILE, TODAY
        )
        self.assertFalse(any("SIN match" in r for r in s.reasons))

    def test_sins_from_comma_string(self):
        opp = Opportunity.from_dict(
            {"notice_id": "N", "title": "T", "set_aside": "NONE",
             "sins": "54151S, 54151HACS"}
        )
        s = score_opportunity(opp, self.PROFILE, TODAY)
        self.assertEqual(s.score, 25.0)


class TestKeywordScoring(unittest.TestCase):
    PROFILE = VendorProfile(set_asides=["SDVOSB"], keywords=["AI", "cloud", "zero trust"])

    def test_whole_word_hit(self):
        s = score_opportunity(
            _opp(set_aside="NONE", title="AI research"), self.PROFILE, TODAY
        )
        self.assertTrue(any("keyword hits" in r for r in s.reasons))

    def test_substring_is_not_a_hit(self):
        s = score_opportunity(
            _opp(set_aside="NONE", title="maintain the airfield", description="retain"),
            self.PROFILE,
            TODAY,
        )
        self.assertFalse(any("keyword hits" in r for r in s.reasons))

    def test_phrase_keyword_matches(self):
        s = score_opportunity(
            _opp(set_aside="NONE", description="a zero trust rollout"),
            self.PROFILE,
            TODAY,
        )
        self.assertTrue(any("zero trust" in r for r in s.reasons))

    def test_keyword_hit_is_case_insensitive(self):
        s = score_opportunity(
            _opp(set_aside="NONE", title="CLOUD hosting"), self.PROFILE, TODAY
        )
        self.assertTrue(any("keyword hits" in r for r in s.reasons))

    def test_keyword_bonus_capped_at_25(self):
        prof = VendorProfile(set_asides=["SDVOSB"], keywords=["a", "b", "c", "d", "e"])
        s = score_opportunity(
            _opp(set_aside="NONE", title="a b c d e"), prof, TODAY
        )
        # 5 hits * 8 = 40 raw, capped to 25
        self.assertEqual(s.score, 25.0)

    def test_matches_in_description_too(self):
        s = score_opportunity(
            _opp(set_aside="NONE", title="Services", description="cloud migration"),
            self.PROFILE,
            TODAY,
        )
        self.assertTrue(any("cloud" in r for r in s.reasons))

    def test_empty_keyword_ignored(self):
        prof = VendorProfile(set_asides=["SDVOSB"], keywords=["", "  "])
        s = score_opportunity(_opp(set_aside="NONE", title="anything"), prof, TODAY)
        self.assertFalse(any("keyword hits" in r for r in s.reasons))


class TestDeadlineBuckets(unittest.TestCase):
    PROFILE = VendorProfile(set_asides=["SDVOSB"], naics=["518210"])

    def _score(self, due):
        return score_opportunity(
            _opp(naics="518210", set_aside="NONE", response_due=due), self.PROFILE, TODAY
        )

    def test_urgent_bucket_adds_10(self):
        # 5 days out -> 35 (naics) + 10 (urgent)
        self.assertEqual(self._score("2026-06-26").score, 45.0)

    def test_urgent_boundary_7_days(self):
        s = self._score("2026-06-28")  # exactly 7
        self.assertTrue(any("urgent" in r for r in s.reasons))

    def test_soon_boundary_8_days(self):
        s = self._score("2026-06-29")  # 8 days -> soon bucket
        self.assertEqual(s.score, 40.0)  # 35 + 5

    def test_soon_boundary_14_days(self):
        s = self._score("2026-07-05")  # exactly 14
        self.assertEqual(s.score, 40.0)

    def test_runway_15_days_no_bonus(self):
        s = self._score("2026-07-06")  # 15 days -> no bonus
        self.assertEqual(s.score, 35.0)

    def test_closed_penalized_30(self):
        # 35 - 30 = 5
        s = self._score("2026-06-01")
        self.assertEqual(s.score, 5.0)
        self.assertTrue(any("CLOSED" in r for r in s.reasons))

    def test_closed_floored_at_zero(self):
        prof = VendorProfile(set_asides=["SDVOSB"])  # no naics
        s = score_opportunity(
            _opp(set_aside="NONE", naics="", response_due="2026-01-01"), prof, TODAY
        )
        self.assertEqual(s.score, 0.0)

    def test_unparseable_date_no_bonus_no_penalty(self):
        s = self._score("not a date")
        self.assertIsNone(s.days_left)
        self.assertEqual(s.score, 35.0)

    def test_missing_date_no_bonus(self):
        s = self._score("")
        self.assertIsNone(s.days_left)
        self.assertEqual(s.score, 35.0)


class TestSurveySortContract(unittest.TestCase):
    PROFILE = VendorProfile(set_asides=["SDVOSB"], naics=["518210"], keywords=["cloud"])

    def test_sorted_by_score_desc(self):
        opps = [
            _opp(notice_id="LOW", naics="999", set_aside="NONE"),
            _opp(notice_id="HIGH", naics="518210", set_aside="NONE", title="cloud"),
        ]
        ranked = survey(opps, self.PROFILE, today=TODAY)
        self.assertEqual([r.opportunity.notice_id for r in ranked], ["HIGH", "LOW"])

    def test_tie_broken_by_nearer_deadline(self):
        opps = [
            _opp(notice_id="LATE", naics="518210", set_aside="NONE",
                 title="cloud", response_due="2026-08-30"),
            _opp(notice_id="SOON", naics="518210", set_aside="NONE",
                 title="cloud", response_due="2026-07-25"),
        ]
        ranked = survey(opps, self.PROFILE, today=TODAY)
        self.assertEqual(ranked[0].opportunity.notice_id, "SOON")
        self.assertEqual(ranked[0].score, ranked[1].score)

    def test_min_score_filters(self):
        opps = [_opp(notice_id="X", naics="999", set_aside="NONE")]
        self.assertEqual(survey(opps, self.PROFILE, min_score=1, today=TODAY), [])

    def test_min_score_zero_keeps_zero_scores(self):
        opps = [_opp(notice_id="Z", set_aside="8A")]  # ineligible, score 0
        ranked = survey(opps, self.PROFILE, min_score=0, today=TODAY)
        self.assertEqual(len(ranked), 1)

    def test_eligible_only_drops_ineligible(self):
        opps = [
            _opp(notice_id="OK", naics="518210", set_aside="SDVOSB"),
            _opp(notice_id="NO", set_aside="8A"),
        ]
        ranked = survey(opps, self.PROFILE, eligible_only=True, today=TODAY)
        self.assertEqual([r.opportunity.notice_id for r in ranked], ["OK"])

    def test_empty_input_returns_empty(self):
        self.assertEqual(survey([], self.PROFILE, today=TODAY), [])

    def test_none_days_left_sorts_last_within_score(self):
        opps = [
            _opp(notice_id="DATED", naics="518210", set_aside="NONE",
                 title="cloud", response_due="2026-08-01"),
            _opp(notice_id="UNDATED", naics="518210", set_aside="NONE",
                 title="cloud", response_due=""),
        ]
        ranked = survey(opps, self.PROFILE, today=TODAY)
        # equal score; dated one (finite days) should precede undated (treated far)
        self.assertEqual(ranked[0].opportunity.notice_id, "DATED")


class TestDaysUntil(unittest.TestCase):
    def test_iso(self):
        self.assertEqual(days_until("2026-06-28", TODAY), 7)

    def test_us_format(self):
        self.assertEqual(days_until("06/28/2026", TODAY), 7)

    def test_slash_iso(self):
        self.assertEqual(days_until("2026/06/28", TODAY), 7)

    def test_negative_for_past(self):
        self.assertEqual(days_until("2026-06-01", TODAY), -20)

    def test_none_for_empty(self):
        self.assertIsNone(days_until("", TODAY))

    def test_none_for_garbage(self):
        self.assertIsNone(days_until("soon-ish", TODAY))

    def test_none_for_impossible_date(self):
        self.assertIsNone(days_until("2026-13-45", TODAY))

    def test_zero_when_due_today(self):
        self.assertEqual(days_until("2026-06-21", TODAY), 0)


if __name__ == "__main__":
    unittest.main()
