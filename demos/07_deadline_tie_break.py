"""Scenario 7 - which of two equal leads first?

Two notices can be an identical fit — same NAICS, same keywords, same schedule
posture — and still not be equally urgent. gsafinder ranks by score first, then
breaks ties by the nearer deadline, so a proposal team always sees the one
closing soonest at the top of a same-score cluster. This demo runs the tie-break
fixture and proves the ordering.
"""
from _common import print_ranked, rule, run_survey


def main() -> None:
    rule("DEADLINE TIE-BREAK  -  equal fit, nearer deadline wins")

    ranked = run_survey("13-tie-break")
    print_ranked(ranked)

    top, second = ranked[0], ranked[1]
    print(f"\nBoth notices score {top.score:.1f} — an identical capability fit.")
    print(f"   1st: {top.opportunity.notice_id}  due in {top.days_left}d")
    print(f"   2nd: {second.opportunity.notice_id}  due in {second.days_left}d")

    assert top.score == second.score, "fixture should produce a scoring tie"
    assert top.days_left <= second.days_left, "nearer deadline should rank first"

    print("\nThe scores tie, so the tighter clock decides: the sooner-closing")
    print("notice is placed first automatically — no manual re-sort required.")


if __name__ == "__main__":
    main()
