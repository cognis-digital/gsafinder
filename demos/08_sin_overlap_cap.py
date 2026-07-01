"""Scenario 8 - schedule breadth, bounded.

Every GSA Schedule SIN a notice shares with the vendor adds points, but the SIN
contribution is capped so a wide multi-SIN vehicle can't dominate on breadth
alone. This demo runs three otherwise-identical notices — three shared SINs, one
shared SIN, and none — and shows the cap holding the multi-SIN lead to a bounded
advantage.
"""
from _common import print_ranked, rule, run_survey


def _sin_reason(r):
    return next((x for x in r.reasons if x.startswith("SIN match")), None)


def main() -> None:
    rule("SIN OVERLAP CAP  -  breadth helps, but it's bounded")

    ranked = {r.opportunity.notice_id: r for r in run_survey("14-sin-overlap")}
    print_ranked(list(ranked.values()))

    many = ranked["SIN-MANY-0001"]
    one = ranked["SIN-ONE-0002"]
    none = ranked["SIN-NONE-0003"]

    print("\nSIN contribution per notice:")
    print(f"   {many.opportunity.notice_id}  3 shared SINs -> {_sin_reason(many)}")
    print(f"   {one.opportunity.notice_id}  1 shared SIN  -> {_sin_reason(one)}")
    print(f"   {none.opportunity.notice_id}  0 shared SINs -> {_sin_reason(none) or 'no SIN reason'}")

    # 3 SINs would be 37.5 raw but is capped at 25; the gap over the 1-SIN
    # notice (12.5) is therefore also 12.5, not 25.
    assert many.score - one.score == one.score - none.score, "SIN bonus should be capped"
    assert _sin_reason(none) is None, "a non-overlapping SIN earns no reason"

    print("\nThe 3-SIN notice leads, but its SIN bonus is clamped: the gap to the")
    print("1-SIN notice equals the gap from 1-SIN to none — breadth is rewarded,")
    print("not runaway. Pair SINs with NAICS and keyword fit to actually climb.")


if __name__ == "__main__":
    main()
