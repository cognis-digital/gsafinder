"""Tests for CSV export, version resolution, and the bundled demo scenarios.

No network. Runs the real CLI / core against every demo's real input files.
"""
import csv
import datetime as dt
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsafinder import TOOL_VERSION  # noqa: E402
from gsafinder.cli import main  # noqa: E402
from gsafinder.core import (  # noqa: E402
    CSV_COLUMNS,
    Opportunity,
    VendorProfile,
    load_opportunities,
    load_profile,
    survey,
    to_csv,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS = os.path.join(ROOT, "demos")
TODAY = dt.date(2026, 6, 21)

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


class TestVersion(unittest.TestCase):
    def test_version_matches_version_file(self):
        with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
            expected = fh.read().strip()
        self.assertEqual(TOOL_VERSION, expected)


class TestCsv(unittest.TestCase):
    def _scored(self):
        opps = [
            _opp(
                notice_id="GOOD",
                title="Zero Trust Cloud",
                set_aside="SDVOSB",
                sins=["54151S"],
                response_due="2026-06-25",
                description="cybersecurity cloud",
            ),
            _opp(notice_id="OPEN", set_aside="NONE", naics="999999"),
        ]
        return survey(opps, PROFILE, today=TODAY)

    def test_csv_has_header_and_rows(self):
        out = to_csv(self._scored())
        rows = list(csv.reader(io.StringIO(out)))
        self.assertEqual(rows[0], CSV_COLUMNS)
        self.assertEqual(len(rows), 3)  # header + 2 records

    def test_csv_roundtrips_via_dictreader(self):
        out = to_csv(self._scored())
        records = list(csv.DictReader(io.StringIO(out)))
        first = records[0]
        self.assertEqual(first["notice_id"], "GOOD")
        self.assertEqual(first["eligible"], "yes")
        # list fields are pipe-joined and stay in one cell
        self.assertIn("|", first["reasons"])

    def test_csv_empty_is_header_only(self):
        out = to_csv([])
        rows = list(csv.reader(io.StringIO(out)))
        self.assertEqual(rows, [CSV_COLUMNS])

    def test_cli_csv_format_runs(self):
        opps = os.path.join(DEMOS, "01-basic", "opportunities.json")
        profile = os.path.join(DEMOS, "01-basic", "profile.json")
        rc = main(["survey", opps, "-p", profile, "--format", "csv"])
        self.assertEqual(rc, 0)


class TestDemoScenarios(unittest.TestCase):
    """Every real-format demo must load, score, and behave as its SCENARIO says."""

    def _run(self, demo):
        d = os.path.join(DEMOS, demo)
        opps = load_opportunities(os.path.join(d, "opportunities.json"))
        profile = load_profile(os.path.join(d, "profile.json"))
        return survey(opps, profile, today=TODAY)

    REAL_DEMOS = [
        "01-basic",
        "04-full-and-open-it",
        "05-wosb-staffing",
        "06-8a-graduate",
        "07-hubzone-construction",
        "08-csv-pipeline",
        "09-multi-agency-cyber",
        "10-keyword-noise",
        "11-deadline-triage",
    ]

    def test_all_real_demos_load_and_score(self):
        for demo in self.REAL_DEMOS:
            ranked = self._run(demo)
            self.assertTrue(ranked, f"{demo} produced no scored results")

    def test_full_and_open_vendor_blocked_from_setasides(self):
        ranked = {r.opportunity.notice_id: r for r in self._run("04-full-and-open-it")}
        # vendor holds no certs -> set-aside notices are ineligible, score 0
        self.assertFalse(ranked["W52P1J26R0099"].eligible)
        self.assertEqual(ranked["GS00Q26WOSB0007"].score, 0.0)
        # full-and-open IT job is the top lead
        top = self._run("04-full-and-open-it")[0]
        self.assertEqual(top.opportunity.notice_id, "47QTCA26R0011")

    def test_edwosb_ladder(self):
        ranked = {r.opportunity.notice_id: r for r in self._run("05-wosb-staffing")}
        self.assertTrue(ranked["GS02Q26WOSB0044"].eligible)  # WOSB by implication
        self.assertTrue(ranked["47QRAA26R0203"].eligible)  # Total SB by implication
        self.assertFalse(ranked["SP470026R8801"].eligible)  # SDVOSB not covered

    def test_8a_vendor_blocked_from_hubzone(self):
        ranked = {r.opportunity.notice_id: r for r in self._run("06-8a-graduate")}
        self.assertFalse(ranked["GS35F26HUB0021"].eligible)
        self.assertEqual(self._run("06-8a-graduate")[0].opportunity.notice_id, "47QFCA26R0050")

    def test_hubzone_scores_without_sins(self):
        ranked = {r.opportunity.notice_id: r for r in self._run("07-hubzone-construction")}
        top = ranked["W912DR26R0024"]
        self.assertTrue(top.eligible)
        self.assertGreater(top.score, 0)
        # no SIN reasons since the vendor holds none
        self.assertFalse(any("SIN match" in r for r in top.reasons))

    def test_keyword_whole_word_no_false_positive(self):
        ranked = {r.opportunity.notice_id: r for r in self._run("10-keyword-noise")}
        # grounds-maintenance text has "maintain"/"remediation" but no real AI/ML hit
        grounds = ranked["W912DY26R0050"]
        self.assertFalse(any("keyword hits" in r for r in grounds.reasons))
        # the genuine AI/ML notice does hit
        ai = ranked["47QTCA26R0160"]
        self.assertTrue(any("keyword hits" in r for r in ai.reasons))

    def test_deadline_urgency_and_closed(self):
        ranked = {r.opportunity.notice_id: r for r in self._run("11-deadline-triage")}
        self.assertTrue(any("urgent" in r for r in ranked["47QTCA26R0180"].reasons))
        self.assertTrue(any("CLOSED" in r for r in ranked["HSHQDC26R00120"].reasons))


if __name__ == "__main__":
    unittest.main()
