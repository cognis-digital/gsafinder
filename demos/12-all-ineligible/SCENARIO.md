# Demo 12 — Every notice is a no-bid

The eligibility gate runs before scoring. When a vendor holds a certification
that does not cover any of the day's set-asides, `gsafinder` should return a
clean, empty *eligible* set rather than surface false leads.

`Summit HUBZone Logistics LLC` holds **HUBZONE** only.

## Source data

Three logistics notices, each restricted to a set-aside HUBZONE does not
subsume:
- `SP470026R9001` — **SDVOSB** freight,
- `GS00Q26WOSB0110` — **WOSB** warehousing,
- `47QMCA26R0300` — **8(a)** managed logistics.

## Run it

```bash
python -m gsafinder survey demos/12-all-ineligible/opportunities.json \
    -p demos/12-all-ineligible/profile.json --eligible-only
```

## Expected

- With `--eligible-only`, the result set is **empty**.
- Without it, all three appear with `eligible=no`, `score=0.0`, and a leading
  `INELIGIBLE:` reason.

## How to act

A wholly-empty eligible set is a signal to walk away for the day — the gate
saved the capture team from chasing three notices it legally cannot bid.
