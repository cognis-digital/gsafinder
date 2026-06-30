# Demos

Two complementary sets of demos ship in [`../demos/`](../demos/), both **offline**
— they drive the real `gsafinder` API against bundled real-format sample
fixtures and never call SAM.gov / eBuy / FedConnect.

## Narrated Python scenarios

Five runnable scenarios, each written for a different federal-sales audience.
Every scenario loads a bundled fixture, runs the real `survey()` ranker, prints
narrated output, and exits 0 — so they double as smoke tests.

```bash
PYTHONUTF8=1 python demos/run_all.py            # all five, end to end
PYTHONUTF8=1 python demos/03_bd_pipeline_export.py   # or just one
```

| # | Scenario | Audience | What it shows |
|---|---|---|---|
| 1 | [`01_capture_manager_triage`](../demos/01_capture_manager_triage.py) | GovCon capture managers | Rank the morning's pull, surface the top lead's scoring rationale, and flag the no-bids the eligibility gate caught |
| 2 | [`02_small_biz_eligibility`](../demos/02_small_biz_eligibility.py) | Small-business federal sellers | The set-aside ladder across three vendors — where EDWOSB / 8(a) / HUBZone certs open or close the door |
| 3 | [`03_bd_pipeline_export`](../demos/03_bd_pipeline_export.py) | BD teams | A 5-agency cyber batch filtered to eligible high-score leads and rendered as the real `to_csv` pipeline export |
| 4 | [`04_proposal_deadline_watch`](../demos/04_proposal_deadline_watch.py) | Proposal teams | Sort the day's work into respond-now / on-the-radar / too-late from the urgency bonus and closed-notice penalty |
| 5 | [`05_keyword_precision`](../demos/05_keyword_precision.py) | Capture analysts | Whole-word keyword matching — "AI"/"ML" hit real notices but never the "maintain"/"remediation" noise |

## Real-format fixture demos

Nine fixture directories (`demos/01-basic`, `demos/04-full-and-open-it`, …) each
hold a `SCENARIO.md`, an `opportunities.json`, and a `profile.json` in the
tool's exact input format. Run the CLI straight against any of them:

```bash
gsafinder survey demos/01-basic/opportunities.json -p demos/01-basic/profile.json
```

The Python scenarios above reuse these same fixtures, so the two sets stay in
lock-step. See the [README Demos table](../README.md#demos) for the full list.

---

Both sets are covered under `pytest` (`tests/test_demos_scenarios.py` runs every
Python scenario's `main()` and asserts exit 0; `tests/test_csv_and_demos.py`
loads and scores every fixture).
