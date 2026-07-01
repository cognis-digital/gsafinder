# Demo 14 — SIN overlap and its cap

Each GSA Schedule SIN a notice shares with the vendor is worth +12.5, but the
total SIN contribution is **capped at +25** so a multi-SIN BPA can't run away
with the ranking on schedule breadth alone.

`Ironclad Multi-Schedule Integrators` (SDVOSB) holds SINs
**54151S, 54151HACS, 541330ENG, 518210C** (no keywords, to isolate the SIN
signal).

## Source data

Three full-and-open NAICS-`541512` notices:
- `SIN-MANY-0001` — references 3 held SINs (raw 37.5, **capped to 25**),
- `SIN-ONE-0002` — references 1 held SIN (**+12.5**),
- `SIN-NONE-0003` — references an unrelated SIN (**+0**, no SIN reason).

## Run it

```bash
python -m gsafinder survey demos/14-sin-overlap/opportunities.json \
    -p demos/14-sin-overlap/profile.json --format json | \
    jq '.results[] | {notice_id, score, reasons}'
```

## Expected

- `SIN-MANY-0001` scores highest, but its SIN bonus is clamped at 25 — it is
  only 12.5 above `SIN-ONE-0002`, not 25.
- `SIN-NONE-0003` has no `SIN match` reason at all.

## How to act

Breadth helps but is bounded — pair SIN coverage with NAICS and keyword fit to
climb the ranking, rather than relying on schedule count alone.
