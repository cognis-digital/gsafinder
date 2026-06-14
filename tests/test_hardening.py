"""Hardening tests: error paths, edge cases, and input validation."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsafinder.core import (  # noqa: E402
    Opportunity,
    VendorProfile,
    load_opportunities,
    survey,
)
from gsafinder.cli import main  # noqa: E402


class TestOpportunityFromDictHardening(unittest.TestCase):
    """Opportunity.from_dict must raise clear errors on bad input."""

    def test_non_dict_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Opportunity.from_dict("not-a-dict")
        self.assertIn("JSON object", str(ctx.exception))

    def test_integer_item_raises_value_error(self):
        with self.assertRaises(ValueError):
            Opportunity.from_dict(42)

    def test_none_description_coerced_to_empty_string(self):
        opp = Opportunity.from_dict({"notice_id": "N1", "title": "T", "description": None})
        self.assertEqual(opp.description, "")

    def test_none_naics_coerced_to_empty_string(self):
        opp = Opportunity.from_dict({"notice_id": "N1", "title": "T", "naics": None})
        self.assertEqual(opp.naics, "")

    def test_sins_non_list_non_string_raises(self):
        with self.assertRaises(ValueError) as ctx:
            Opportunity.from_dict({"notice_id": "N1", "title": "T", "sins": 99})
        self.assertIn("sins", str(ctx.exception))


class TestVendorProfileFromDictHardening(unittest.TestCase):
    """VendorProfile.from_dict must reject non-dict input and bad field types."""

    def test_non_dict_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            VendorProfile.from_dict([1, 2, 3])
        self.assertIn("JSON object", str(ctx.exception))

    def test_naics_as_integer_raises(self):
        with self.assertRaises(ValueError) as ctx:
            VendorProfile.from_dict({"naics": 12345})
        self.assertIn("naics", str(ctx.exception))

    def test_none_name_falls_back_to_default(self):
        p = VendorProfile.from_dict({"name": None})
        self.assertEqual(p.name, "vendor")

    def test_empty_profile_gives_open_eligibility(self):
        p = VendorProfile.from_dict({})
        self.assertIn("NONE", p.eligible_set_asides())
        self.assertIn("", p.eligible_set_asides())


class TestLoadOpportunitiesHardening(unittest.TestCase):
    """load_opportunities must produce clear errors for bad files."""

    def _write_json(self, data) -> str:
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(data, fh)
        fh.close()
        return fh.name

    def _write_raw(self, text: str) -> str:
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        fh.write(text)
        fh.close()
        return fh.name

    def tearDown(self):
        # Temp files cleaned up per-test via try/finally in each test.
        pass

    def test_non_dict_item_in_list_raises_value_error(self):
        path = self._write_json([{"notice_id": "X1", "title": "T"}, "bad-item"])
        try:
            with self.assertRaises(ValueError) as ctx:
                load_opportunities(path)
            self.assertIn("opportunities[1]", str(ctx.exception))
        finally:
            os.unlink(path)

    def test_integer_item_in_list_raises_value_error(self):
        path = self._write_json([42])
        try:
            with self.assertRaises(ValueError):
                load_opportunities(path)
        finally:
            os.unlink(path)

    def test_malformed_json_raises_json_decode_error(self):
        path = self._write_raw("{bad json")
        try:
            import json as _json
            with self.assertRaises(_json.JSONDecodeError):
                load_opportunities(path)
        finally:
            os.unlink(path)

    def test_missing_file_raises_os_error(self):
        with self.assertRaises(OSError):
            load_opportunities("/no/such/path/opps.json")

    def test_empty_list_returns_empty(self):
        path = self._write_json([])
        try:
            result = load_opportunities(path)
            self.assertEqual(result, [])
        finally:
            os.unlink(path)


class TestCLIHardening(unittest.TestCase):
    """CLI must return non-zero exit codes for bad inputs and invalid flags."""

    def setUp(self):
        demo = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "demos", "01-basic",
        )
        self.opps = os.path.join(demo, "opportunities.json")
        self.profile = os.path.join(demo, "profile.json")

    def test_negative_top_returns_exit_2(self):
        rc = main(["survey", self.opps, "-p", self.profile, "--top", "-1"])
        self.assertEqual(rc, 2)

    def test_negative_min_score_returns_exit_2(self):
        rc = main(["survey", self.opps, "-p", self.profile, "--min-score", "-5"])
        self.assertEqual(rc, 2)

    def test_non_dict_item_in_opps_file_returns_exit_2(self):
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump([{"notice_id": "X1", "title": "T"}, "bad"], fh)
        fh.close()
        try:
            rc = main(["survey", fh.name, "-p", self.profile])
            self.assertEqual(rc, 2)
        finally:
            os.unlink(fh.name)

    def test_profile_as_list_returns_exit_2(self):
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump([1, 2, 3], fh)
        fh.close()
        try:
            rc = main(["survey", self.opps, "-p", fh.name])
            self.assertEqual(rc, 2)
        finally:
            os.unlink(fh.name)


class TestSurveyEdgeCases(unittest.TestCase):
    """survey() must handle edge cases gracefully."""

    def test_empty_opportunities(self):
        result = survey([], VendorProfile())
        self.assertEqual(result, [])

    def test_all_ineligible_eligible_only(self):
        from gsafinder.core import Opportunity
        opp = Opportunity.from_dict({"notice_id": "N1", "title": "T", "set_aside": "8A"})
        result = survey([opp], VendorProfile(), eligible_only=True)
        self.assertEqual(result, [])

    def test_min_score_zero_includes_everything_eligible(self):
        opp = Opportunity.from_dict({"notice_id": "N1", "title": "T", "set_aside": "NONE"})
        result = survey([opp], VendorProfile(), min_score=0.0)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
