"""Scenario 9 - ingesting a messy, multi-format feed.

Real opportunity feeds mix date formats and leave some deadlines blank or free
text. gsafinder parses ISO, US, and slash-ISO dates and degrades to a null
`days_left` for anything it can't read — without ever crashing on bad input.
This demo runs a fixture with one notice per date shape and shows each resolving
(or safely not resolving) to a deadline.
"""
from _common import rule, run_survey


def main() -> None:
    rule("MESSY DATE FEEDS  -  parse what you can, never crash on the rest")

    ranked = {r.opportunity.notice_id: r for r in run_survey("17-date-formats")}

    print("\nParsed deadline per notice (whatever the source format):\n")
    for nid in ("DATE-ISO-0001", "DATE-US-0002", "DATE-SLASH-0003",
                "DATE-BAD-0004", "DATE-MISSING-0005"):
        r = ranked[nid]
        raw = r.opportunity.response_due or "(empty)"
        days = "-- (unparseable)" if r.days_left is None else f"{r.days_left}d left"
        print(f"   {nid:<18} raw={raw:<22} -> {days}")

    parsed = [r for r in ranked.values() if r.days_left is not None]
    undated = [r for r in ranked.values() if r.days_left is None]
    assert len(parsed) == 3 and len(undated) == 2, "3 formats parse, 2 degrade"

    print(f"\n{len(parsed)} well-formed dates resolved; {len(undated)} undated notices")
    print("degraded cleanly to no deadline — no urgency bonus, no penalty, no error.")
    print("A raw multi-source pull can be scored without pre-cleaning the dates.")


if __name__ == "__main__":
    main()
