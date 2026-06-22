# Demo 05 — EDWOSB staffing firm and the set-aside ladder

`Beacon Workforce Solutions LLC` is an **EDWOSB** (economically disadvantaged
women-owned small business) staffing firm. This demo exercises the eligibility
ladder: EDWOSB subsumes WOSB and Total Small Business, but it does **not** make
the vendor eligible for SDVOSB notices.

Vendor capability:
- NAICS **561320** (Temporary Help), **561311**, **541612**
- SINs **541612**, **561320**
- Set-aside: **EDWOSB**
- Keywords: staffing, temporary, human capital, recruiting, administrative support

## Source data

Four VA / GSA / DLA notices: an EDWOSB notice (exact match), a WOSB notice
(eligible by implication), an **SDVOSB** notice (ineligible), and a Total Small
Business notice (eligible by implication).

## Run it

```bash
python -m gsafinder survey demos/05-wosb-staffing/opportunities.json \
    -p demos/05-wosb-staffing/profile.json --eligible-only --format table
```

## Expected

- `36C24426R0142` (EDWOSB, exact NAICS + SIN + keywords) ranks **first**.
- `GS02Q26WOSB0044` (WOSB) is **eligible** by implication and scores well.
- `47QRAA26R0203` (Total SB) is eligible but lower (no NAICS/SIN/keyword match).
- `SP470026R8801` (SDVOSB) is **filtered out** by `--eligible-only` — an EDWOSB
  cert does not qualify for an SDVOSB reservation.

## How to act

Drop `--eligible-only` to confirm the SDVOSB notice is scored `0` /
`INELIGIBLE` rather than silently missing — useful when deciding whether to
pursue a teaming arrangement with an SDVOSB prime.
