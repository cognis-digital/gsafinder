"""Scenario 20 - graceful failure on bad data.

Feeds break. A truncated file, invalid JSON, or a record that isn't an object
should produce a clear error and a nonzero exit — never a stack trace. This demo
writes three broken inputs to a temp dir, runs the real CLI against each, and
shows the human-readable error and exit code 2 for every case.
"""
import io
import json
import os
import tempfile
from contextlib import redirect_stdout, redirect_stderr

from _common import rule

from gsafinder.cli import main as cli_main

DEMOS = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(DEMOS, "01-basic", "profile.json")


def _run(path):
    err = io.StringIO()
    with redirect_stdout(io.StringIO()), redirect_stderr(err):
        rc = cli_main(["survey", path, "-p", PROFILE])
    return rc, err.getvalue().strip()


def main() -> None:
    rule("MALFORMED INPUT HANDLING  -  clear errors, never a stack trace")

    with tempfile.TemporaryDirectory() as tmp:
        invalid = os.path.join(tmp, "invalid.json")
        with open(invalid, "w", encoding="utf-8") as fh:
            fh.write("{ not valid json")

        not_object = os.path.join(tmp, "not_object.json")
        with open(not_object, "w", encoding="utf-8") as fh:
            json.dump(["just", "strings"], fh)

        missing_field = os.path.join(tmp, "missing_field.json")
        with open(missing_field, "w", encoding="utf-8") as fh:
            json.dump({"opportunities": [{"title": "no notice id here"}]}, fh)

        cases = [
            ("invalid JSON", invalid),
            ("record is not an object", not_object),
            ("record missing notice_id", missing_field),
        ]
        for label, path in cases:
            rc, msg = _run(path)
            print(f"\n   {label}")
            print(f"     exit={rc}  {msg}")
            assert rc == 2, f"{label} should exit 2, got {rc}"
            assert msg.startswith("error:"), "error must be human-readable on stderr"

    print("\nEvery broken input yields exit 2 and a plain 'error: ...' line —")
    print("safe to run against a raw feed without babysitting for tracebacks.")


if __name__ == "__main__":
    main()
