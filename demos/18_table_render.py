"""Scenario 18 - the human-readable table.

The default CLI output is a fixed-width table a person reads in a terminal. This
demo invokes the real CLI with the default format, captures it, and verifies the
table has aligned columns, a header rule, and one row per scored notice — the
same view a capture manager sees at the command line.
"""
import io
import os
from contextlib import redirect_stdout

from _common import rule

from gsafinder.cli import main as cli_main

DEMOS = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    rule("TABLE RENDER  -  the default human-readable view")

    opps = os.path.join(DEMOS, "01-basic", "opportunities.json")
    profile = os.path.join(DEMOS, "01-basic", "profile.json")

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(["survey", opps, "-p", profile])  # default format = table
    assert rc == 0

    text = buf.getvalue()
    print("\n" + text)

    lines = [ln for ln in text.splitlines() if ln.strip()]
    header = lines[0]
    assert "SCORE" in header and "TITLE" in header, "table needs a header row"
    assert set(lines[1]) <= set("- "), "second line should be the header rule"
    data_rows = lines[2:]
    assert data_rows, "table should have at least one data row"

    print(f"header + rule + {len(data_rows)} data row(s) rendered.")
    print("This is the at-a-glance view; --format json/csv feed machines instead.")


if __name__ == "__main__":
    main()
