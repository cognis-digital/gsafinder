"""Scenario 2 - small-business federal sellers.

A small business living on set-asides needs to know, before it spends a minute
on a notice: *am I even allowed to bid this?* The set-aside ladder is subtle —
an SDVOSB subsumes Total SB, an EDWOSB covers WOSB, an 8(a) does not cover
HUBZone. This demo runs three different vendor profiles against their real
fixtures and shows where each one's certifications open or close the door.
"""
from _common import print_ranked, rule, run_survey


def _eligibility_breakdown(label, fixture):
    print(f"\n{label}")
    ranked = run_survey(fixture)
    eligible = [r for r in ranked if r.eligible]
    blocked = [r for r in ranked if not r.eligible]
    print(f"   may bid: {len(eligible)}    blocked by set-aside: {len(blocked)}")
    for r in blocked:
        print(f"     x {r.opportunity.notice_id}  needs {r.opportunity.set_aside:<8}"
              f"  -> {r.reasons[0]}")
    return ranked


def main() -> None:
    rule("SMALL-BIZ ELIGIBILITY  -  which set-asides can I actually bid?")

    ranked = _eligibility_breakdown(
        "EDWOSB staffing firm (covers WOSB + Total SB, NOT SDVOSB):",
        "05-wosb-staffing",
    )
    _eligibility_breakdown(
        "8(a) analytics firm (covers 8(a) + Total SB, NOT HUBZone):",
        "06-8a-graduate",
    )
    _eligibility_breakdown(
        "HUBZone trades vendor with no GSA SINs (NAICS + keyword only):",
        "07-hubzone-construction",
    )

    print("\nFull ranking for the EDWOSB firm (eligible notices first):\n")
    print_ranked(ranked)

    print("\nEach seller bids only what its certifications actually allow —")
    print("the ladder is applied automatically, so no time is wasted on no-bids.")


if __name__ == "__main__":
    main()
