"""Scenario 1 - GovCon capture managers.

A capture manager opens the morning's SAM.gov / eBuy pull and has to answer one
question fast: *which of these are worth a capture decision today?* gsafinder
runs the eligibility gate first, then ranks the eligible notices by fit (NAICS,
SIN, keyword) and deadline urgency. This demo plays that triage against the real
ranker, then shows the per-notice "why" the tool returns for each lead.
"""
from _common import print_ranked, rule, run_survey


def main() -> None:
    rule("CAPTURE MANAGER TRIAGE  -  what deserves a capture decision today?")

    ranked = run_survey("01-basic")

    print("\nThis morning's pull scored and ranked (eligibility gate applied first):\n")
    print_ranked(ranked)

    top = ranked[0]
    print(f"\nTop lead: {top.opportunity.notice_id}  '{top.opportunity.title}'")
    print(f"   agency={top.opportunity.agency}  source={top.opportunity.source}"
          f"  score={top.score:.1f}")
    print("   why it ranks here:")
    for reason in top.reasons:
        print(f"     - {reason}")

    ineligible = [r for r in ranked if not r.eligible]
    print(f"\nThe gate flagged {len(ineligible)} notice(s) as no-bid (score 0):")
    for r in ineligible:
        print(f"   - {r.opportunity.notice_id}  {r.opportunity.set_aside:<8}"
              f"  {r.reasons[0]}")

    print("\nThe capture manager chases the top of the list and skips the no-bids,")
    print("with the scoring rationale already written for the pipeline review.")


if __name__ == "__main__":
    main()
