# Demo 01 - Basic opportunity survey

A small SDVOSB cloud/cyber integrator (`Acme Federal LLC`) wants to know which
of this week's federal solicitations are worth a bid. The vendor holds:

- NAICS **518210** (Computing Infrastructure) and **541512** (Systems Design)
- GSA Schedule SIN **54151S** (IT Professional Services)
- Socioeconomic set-asides: **SDVOSB** (which subsumes VOSB / Total Small Business)
- Capability keywords: cloud, cybersecurity, zero trust, migration

`opportunities.json` holds five normalized notices pulled from SAM.gov, eBuy,
and FedConnect, including:

- a perfect-fit SDVOSB cloud set-aside (NAICS + SIN + keywords + urgent),
- an open-competition cyber job the vendor can still bid,
- an **8(a) set-aside** the vendor is **ineligible** for,
- an off-domain janitorial notice (wrong NAICS, no keywords),
- an already-closed notice.

## Run it

```bash
python -m gsafinder survey demos/01-basic/opportunities.json \
    -p demos/01-basic/profile.json --format table
```

Add `--eligible-only` to hide the 8(a) notice, or `--format json` for machine
output, or `--min-score 50 --top 3` to surface only the strong leads.

Expected: the SDVOSB cloud notice ranks first; the 8(a) notice is flagged
`INELIGIBLE` with score 0; the janitorial notice scores low.
