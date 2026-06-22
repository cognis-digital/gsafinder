# Demo 11 — Deadline-driven triage (urgency bonus and closed penalty)

`Harbor IT Services` (Total Small Business) needs to know what's about to close.
Four near-identical TOTAL_SB cloud/help-desk notices that differ mainly by
**response_due**, so the deadline logic drives the ranking:

- a notice due in a few days → **urgency bonus** (`urgent: Nd to respond`),
- one due in ~two weeks → small bonus,
- one due in ~a month → no bonus,
- one already **closed** → score is penalized and flagged `CLOSED Nd ago`.

> Dates are relative to **today** (the CLI uses the current date). The exact day
> counts shift over time, but the *ordering by urgency* and the closed-flag
> behavior hold.

## Run it — surface what closes within 7 days

```bash
python -m gsafinder survey demos/11-deadline-triage/opportunities.json \
    -p demos/11-deadline-triage/profile.json --format json | \
    jq '.results[] | select(.days_left != null and .days_left >= 0 and .days_left <= 7)'
```

## Expected

- `47QTCA26R0180` (due ~3 days out) carries the urgency bonus and ranks at or
  near the top.
- `HSHQDC26R00120` is flagged `CLOSED` in its `reasons` and drops in the
  ranking — surfaced so you can request a debrief, not chase a dead bid.
- The `jq` filter returns only the genuinely time-critical, still-open notices.

## How to act

Wire this into a daily cron and alert on any result where `days_left <= 7` —
that is the "respond now" queue.
