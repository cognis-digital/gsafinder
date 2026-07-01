"""Scenario 11 - CLI CSV straight into a spreadsheet.

A BD analyst lives in a spreadsheet. gsafinder's `--format csv` writes a stable,
pipe-safe column layout that opens cleanly in Excel/Sheets and round-trips
through csv.DictReader. This demo invokes the real CLI, captures the CSV, and
parses it back into records — confirming the header, row count, and that list
fields (sins, reasons) stay in one cell.
"""
import csv
import io
import os
from contextlib import redirect_stdout

from _common import rule

from gsafinder.cli import main as cli_main
from gsafinder.core import CSV_COLUMNS

DEMOS = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    rule("CLI CSV PIPELINE  -  spreadsheet-ready, pipe-safe columns")

    opps = os.path.join(DEMOS, "08-csv-pipeline", "opportunities.json")
    profile = os.path.join(DEMOS, "08-csv-pipeline", "profile.json")

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(["survey", opps, "-p", profile, "--format", "csv"])
    assert rc == 0, f"CLI returned {rc}"

    text = buf.getvalue()
    rows = list(csv.reader(io.StringIO(text)))
    print(f"\nheader columns : {len(rows[0])}")
    print(f"data rows      : {len(rows) - 1}")
    assert rows[0] == CSV_COLUMNS

    records = list(csv.DictReader(io.StringIO(text)))
    print("\nFirst record parsed back via DictReader:")
    first = records[0]
    for k in ("score", "eligible", "days_left", "notice_id", "set_aside"):
        print(f"   {k:<10} = {first[k]}")

    # pipe-joined list fields survive as a single cell
    assert "|" in first["reasons"]
    print("\nreasons cell (single field):", first["reasons"][:70], "...")
    print("\nEvery scored notice is one clean CSV row — drop it straight into the")
    print("pipeline tracker with the 'reasons' column as the ready rationale.")


if __name__ == "__main__":
    main()
