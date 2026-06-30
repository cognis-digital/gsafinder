"""Tests for the narrated Python demo scenarios in demos/.

Each scenario drives the real gsafinder API against bundled fixtures (offline)
and must run cleanly to completion. We import each scenario module and call its
main(), asserting it neither raises nor calls sys.exit with a nonzero code.
No network.
"""
import importlib
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS = os.path.join(ROOT, "demos")
sys.path.insert(0, ROOT)
sys.path.insert(0, DEMOS)

SCENARIOS = [
    "01_capture_manager_triage",
    "02_small_biz_eligibility",
    "03_bd_pipeline_export",
    "04_proposal_deadline_watch",
    "05_keyword_precision",
]


class TestDemoCommon(unittest.TestCase):
    def test_run_survey_helper(self):
        _common = importlib.import_module("_common")
        ranked = _common.run_survey("01-basic")
        self.assertTrue(ranked)
        # eligibility gate runs: the 8(a) notice is present but ineligible
        by_id = {r.opportunity.notice_id: r for r in ranked}
        self.assertFalse(by_id["HHS-26-8A-0099"].eligible)

    def test_print_ranked_handles_empty(self):
        _common = importlib.import_module("_common")
        # should not raise on an empty ranking
        _common.print_ranked([])


class TestScenariosRun(unittest.TestCase):
    """Every scenario's main() runs to completion without raising or exiting."""

    def _run(self, name):
        mod = importlib.import_module(name)
        try:
            mod.main()
        except SystemExit as exc:  # a nonzero exit is a failure
            code = exc.code if exc.code is not None else 0
            self.assertEqual(code, 0, f"{name} exited with {code}")

    def test_each_scenario_runs(self):
        for name in SCENARIOS:
            with self.subTest(scenario=name):
                self._run(name)

    def test_run_all_module_lists_every_scenario(self):
        run_all = importlib.import_module("run_all")
        self.assertEqual(run_all.SCENARIOS, SCENARIOS)


if __name__ == "__main__":
    unittest.main()
