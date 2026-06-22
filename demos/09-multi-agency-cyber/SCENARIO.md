# Demo 09 — Multi-agency cyber pipeline, top-N triage

A busy day for `Sentinel Cyber Partners` (SDVOSB): six cybersecurity notices
spanning CISA, Air Force, VA, Navy, and GSA. This demo shows ranking a larger
batch and trimming to the strongest leads for a capture standup.

Vendor capability:
- NAICS **541512 / 541519 / 518210**
- SINs **54151S**, **54151HACS**
- Set-aside: **SDVOSB**
- Keywords: penetration testing, vulnerability assessment, SOC, threat hunting,
  zero trust, RMF, incident response, SIEM

## Run it — top 3 eligible leads

```bash
python -m gsafinder survey demos/09-multi-agency-cyber/opportunities.json \
    -p demos/09-multi-agency-cyber/profile.json \
    --eligible-only --min-score 50 --top 3 --format table
```

## Expected

- The SDVOSB CDM/SOC notice (`HSHQDC26R00101`) leads — two SIN hits plus dense
  keyword coverage (SOC, SIEM, threat hunting, incident response).
- The full-and-open pentest notice (`FA830726R0009`) and the SDVOSB RMF/zero
  trust notice (`36C10X26R0210`) round out the top 3.
- The 8(a) help desk notice (`N0001926R0077`) is **excluded** —
  `--eligible-only` drops it (SDVOSB does not cover 8(a)), and it would score
  `0` regardless.

## How to act

Run without `--top` to get the full ranked board, then assign the top 3 to
capture leads. Swap `--format json | jq '.results[].notice_id'` to push the
shortlist straight into a tracker.
