# Demo 06 — 8(a) analytics firm, HUBZone gap

`Cascade Analytics Group` is an **8(a)** data-analytics shop. The 8(a) program
qualifies the vendor for 8(a) and Total Small Business reservations and any
full-and-open notice, but **not** for HUBZone or WOSB set-asides.

Vendor capability:
- NAICS **541511 / 541512 / 518210 / 541690**
- SINs **54151S**, **518210C**
- Set-aside: **8A**
- Keywords: data analytics, machine learning, data engineering, ETL,
  dashboard, geospatial

## Source data

GSA / DHS / Army notices: an 8(a) analytics notice (exact fit), a full-and-open
geospatial ML notice (eligible), a **HUBZone** infrastructure notice
(ineligible), and a Total Small Business digitization notice (eligible but off
the vendor's keyword domain).

## Run it

```bash
python -m gsafinder survey demos/06-8a-graduate/opportunities.json \
    -p demos/06-8a-graduate/profile.json --format table
```

## Expected

- `47QFCA26R0050` (8(a), NAICS + SIN + keywords) ranks **first**.
- `HSHQDC26R00031` (full & open ML) scores well and is eligible.
- `GS35F26HUB0021` (HUBZone) is `INELIGIBLE` with score `0`.
- `W91QVN26R0010` (Total SB digitization) is eligible but low — no NAICS/SIN
  match and no keyword hits.

## How to act

The HUBZone notice surfacing as `INELIGIBLE` is the flag to pursue a HUBZone
teaming partner if the contract value justifies it.
