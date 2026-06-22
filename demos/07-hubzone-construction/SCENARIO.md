# Demo 07 — HUBZone construction firm, no GSA Schedule SINs

`Granite Ridge Builders LLC` is a **HUBZone** construction firm. Construction
work is typically procured off-Schedule, so this vendor holds **no SINs** — the
demo proves scoring still works on NAICS + keyword + set-aside alone (the SIN
component simply contributes 0).

Vendor capability:
- NAICS **236220** (Commercial Building Construction), **238210**
  (Electrical), **237310** (Highway/Street)
- SINs: none
- Set-aside: **HUBZONE**
- Keywords: construction, renovation, design-build, electrical, roofing, facility

## Source data

USACE / VA / GSA notices: a HUBZone design-build (exact NAICS + multiple
keywords), a Total Small Business roofing job (eligible by implication), a
full-and-open electrical upgrade (eligible, NAICS match), and a WOSB painting
notice the vendor **cannot** bid.

## Run it

```bash
python -m gsafinder survey demos/07-hubzone-construction/opportunities.json \
    -p demos/07-hubzone-construction/profile.json --eligible-only --format table
```

## Expected

- `W912DR26R0024` (HUBZone design-build) ranks **first** — NAICS 236220 match
  plus renovation/design-build/electrical/roofing/facility keyword hits.
- `47PE0226R0008` (electrical, full & open) is eligible — NAICS 238210 match.
- `36C25026R0301` (Total SB roofing) is eligible by implication.
- `GS00P26WOSB0061` (WOSB painting) is **filtered out** by `--eligible-only`.

## How to act

No SIN column is needed for off-Schedule trades — rank on NAICS fit and
keyword density, then confirm the HUBZone notice against your geographic
HUBZone designation before committing capture resources.
