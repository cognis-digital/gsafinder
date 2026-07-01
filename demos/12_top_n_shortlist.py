"""Scenario 12 - a top-N shortlist for the stand-up.

A capture lead wants the three best leads for the morning stand-up, not the full
board. The CLI's `--top N` trims the ranked list after scoring, so the shortlist
is always the highest-fit N. This demo runs the same batch with and without
`--top` and shows the shortlist is exactly the head of the full ranking.
"""
import io
import json
import os
from contextlib import redirect_stdout

from _common import rule

from gsafinder.cli import main as cli_main

DEMOS = os.path.dirname(os.path.abspath(__file__))


def _run(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(args)
    assert rc == 0, f"CLI returned {rc}"
    return json.loads(buf.getvalue())


def main() -> None:
    rule("TOP-N SHORTLIST  -  the best three for the stand-up")

    opps = os.path.join(DEMOS, "09-multi-agency-cyber", "opportunities.json")
    profile = os.path.join(DEMOS, "09-multi-agency-cyber", "profile.json")
    base = ["survey", opps, "-p", profile, "--format", "json"]

    full = _run(base)
    top3 = _run(base + ["--top", "3"])

    print(f"\nfull ranking : {full['count']} notices")
    print(f"--top 3      : {top3['count']} notices")
    assert top3["count"] == 3

    full_ids = [r["notice_id"] for r in full["results"]]
    top_ids = [r["notice_id"] for r in top3["results"]]
    print("\nshortlist (in rank order):")
    for r in top3["results"]:
        print(f"   {r['score']:>5.1f}  {r['notice_id']}  {r['title'][:44]}")

    assert top_ids == full_ids[:3], "top-N must be the head of the full ranking"
    print("\nThe shortlist is exactly the top of the full board — trimmed after")
    print("scoring, so you never lose a high-fit lead to an arbitrary cut.")


if __name__ == "__main__":
    main()
