# Demo 13 — Deadline breaks a scoring tie

When two opportunities score identically, the sooner deadline should rank first
— a proposal team would rather chase the one closing next. `survey()` sorts by
score descending, then by `days_left` ascending.

`Vertex Cloud Federal` (SDVOSB) keywords: **cloud, hosting**.

## Source data

Two full-and-open cloud-hosting notices with identical fit (same NAICS `518210`,
same single keyword hit, no SINs, both far enough out to earn no urgency bonus)
but different response dates:
- `TIE-SOON-0001` due 2026-07-20,
- `TIE-LATE-0002` due 2026-08-15.

## Run it

```bash
python -m gsafinder survey demos/13-tie-break/opportunities.json \
    -p demos/13-tie-break/profile.json
```

## Expected

- Both notices carry the **same score**.
- `TIE-SOON-0001` ranks **above** `TIE-LATE-0002` because its deadline is nearer.

## How to act

Trust the ordering for same-fit leads: the tool already prioritizes the tighter
clock so you don't have to re-sort by hand.
