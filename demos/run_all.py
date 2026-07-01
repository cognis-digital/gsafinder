"""Run every gsafinder demo scenario end to end.

    python demos/run_all.py

Each scenario is independent and drives the real ``gsafinder`` API against the
bundled real-format sample fixtures (offline — no SAM.gov / eBuy calls), so they
can be run in any order or on their own. They print narrated output and exit 0,
so they double as smoke tests.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCENARIOS = [
    "01_capture_manager_triage",
    "02_small_biz_eligibility",
    "03_bd_pipeline_export",
    "04_proposal_deadline_watch",
    "05_keyword_precision",
    "06_no_bid_walkaway",
    "07_deadline_tie_break",
    "08_sin_overlap_cap",
    "09_messy_date_feeds",
    "10_cli_json_output",
    "11_cli_csv_pipeline",
    "12_top_n_shortlist",
    "13_score_floor_filter",
    "14_set_aside_ladder_walk",
    "15_closed_notice_penalty",
    "16_urgency_buckets",
    "17_multi_agency_spread",
    "18_table_render",
    "19_cli_exit_codes",
    "20_malformed_input_handling",
]


def main() -> None:
    for name in SCENARIOS:
        mod = importlib.import_module(name)
        mod.main()
    print("\n" + "=" * 72)
    print("  All demo scenarios completed.")
    print("=" * 72)


if __name__ == "__main__":
    main()
