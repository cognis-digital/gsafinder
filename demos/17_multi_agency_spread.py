"""Scenario 17 - one profile across many agencies.

A cyber SDVOSB sells to everyone — DHS, Air Force, VA, GSA, Navy. gsafinder
scores a single profile across a multi-agency pull and lets the team see its
addressable footprint: which agencies carry eligible leads and how the fit
stacks up across the government. This demo runs the 6-notice, 5-agency batch and
summarizes the spread.
"""
from _common import print_ranked, rule, run_survey


def main() -> None:
    rule("MULTI-AGENCY SPREAD  -  one profile, the whole government")

    ranked = run_survey("09-multi-agency-cyber")
    print_ranked(ranked)

    by_agency: dict[str, list] = {}
    for r in ranked:
        by_agency.setdefault(r.opportunity.agency, []).append(r)

    print("\nAddressable footprint by agency:")
    for agency in sorted(by_agency):
        rows = by_agency[agency]
        elig = sum(1 for r in rows if r.eligible)
        best = max(r.score for r in rows)
        print(f"   {agency:<28} {len(rows)} notice(s), {elig} eligible, best score {best:.1f}")

    eligible = [r for r in ranked if r.eligible]
    print(f"\n{len(eligible)} of {len(ranked)} notices are eligible across "
          f"{len(by_agency)} agencies.")
    assert len(by_agency) >= 4, "fixture spans multiple agencies"
    print("The SDVOSB sees exactly where its certification and capability open")
    print("doors government-wide — a portfolio view, not a single-notice look.")


if __name__ == "__main__":
    main()
