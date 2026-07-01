# Demos

Two complementary sets of demos ship in [`../demos/`](../demos/), both **offline**
— they drive the real `gsafinder` API against bundled real-format sample
fixtures and never call SAM.gov / eBuy / FedConnect.

## Narrated Python scenarios

Twenty runnable scenarios, each written for a different federal-sales question.
Every scenario loads a bundled fixture (or invokes the real CLI), runs the real
`survey()` ranker, prints narrated output, and exits 0 — so they double as smoke
tests.

```bash
PYTHONUTF8=1 python demos/run_all.py                 # all twenty, end to end
PYTHONUTF8=1 python demos/03_bd_pipeline_export.py   # or just one
```

| # | Scenario | Audience / focus | What it shows |
|---|----------|------------------|---------------|
| 1 | [`01_capture_manager_triage`](../demos/01_capture_manager_triage.py) | Capture managers | Rank the morning's pull, surface the top lead's rationale, flag the no-bids |
| 2 | [`02_small_biz_eligibility`](../demos/02_small_biz_eligibility.py) | Small-business sellers | The set-aside ladder across three vendors |
| 3 | [`03_bd_pipeline_export`](../demos/03_bd_pipeline_export.py) | BD teams | A 5-agency batch filtered to high-score leads, rendered as `to_csv` |
| 4 | [`04_proposal_deadline_watch`](../demos/04_proposal_deadline_watch.py) | Proposal teams | Respond-now / on-the-radar / too-late from the urgency bonus + closed penalty |
| 5 | [`05_keyword_precision`](../demos/05_keyword_precision.py) | Capture analysts | Whole-word keyword matching — "AI" hits AI, never "maintain" |
| 6 | [`06_no_bid_walkaway`](../demos/06_no_bid_walkaway.py) | Discipline | The eligibility gate returning an empty set — the honest no-bid day |
| 7 | [`07_deadline_tie_break`](../demos/07_deadline_tie_break.py) | Ranking contract | Equal-fit leads broken by the nearer deadline |
| 8 | [`08_sin_overlap_cap`](../demos/08_sin_overlap_cap.py) | Scoring internals | SIN overlap rewarded but bounded by the cap |
| 9 | [`09_messy_date_feeds`](../demos/09_messy_date_feeds.py) | Ingest robustness | ISO / US / slash-ISO dates parsed; bad/blank degrade to null, never crash |
| 10 | [`10_cli_json_output`](../demos/10_cli_json_output.py) | Integrators | The stable `{vendor, count, results}` JSON envelope |
| 11 | [`11_cli_csv_pipeline`](../demos/11_cli_csv_pipeline.py) | BD analysts | `--format csv` round-tripping through `csv.DictReader` |
| 12 | [`12_top_n_shortlist`](../demos/12_top_n_shortlist.py) | Capture leads | `--top N` = the head of the full ranking |
| 13 | [`13_score_floor_filter`](../demos/13_score_floor_filter.py) | Noise control | `--min-score` shrinking the set monotonically |
| 14 | [`14_set_aside_ladder_walk`](../demos/14_set_aside_ladder_walk.py) | Eligibility | Every certification's expanded eligibility set |
| 15 | [`15_closed_notice_penalty`](../demos/15_closed_notice_penalty.py) | Proposal teams | Closed notices penalized below live leads |
| 16 | [`16_urgency_buckets`](../demos/16_urgency_buckets.py) | Deadline model | The <=7d / 8-14d / runway tiers |
| 17 | [`17_multi_agency_spread`](../demos/17_multi_agency_spread.py) | BD strategy | One profile's addressable footprint across agencies |
| 18 | [`18_table_render`](../demos/18_table_render.py) | CLI users | The default human-readable table |
| 19 | [`19_cli_exit_codes`](../demos/19_cli_exit_codes.py) | Automation | The 0 / 1 / 2 exit-code contract |
| 20 | [`20_malformed_input_handling`](../demos/20_malformed_input_handling.py) | Robustness | Clear errors + exit 2 on bad input, never a stack trace |

## Real-format fixture demos

Thirteen fixture directories (`demos/01-basic`, `demos/04-full-and-open-it`, …)
each hold a `SCENARIO.md`, an `opportunities.json`, and a `profile.json` in the
tool's exact input format. Run the CLI straight against any of them:

```bash
gsafinder survey demos/01-basic/opportunities.json -p demos/01-basic/profile.json
```

Fixtures: `01-basic`, `04-full-and-open-it`, `05-wosb-staffing`, `06-8a-graduate`,
`07-hubzone-construction`, `08-csv-pipeline`, `09-multi-agency-cyber`,
`10-keyword-noise`, `11-deadline-triage`, `12-all-ineligible`, `13-tie-break`,
`14-sin-overlap`, `17-date-formats`.

The Python scenarios above reuse these same fixtures, so the two sets stay in
lock-step. See the [README Demos table](../README.md#demos) for the full list.

---

Both sets are covered under `pytest`: `tests/test_demos_scenarios.py` runs every
Python scenario's `main()` and asserts exit 0; `tests/test_csv_and_demos.py` and
`tests/test_new_fixtures.py` load and score every fixture and assert its encoded
property.
