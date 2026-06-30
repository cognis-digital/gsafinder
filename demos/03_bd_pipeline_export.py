"""Scenario 3 - business-development teams.

A BD team does not live in a terminal — it lives in a spreadsheet and a CRM.
gsafinder's job here is to turn a multi-agency opportunity pull into a ranked,
filtered CSV the team can drop straight into a pipeline tracker. This demo runs
the real ranker across a larger 5-agency cyber batch, filters to eligible
high-score leads, and renders the real ``to_csv`` export with every scoring
reason captured per row.
"""
from _common import print_ranked, rule, run_survey, to_csv


def main() -> None:
    rule("BD PIPELINE EXPORT  -  ranked, filtered, spreadsheet-ready CSV")

    # eligible-only + a score floor: the BD team wants real leads, not noise.
    ranked = run_survey("09-multi-agency-cyber", eligible_only=True, min_score=40)

    agencies = sorted({r.opportunity.agency for r in ranked})
    print(f"\n{len(ranked)} eligible leads (score >= 40) across {len(agencies)} agencies:")
    for a in agencies:
        print(f"   - {a}")

    print()
    print_ranked(ranked)

    csv_text = to_csv(ranked)
    lines = csv_text.splitlines()
    print(f"\nto_csv() -> {len(lines) - 1} data row(s), {len(lines[0].split(','))} columns")
    print("Header + first two rows of the pipeline export:\n")
    for line in lines[:3]:
        print("   " + (line[:110] + ("..." if len(line) > 110 else "")))

    print("\nThe BD team imports this CSV into the pipeline tracker — score, days")
    print("left, agency, and the 'reasons' column give every row a ready rationale.")


if __name__ == "__main__":
    main()
