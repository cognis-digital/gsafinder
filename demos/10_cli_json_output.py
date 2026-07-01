"""Scenario 10 - the CLI as a JSON data source.

Downstream tooling (a CRM sync, a dashboard, a notebook) wants structured data,
not a table. gsafinder's CLI emits a stable JSON envelope — vendor name, count,
and a results array — that any consumer can parse. This demo invokes the real
CLI `main()` with `--format json`, captures stdout, parses it back, and checks
the envelope shape and that the eligibility gate is reflected in the payload.
"""
import io
import json
import os
from contextlib import redirect_stdout

from _common import rule

from gsafinder.cli import main as cli_main

DEMOS = os.path.dirname(os.path.abspath(__file__))


def main_demo() -> None:
    rule("CLI JSON OUTPUT  -  a stable envelope for downstream tooling")

    opps = os.path.join(DEMOS, "09-multi-agency-cyber", "opportunities.json")
    profile = os.path.join(DEMOS, "09-multi-agency-cyber", "profile.json")

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(["survey", opps, "-p", profile, "--format", "json"])
    assert rc == 0, f"CLI returned {rc}"

    payload = json.loads(buf.getvalue())
    print(f"\nvendor : {payload['vendor']}")
    print(f"count  : {payload['count']}")
    print(f"keys   : {sorted(payload.keys())}")

    assert set(payload) == {"vendor", "count", "results"}
    assert payload["count"] == len(payload["results"])

    first = payload["results"][0]
    print(f"\ntop result: {first['notice_id']}  score={first['score']}  "
          f"eligible={first['eligible']}")
    print("result keys:", sorted(first.keys()))

    # every result carries an explicit eligibility flag and rationale
    assert all("eligible" in r and "reasons" in r for r in payload["results"])
    print("\nParsed cleanly — the envelope is safe to pipe into a CRM or notebook.")


def main() -> None:  # run_all / test entry point
    main_demo()


if __name__ == "__main__":
    main()
