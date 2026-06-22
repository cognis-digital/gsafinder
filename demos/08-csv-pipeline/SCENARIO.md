# Demo 08 — CSV export for a capture-team spreadsheet

This demo showcases the `--format csv` exporter. A capture manager at
`Meridian Defense Technologies` (SDVOSB) wants the ranked pipeline in a
spreadsheet for bid/no-bid review, not a terminal table.

Vendor capability:
- NAICS **541512 / 541330 / 518210 / 541715**
- SINs **54151S**, **54151HACS**, **541330ENG**
- Set-aside: **SDVOSB**
- Keywords: cybersecurity, zero trust, systems engineering, cloud, RMF,
  incident response

## Run it — write a CSV the capture team can open in Excel/Sheets

```bash
python -m gsafinder survey demos/08-csv-pipeline/opportunities.json \
    -p demos/08-csv-pipeline/profile.json \
    --eligible-only --min-score 40 --format csv > pipeline.csv
```

CSV columns: `score, eligible, days_left, notice_id, agency, source, naics,
set_aside, sins, response_due, title, reasons`. List fields (`sins`,
`reasons`) are pipe-joined so each value stays in one cell.

## Expected

- `FA877326R0014` (SDVOSB zero-trust/RMF) is the top row — two SIN hits, NAICS
  match, multiple keyword hits.
- `N0017826R0042` (full & open systems engineering) and `HSHQDC26R00088`
  (Total SB SOC) follow.
- The `W56HZV26R0205` 8(a) cabling notice is excluded by `--eligible-only`
  (SDVOSB does not qualify for an 8(a) reservation).

## How to act

Import `pipeline.csv`, sort by `score`, and use the `reasons` column as the
first-pass bid/no-bid justification. Pipe to `column -s, -t < pipeline.csv` for
a quick aligned preview in the terminal.
