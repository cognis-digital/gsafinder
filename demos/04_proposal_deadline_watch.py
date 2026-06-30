"""Scenario 4 - proposal teams.

A proposal shop is bound by the clock. A high-fit notice that closes in three
days outranks a perfect-fit notice that already closed. gsafinder bakes that
into the score: an urgency bonus for notices due soon and a hard penalty for
closed notices. This demo runs the deadline-triage fixture and sorts the day's
work into "respond now", "on the radar", and "too late", straight from the real
``days_left`` and scoring reasons.
"""
from _common import rule, run_survey


def main() -> None:
    rule("PROPOSAL DEADLINE WATCH  -  respond now / on the radar / too late")

    ranked = run_survey("11-deadline-triage")

    urgent, radar, closed = [], [], []
    for r in ranked:
        dl = r.days_left
        if dl is not None and dl < 0:
            closed.append(r)
        elif dl is not None and dl <= 7:
            urgent.append(r)
        else:
            radar.append(r)

    def _show(bucket, label):
        print(f"\n{label} ({len(bucket)}):")
        if not bucket:
            print("   (none)")
        for r in bucket:
            dl = r.days_left
            when = "closed" if dl is None or dl < 0 else f"{dl}d left"
            print(f"   {r.opportunity.notice_id:<16} {when:>9}  score={r.score:>5.1f}"
                  f"  {r.opportunity.title[:40]}")

    _show(urgent, "RESPOND NOW  (<= 7 days, urgency bonus applied)")
    _show(radar, "ON THE RADAR (more runway)")
    _show(closed, "TOO LATE     (closed, penalized)")

    if urgent:
        top = urgent[0]
        print(f"\nThe team's clock-driven priority is {top.opportunity.notice_id} —")
        print("   " + "; ".join(top.reasons))


if __name__ == "__main__":
    main()
