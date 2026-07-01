"""Scenario 16 - the three urgency tiers.

gsafinder's deadline scoring has three live tiers: <=7 days earns the full
urgency bonus, 8-14 days a partial bonus, and beyond that no bonus. This demo
runs the deadline-triage fixture and sorts the live notices into those tiers,
showing the bonus reflected in each notice's reasons.
"""
from _common import rule, run_survey


def _tier(days):
    if days is None or days < 0:
        return "closed"
    if days <= 7:
        return "urgent (<=7d, +10)"
    if days <= 14:
        return "soon (8-14d, +5)"
    return "runway (>14d, +0)"


def main() -> None:
    rule("URGENCY BUCKETS  -  <=7d / 8-14d / runway")

    ranked = run_survey("11-deadline-triage")
    buckets: dict[str, list] = {}
    for r in ranked:
        buckets.setdefault(_tier(r.days_left), []).append(r)

    for tier in ("urgent (<=7d, +10)", "soon (8-14d, +5)", "runway (>14d, +0)", "closed"):
        rows = buckets.get(tier, [])
        print(f"\n{tier}  ({len(rows)}):")
        for r in rows:
            days = "--" if r.days_left is None else f"{r.days_left}d"
            print(f"   {r.opportunity.notice_id:<16} {days:>5}  score={r.score:>5.1f}")

    urgent = buckets.get("urgent (<=7d, +10)", [])
    if urgent:
        assert any("urgent" in x for x in urgent[0].reasons)
    print("\nEach live notice lands in exactly one tier, and the reasons string")
    print("names the bonus applied — the clock is legible at a glance.")


if __name__ == "__main__":
    main()
