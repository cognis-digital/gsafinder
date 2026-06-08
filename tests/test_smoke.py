"""Smoke tests for GSAFINDER. No network."""
import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsafinder import (  # noqa: E402
    TOOL_NAME,
    TOOL_VERSION,
    Opportunity,
    VendorProfile,
    days_until,
    score_opportunity,
    survey,
)
from gsafinder.cli import main  # noqa: E402

TODAY = dt.date(2026, 6, 8)

PROFILE = VendorProfile(
    name="Acme Federal LLC",
    naics=["518210", "541512"],
    sins=["54151S"],
    set_asides=["SDVOSB"],
    keywords=["cloud", "cybersecurity", "zero trust"],
)


def _opp(**kw):
    base = dict(notice_id="N1", title="T", naics="518210", set_aside="NONE")
    base.update(kw)
    return Opportunity.from_dict(base)


class TestMetadata(unittest.TestCase):
    def test_version_exports(self):
        self.assertEqual(TOOL_NAME, "gsafinder")
        self.assertTrue(TOOL_VERSION)


class TestDates(unittest.TestCase):
    def test_days_until(self):
        self.assertEqual(days_until("2026-06-15", TODAY), 7)
        self.assertEqual(days_until("2026-06-01", TODAY), -7)
        self.assertIsNone(days_until("", TODAY))
        self.assertIsNone(days_until("not-a-date", TODAY))
        self.assertEqual(days_until("06/15/2026", TODAY), 7)


class TestEligibility(unittest.TestCase):
    def test_sdvosb_subsumes_total_sb(self):
        opp = _opp(set_aside="TOTAL_SB")
        s = score_opportunity(opp, PROFILE, TODAY)
        self.assertTrue(s.eligible)

    def test_8a_ineligible_scores_zero(self):
        opp = _opp(set_aside="8A")
        s = score_opportunity(opp, PROFILE, TODAY)
        self.assertFalse(s.eligible)
        self.assertEqual(s.score, 0.0)
        self.assertTrue(any("INELIGIBLE" in r for r in s.reasons))

    def test_open_competition_eligible(self):
        opp = _opp(set_aside="NONE")
        self.assertTrue(score_opportunity(opp, PROFILE, TODAY).eligible)


class TestScoring(unittest.TestCase):
    def test_perfect_fit_outscores_offdomain(self):
        good = _opp(
            notice_id="GOOD",
            title="Zero Trust Cloud Migration",
            naics="518210",
            set_aside="SDVOSB",
            sins=["54151S"],
            response_due="2026-06-13",
            description="cybersecurity cloud",
        )
        bad = _opp(
            notice_id="BAD",
            title="Janitorial Services",
            naics="561720",
            set_aside="TOTAL_SB",
            sins=[],
            response_due="2026-07-10",
            description="custodial",
        )
        ranked = survey([bad, good], PROFILE, today=TODAY)
        self.assertEqual(ranked[0].opportunity.notice_id, "GOOD")
        self.assertGreater(ranked[0].score, ranked[1].score)

    def test_naics_match_adds_points(self):
        match = _opp(naics="518210")
        miss = _opp(naics="999999")
        self.assertGreater(
            score_opportunity(match, PROFILE, TODAY).score,
            score_opportunity(miss, PROFILE, TODAY).score,
        )

    def test_closed_penalized(self):
        opp = _opp(naics="518210", set_aside="NONE", response_due="2026-05-01")
        s = score_opportunity(opp, PROFILE, TODAY)
        self.assertTrue(any("CLOSED" in r for r in s.reasons))
        self.assertEqual(s.days_left, -38)

    def test_min_score_filter(self):
        opp = _opp(naics="999999", set_aside="NONE", title="x", description="")
        self.assertEqual(survey([opp], PROFILE, min_score=10, today=TODAY), [])

    def test_eligible_only_filter(self):
        opp = _opp(set_aside="8A")
        self.assertEqual(
            survey([opp], PROFILE, eligible_only=True, today=TODAY), []
        )


class TestValidation(unittest.TestCase):
    def test_missing_notice_id(self):
        with self.assertRaises(ValueError):
            Opportunity.from_dict({"title": "x"})

    def test_missing_title(self):
        with self.assertRaises(ValueError):
            Opportunity.from_dict({"notice_id": "x"})


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "demos",
            "01-basic",
        )
        self.opps = os.path.join(self.dir, "opportunities.json")
        self.profile = os.path.join(self.dir, "profile.json")

    def test_demo_files_exist(self):
        self.assertTrue(os.path.exists(self.opps))
        self.assertTrue(os.path.exists(self.profile))

    def test_cli_json_runs(self):
        rc = main(
            ["survey", self.opps, "-p", self.profile, "--format", "json"]
        )
        self.assertEqual(rc, 0)

    def test_cli_no_command_returns_nonzero(self):
        self.assertEqual(main([]), 1)

    def test_cli_bad_path_returns_nonzero(self):
        rc = main(["survey", "/no/such/file.json", "-p", self.profile])
        self.assertEqual(rc, 2)

    def test_demo_data_parses_and_scores(self):
        with open(self.opps, encoding="utf-8") as fh:
            data = json.load(fh)
        opps = [Opportunity.from_dict(d) for d in data["opportunities"]]
        ranked = survey(opps, PROFILE, today=TODAY)
        self.assertEqual(ranked[0].opportunity.notice_id, "GS-35F-26-CLOUD-0042")
        ineligible = [r for r in ranked if not r.eligible]
        self.assertTrue(any(r.opportunity.set_aside == "8A" for r in ineligible))


if __name__ == "__main__":
    unittest.main()
