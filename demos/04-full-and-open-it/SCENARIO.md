# Demo 04 — Open-market IT vendor with no socioeconomic certs

`Northstar Systems Inc` is a mid-size IT integrator with **no** socioeconomic
set-aside certifications (`set_asides: []`). It can only bid full-and-open
notices and is gated out of anything reserved for small/disadvantaged firms.

Vendor capability:
- NAICS **541512** (Computer Systems Design), **541519**, **518210**
- GSA SINs **54151S** (IT Professional Services) and **54151HACS** (HACS)
- Keywords: software development, agile, DevSecOps, cloud, data migration

## Source data

`opportunities.json` holds four normalized notices pulled from SAM.gov / eBuy:
two full-and-open IT requirements that fit, plus a Total Small Business
help-desk notice and a WOSB graphics notice that this vendor **cannot** bid.

## Run it

```bash
python -m gsafinder survey demos/04-full-and-open-it/opportunities.json \
    -p demos/04-full-and-open-it/profile.json --format table
```

## Expected

- `47QTCA26R0011` (agile/DevSecOps, full & open) ranks **first** — NAICS + SIN +
  multiple keyword hits.
- `75N98026R00024` (health data migration, full & open) ranks second.
- `W52P1J26R0099` (Total SB) and `GS00Q26WOSB0007` (WOSB) score **0** and are
  flagged `INELIGIBLE` — the vendor holds no qualifying certification.

## How to act

Add `--eligible-only` for the bid list this vendor can actually submit, then
`--min-score 40` to drop weak fits. This is the right run for a prime that wins
on capability, not on socioeconomic status.
