"""Scenario 5 - capture analysts tuning relevance.

Naive substring matching is a capture team's worst enemy: search for "AI" and
every "maintain" lights up, drowning the real leads. gsafinder matches keywords
on whole-word boundaries, so "AI" and "ML" hit genuine artificial-intelligence
notices but never the "maintain"/"remediation" noise. This demo runs the
keyword-noise fixture and shows, notice by notice, where the real hits land and
where the false positives are correctly suppressed.
"""
from _common import rule, run_survey


def main() -> None:
    rule("KEYWORD PRECISION  -  'AI' matches AI, not 'maintain'")

    ranked = run_survey("10-keyword-noise")

    print("\nPer-notice keyword verdict (whole-word matching):\n")
    for r in ranked:
        hit_reason = next((x for x in r.reasons if "keyword hits" in x), None)
        verdict = hit_reason if hit_reason else "no keyword hit (noise suppressed)"
        print(f"   {r.opportunity.notice_id:<16} score={r.score:>5.1f}  {verdict}")
        print(f"      title: {r.opportunity.title[:58]}")

    hits = [r for r in ranked if any("keyword hits" in x for x in r.reasons)]
    noise = [r for r in ranked if not any("keyword hits" in x for x in r.reasons)]
    print(f"\nReal keyword leads: {len(hits)}    correctly-suppressed noise: {len(noise)}")
    print("The grounds-maintenance notice has 'maintain'/'remediation' in its text")
    print("but scores no keyword points — the analyst's relevance stays honest.")


if __name__ == "__main__":
    main()
