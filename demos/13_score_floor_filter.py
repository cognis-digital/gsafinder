"""Scenario 13 - a score floor to cut the noise.

Not every eligible notice is worth a bid decision. `--min-score` drops anything
below a fit threshold so the team sees only real leads. This demo runs a batch
at several floors and shows the result set shrinking monotonically as the bar
rises — and that the survivors are always the highest-scoring notices.
"""
import io
import json
import os
from contextlib import redirect_stdout

from _common import rule

from gsafinder.cli import main as cli_main

DEMOS = os.path.dirname(os.path.abspath(__file__))


def _count(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(args)
    assert rc == 0
    return json.loads(buf.getvalue())


def main() -> None:
    rule("SCORE-FLOOR FILTER  -  only leads above the bar")

    opps = os.path.join(DEMOS, "09-multi-agency-cyber", "opportunities.json")
    profile = os.path.join(DEMOS, "09-multi-agency-cyber", "profile.json")
    base = ["survey", opps, "-p", profile, "--format", "json"]

    counts = {}
    for floor in (0, 40, 60, 80, 200):
        payload = _count(base + ["--min-score", str(floor)])
        counts[floor] = payload["count"]
        lowest = min((r["score"] for r in payload["results"]), default=None)
        print(f"   min-score {floor:>3}  ->  {payload['count']} lead(s)"
              f"  (lowest surviving score: {lowest})")

    ordered = [counts[f] for f in (0, 40, 60, 80, 200)]
    assert ordered == sorted(ordered, reverse=True), "raising the floor cannot add leads"
    assert counts[200] == 0, "an impossible floor yields no leads"

    print("\nRaising the floor only ever removes leads, never adds them, and an")
    print("unreachable floor cleanly yields zero — the team dials in its own bar.")


if __name__ == "__main__":
    main()
