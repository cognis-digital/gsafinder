# Demo 10 — Short keywords without false positives

Short capability keywords like **AI** and **ML** are notorious for matching
inside unrelated words ("m**ai**nt**ai**n", "re**m**ediation"). `gsafinder`
matches on whole words/phrases only, so noise does not inflate scores. This demo
proves it.

`Apex AI Labs` (SDVOSB) keywords: **AI, ML, natural language processing,
computer vision, model**.

## Source data

Three SDVOSB-eligible notices:
- a genuine AI/ML model notice (real keyword hits),
- a **grounds-maintenance** notice whose text contains *maintain*, *retain*,
  *remediation*, *plan*, and *airfield* — substrings of AI/ML/plan but **not**
  whole-word matches,
- a computer-vision medical-imaging notice (real hits).

## Run it

```bash
python -m gsafinder survey demos/10-keyword-noise/opportunities.json \
    -p demos/10-keyword-noise/profile.json --format json | \
    jq '.results[] | {notice_id, score, reasons}'
```

## Expected

- `47QTCA26R0160` (AI/ML model + NLP) scores high — multiple legitimate keyword
  hits plus NAICS + SIN.
- `75N98026R00050` (computer vision model) also scores well.
- `W912DY26R0050` (grounds maintenance) is SDVOSB-eligible but its `reasons`
  contain **no keyword hits** — "maintain"/"remediation" do not trigger AI/ML.
  It ranks last on capability fit despite being a valid set-aside.

## How to act

Use this pattern to keep two- and three-letter capability tags (AI, ML, IV&V,
RMF) in your profile without poisoning the ranking with substring noise.
