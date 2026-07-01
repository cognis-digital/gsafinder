"""Scenario 15 - closed notices sink to the bottom.

A perfect-fit notice that already closed is worthless today. gsafinder applies a
hard penalty to notices past their response date, so they fall below live leads
of lesser fit. This demo runs the deadline-triage fixture, isolates the closed
notice, and shows both the negative `days_left` and the CLOSED penalty in its
reasons.
"""
from _common import rule, run_survey


def main() -> None:
    rule("CLOSED-NOTICE PENALTY  -  past deadlines sink below live leads")

    ranked = run_survey("11-deadline-triage")
    closed = [r for r in ranked if r.days_left is not None and r.days_left < 0]
    live = [r for r in ranked if r.days_left is None or r.days_left >= 0]

    print(f"\nlive notices: {len(live)}    closed notices: {len(closed)}\n")
    for r in closed:
        print(f"   CLOSED  {r.opportunity.notice_id}  {r.days_left}d  score={r.score:.1f}")
        for reason in r.reasons:
            print(f"      - {reason}")

    assert closed, "fixture should contain a closed notice"
    c = closed[0]
    assert any("CLOSED" in x for x in c.reasons), "closed notice needs a CLOSED reason"
    # a closed notice never outranks the top live lead
    assert ranked[0].days_left is None or ranked[0].days_left >= 0

    print("\nThe closed notice carries the penalty in its own reasons and never")
    print("tops the board — the team's attention stays on what it can still win.")


if __name__ == "__main__":
    main()
