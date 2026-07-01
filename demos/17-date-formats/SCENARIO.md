# Demo 17 — Mixed and missing deadline formats

Feeds arrive with dates in several shapes, and some notices carry no usable
deadline at all. `gsafinder` parses ISO (`YYYY-MM-DD`), US (`MM/DD/YYYY`), and
slash-ISO (`YYYY/MM/DD`) forms, and degrades gracefully to `days_left = None`
for anything it can't parse — it never crashes on a bad date.

`Datewise IT Partners` (Total SB) keyword: **support**.

## Source data

Five Total-SB support notices, one per date shape:
- `DATE-ISO-0001` — `2026-06-27`,
- `DATE-US-0002` — `07/05/2026`,
- `DATE-SLASH-0003` — `2026/07/18`,
- `DATE-BAD-0004` — `TBD - see amendment` (unparseable),
- `DATE-MISSING-0005` — empty string.

## Run it

```bash
python -m gsafinder survey demos/17-date-formats/opportunities.json \
    -p demos/17-date-formats/profile.json
```

## Expected

- The three well-formed dates yield concrete `days_left` values.
- The unparseable and missing dates yield `days_left` of `--` (None) with no
  urgency bonus or closed penalty — and no error.

## How to act

You can ingest a raw multi-source pull without pre-cleaning dates; undated
notices simply don't earn (or lose) deadline points.
