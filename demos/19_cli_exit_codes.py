"""Scenario 19 - exit codes for automation.

When gsafinder runs inside a cron job or a pipeline, the exit code is the
contract: 0 on a clean survey, 1 when no subcommand is given, 2 on a load/parse
error. This demo exercises each path through the real CLI and confirms the code,
so an operator can wire alerting to the right signal.
"""
import io
import os
from contextlib import redirect_stdout, redirect_stderr

from _common import rule

from gsafinder.cli import main as cli_main

DEMOS = os.path.dirname(os.path.abspath(__file__))


def _rc(args):
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return cli_main(args)


def main() -> None:
    rule("CLI EXIT CODES  -  the automation contract")

    opps = os.path.join(DEMOS, "01-basic", "opportunities.json")
    profile = os.path.join(DEMOS, "01-basic", "profile.json")

    ok = _rc(["survey", opps, "-p", profile, "--format", "json"])
    no_cmd = _rc([])
    bad_path = _rc(["survey", os.path.join(DEMOS, "does-not-exist.json"), "-p", profile])

    print(f"\n   clean survey        -> exit {ok}")
    print(f"   no subcommand       -> exit {no_cmd}")
    print(f"   missing input file  -> exit {bad_path}")

    assert ok == 0, "a clean survey must exit 0"
    assert no_cmd == 1, "no subcommand must exit 1"
    assert bad_path == 2, "a load error must exit 2"

    print("\n0 = success, 1 = usage, 2 = data error. Wire your alerting to 2 and")
    print("your 'nothing to do' path to 1 — the contract is stable and testable.")


if __name__ == "__main__":
    main()
