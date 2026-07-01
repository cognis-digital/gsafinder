"""Error-path, loader, CSV, and CLI-contract tests.

No network. Covers malformed input handling (bad JSON, wrong shapes, missing
required fields), the file loaders' envelope forms, CSV structure/escaping, and
the CLI's exit-code contract and output formats.
"""
import csv
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    set_asides=["SDVOSB"], naics=["518210"], sins=["54151S"], keywords=["cloud"]
)


def _opp(**kw):
    base = dict(notice_id="N", title="T", naics="518210", set_aside="NONE")
    base.update(kw)
    return Opportunity.from_dict(base)


def _write(dirpath, name, text):
    p = os.path.join(dirpath, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class TestOpportunityValidation(unittest.TestCase):
    def test_missing_notice_id_raises(self):
        with self.assertRaises(ValueError):
            Opportunity.from_dict({"title": "x"})

    def test_missing_title_raises(self):
        with self.assertRaises(ValueError):
            Opportunity.from_dict({"notice_id": "x"})

    def test_non_dict_record_raises_valueerror(self):
        with self.assertRaises(ValueError):
            Opportunity.from_dict("not a dict")

    def test_non_dict_record_not_attributeerror(self):
        # regression: used to raise an opaque AttributeError
        try:
            Opportunity.from_dict(["a", "list"])
        except ValueError:
            pass
        except AttributeError:
            self.fail("non-dict record should raise ValueError, not AttributeError")

    def test_notice_id_coerced_to_str(self):
        o = Opportunity.from_dict({"notice_id": 12345, "title": "t"})
        self.assertEqual(o.notice_id, "12345")

    def test_sins_string_split(self):
        o = Opportunity.from_dict(
            {"notice_id": "n", "title": "t", "sins": "a, b ,c"}
        )
        self.assertEqual(o.sins, ["a", "b", "c"])

    def test_sins_missing_defaults_empty(self):
        o = Opportunity.from_dict({"notice_id": "n", "title": "t"})
        self.assertEqual(o.sins, [])

    def test_defaults_for_optional_fields(self):
        o = Opportunity.from_dict({"notice_id": "n", "title": "t"})
        self.assertEqual(o.agency, "")
        self.assertEqual(o.set_aside, "")


class TestProfileValidation(unittest.TestCase):
    def test_non_dict_profile_raises(self):
        with self.assertRaises(ValueError):
            VendorProfile.from_dict(["a", "b"])

    def test_empty_profile_has_defaults(self):
        p = VendorProfile.from_dict({})
        self.assertEqual(p.name, "vendor")
        self.assertEqual(p.naics, [])

    def test_profile_coerces_list_items_to_str(self):
        p = VendorProfile.from_dict({"naics": [518210, 541512]})
        self.assertEqual(p.naics, ["518210", "541512"])


class TestLoaders(unittest.TestCase):
    def test_load_opportunities_bare_list(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "o.json", json.dumps(
                [{"notice_id": "n", "title": "t"}]))
            opps = load_opportunities(p)
            self.assertEqual(len(opps), 1)

    def test_load_opportunities_opportunities_key(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "o.json", json.dumps(
                {"opportunities": [{"notice_id": "n", "title": "t"}]}))
            self.assertEqual(len(load_opportunities(p)), 1)

    def test_load_opportunities_results_key(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "o.json", json.dumps(
                {"results": [{"notice_id": "n", "title": "t"}]}))
            self.assertEqual(len(load_opportunities(p)), 1)

    def test_load_opportunities_bad_json_raises_jsondecode(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "o.json", "{ not json")
            with self.assertRaises(json.JSONDecodeError):
                load_opportunities(p)

    def test_load_opportunities_wrong_toplevel_type_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "o.json", json.dumps("a string"))
            with self.assertRaises(ValueError):
                load_opportunities(p)

    def test_load_opportunities_non_dict_element_raises_valueerror(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "o.json", json.dumps(["notadict"]))
            with self.assertRaises(ValueError):
                load_opportunities(p)

    def test_load_opportunities_missing_file_raises_oserror(self):
        with self.assertRaises(OSError):
            load_opportunities("/no/such/file/here.json")

    def test_load_profile_object(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "p.json", json.dumps({"name": "X", "naics": ["1"]}))
            prof = load_profile(p)
            self.assertEqual(prof.name, "X")

    def test_load_profile_wrong_type_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "p.json", json.dumps(["a", "b"]))
            with self.assertRaises(ValueError):
                load_profile(p)

    def test_load_profile_bad_json_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "p.json", "{bad")
            with self.assertRaises(json.JSONDecodeError):
                load_profile(p)


class TestCsv(unittest.TestCase):
    def _scored(self):
        opps = [
            _opp(notice_id="GOOD", title="cloud", set_aside="SDVOSB",
                 sins=["54151S"], response_due="2026-07-01"),
            _opp(notice_id="OPEN", set_aside="NONE", naics="999"),
        ]
        return survey(opps, PROFILE, today=TODAY)

    def test_header_matches_columns(self):
        rows = list(csv.reader(io.StringIO(to_csv(self._scored()))))
        self.assertEqual(rows[0], CSV_COLUMNS)

    def test_row_count(self):
        rows = list(csv.reader(io.StringIO(to_csv(self._scored()))))
        self.assertEqual(len(rows), 3)

    def test_empty_is_header_only(self):
        rows = list(csv.reader(io.StringIO(to_csv([]))))
        self.assertEqual(rows, [CSV_COLUMNS])

    def test_dictreader_roundtrip(self):
        recs = list(csv.DictReader(io.StringIO(to_csv(self._scored()))))
        self.assertEqual(recs[0]["notice_id"], "GOOD")
        self.assertEqual(recs[0]["eligible"], "yes")

    def test_list_fields_pipe_joined(self):
        recs = list(csv.DictReader(io.StringIO(to_csv(self._scored()))))
        self.assertIn("|", recs[0]["reasons"])

    def test_ineligible_row_marked_no(self):
        opps = [_opp(notice_id="X", set_aside="8A")]
        recs = list(csv.DictReader(io.StringIO(to_csv(survey(opps, PROFILE, today=TODAY)))))
        self.assertEqual(recs[0]["eligible"], "no")

    def test_score_formatted_one_decimal(self):
        recs = list(csv.DictReader(io.StringIO(to_csv(self._scored()))))
        self.assertRegex(recs[0]["score"], r"^\d+\.\d$")

    def test_comma_in_title_is_quoted_not_split(self):
        opps = [_opp(notice_id="C", title="Cloud, Hosting, and Support",
                     set_aside="SDVOSB")]
        out = to_csv(survey(opps, PROFILE, today=TODAY))
        recs = list(csv.DictReader(io.StringIO(out)))
        self.assertEqual(recs[0]["title"], "Cloud, Hosting, and Support")

    def test_none_days_left_is_empty_cell(self):
        opps = [_opp(notice_id="U", set_aside="SDVOSB", response_due="")]
        recs = list(csv.DictReader(io.StringIO(to_csv(survey(opps, PROFILE, today=TODAY)))))
        self.assertEqual(recs[0]["days_left"], "")


class TestCliExitCodes(unittest.TestCase):
    def setUp(self):
        self.opps = os.path.join(DEMOS, "01-basic", "opportunities.json")
        self.profile = os.path.join(DEMOS, "01-basic", "profile.json")

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_clean_survey_exits_0(self):
        rc, _, _ = self._run(["survey", self.opps, "-p", self.profile, "--format", "json"])
        self.assertEqual(rc, 0)

    def test_no_command_exits_1(self):
        rc, _, _ = self._run([])
        self.assertEqual(rc, 1)

    def test_missing_file_exits_2(self):
        rc, _, err = self._run(["survey", "/no/such.json", "-p", self.profile])
        self.assertEqual(rc, 2)
        self.assertIn("error:", err)

    def test_invalid_json_exits_2_with_message(self):
        with tempfile.TemporaryDirectory() as d:
            bad = _write(d, "bad.json", "{ not json")
            rc, _, err = self._run(["survey", bad, "-p", self.profile])
        self.assertEqual(rc, 2)
        self.assertIn("invalid JSON", err)

    def test_non_dict_record_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            bad = _write(d, "bad.json", json.dumps(["x"]))
            rc, _, err = self._run(["survey", bad, "-p", self.profile])
        self.assertEqual(rc, 2)
        self.assertIn("error:", err)

    def test_missing_notice_id_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            bad = _write(d, "bad.json", json.dumps({"opportunities": [{"title": "t"}]}))
            rc, _, err = self._run(["survey", bad, "-p", self.profile])
        self.assertEqual(rc, 2)


class TestCliOutputFormats(unittest.TestCase):
    def setUp(self):
        self.opps = os.path.join(DEMOS, "01-basic", "opportunities.json")
        self.profile = os.path.join(DEMOS, "01-basic", "profile.json")

    def _run(self, argv):
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(argv)
        return rc, out.getvalue()

    def test_json_output_is_parseable_envelope(self):
        rc, out = self._run(["survey", self.opps, "-p", self.profile, "--format", "json"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(set(payload), {"vendor", "count", "results"})
        self.assertEqual(payload["count"], len(payload["results"]))

    def test_csv_output_has_header(self):
        rc, out = self._run(["survey", self.opps, "-p", self.profile, "--format", "csv"])
        self.assertEqual(rc, 0)
        rows = list(csv.reader(io.StringIO(out)))
        self.assertEqual(rows[0], CSV_COLUMNS)

    def test_table_output_has_header(self):
        rc, out = self._run(["survey", self.opps, "-p", self.profile])
        self.assertEqual(rc, 0)
        self.assertIn("SCORE", out)
        self.assertIn("TITLE", out)

    def test_top_limits_results(self):
        rc, out = self._run(
            ["survey", self.opps, "-p", self.profile, "--format", "json", "--top", "2"]
        )
        self.assertEqual(json.loads(out)["count"], 2)

    def test_top_zero_means_no_limit(self):
        rc, full = self._run(["survey", self.opps, "-p", self.profile, "--format", "json"])
        rc, zero = self._run(
            ["survey", self.opps, "-p", self.profile, "--format", "json", "--top", "0"]
        )
        self.assertEqual(json.loads(full)["count"], json.loads(zero)["count"])

    def test_min_score_filters_via_cli(self):
        rc, out = self._run(
            ["survey", self.opps, "-p", self.profile, "--format", "json",
             "--min-score", "200"]
        )
        self.assertEqual(json.loads(out)["count"], 0)

    def test_eligible_only_via_cli(self):
        rc, out = self._run(
            ["survey", self.opps, "-p", self.profile, "--format", "json",
             "--eligible-only"]
        )
        payload = json.loads(out)
        self.assertTrue(all(r["eligible"] for r in payload["results"]))

    def test_empty_table_message(self):
        rc, out = self._run(
            ["survey", self.opps, "-p", self.profile, "--min-score", "200"]
        )
        self.assertIn("No matching opportunities", out)


if __name__ == "__main__":
    unittest.main()
