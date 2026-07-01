"""Scenario 6 - the disciplined no-bid.

The most valuable answer a capture tool can give is often "none of these."
A HUBZone-only logistics vendor opens a pull where every notice is restricted to
a set-aside it does not hold. gsafinder's eligibility gate should return an empty
*eligible* set rather than tempt the team with leads it legally cannot bid. This
demo runs that walk-away case and shows the gate rejecting all three notices.
"""
from _common import print_ranked, rule, run_survey


def main() -> None:
    rule("NO-BID WALKAWAY  -  when the honest answer is 'none of these'")

    ranked = run_survey("12-all-ineligible")
    eligible = [r for r in ranked if r.eligible]
    blocked = [r for r in ranked if not r.eligible]

    print(f"\nToday's pull: {len(ranked)} notice(s).")
    print(f"   eligible to bid: {len(eligible)}")
    print(f"   blocked by set-aside: {len(blocked)}\n")

    print_ranked(ranked)

    print("\nEvery notice is a no-bid — the HUBZone vendor holds no cert that")
    print("covers SDVOSB, WOSB, or 8(a). The gate's rationale, per notice:")
    for r in blocked:
        print(f"   x {r.opportunity.notice_id}  {r.opportunity.set_aside:<8}  {r.reasons[0]}")

    # eligible-only view is what a scheduled scan would forward downstream
    scan = run_survey("12-all-ineligible", eligible_only=True)
    assert scan == [], "eligible-only view should be empty"
    print("\nWith --eligible-only the forwarded set is empty: the team walks away")
    print("today and spends zero minutes on notices it cannot legally pursue.")


if __name__ == "__main__":
    main()
