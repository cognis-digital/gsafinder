"""Command-line interface for GSAFINDER."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from . import TOOL_NAME, TOOL_VERSION
from .core import load_opportunities, load_profile, survey


def _format_table(rows: list[dict]) -> str:
    if not rows:
        return "No matching opportunities."
    headers = ["SCORE", "ELIG", "DAYS", "NOTICE_ID", "SET-ASIDE", "TITLE"]
    lines = []
    table = []
    for r in rows:
        table.append(
            [
                f"{r['score']:.1f}",
                "yes" if r["eligible"] else "no",
                "--" if r["days_left"] is None else str(r["days_left"]),
                r["notice_id"],
                r["set_aside"] or "open",
                r["title"][:48],
            ]
        )
    widths = [len(h) for h in headers]
    for row in table:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    lines.append(fmt.format(*headers))
    lines.append(fmt.format(*["-" * w for w in widths]))
    for row in table:
        lines.append(fmt.format(*row))
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="GSA Schedule opportunity surveyor (SAM.gov / eBuy / FedConnect).",
    )
    parser.add_argument(
        "--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}"
    )
    sub = parser.add_subparsers(dest="command")

    survey_p = sub.add_parser(
        "survey",
        help="score and rank opportunities against a vendor profile",
    )
    survey_p.add_argument("opportunities", help="path to opportunities JSON file")
    survey_p.add_argument(
        "-p", "--profile", required=True, help="path to vendor profile JSON file"
    )
    survey_p.add_argument(
        "--min-score", type=float, default=0.0, help="drop results below this score"
    )
    survey_p.add_argument(
        "--eligible-only",
        action="store_true",
        help="only show opportunities the vendor may bid",
    )
    survey_p.add_argument("--top", type=int, default=0, help="limit to top N results")
    survey_p.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="output format (default: table)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "survey":
        parser.print_help()
        return 1

    try:
        opportunities = load_opportunities(args.opportunities)
        profile = load_profile(args.profile)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2

    results = survey(
        opportunities,
        profile,
        min_score=args.min_score,
        eligible_only=args.eligible_only,
    )
    if args.top > 0:
        results = results[: args.top]

    rows = [r.to_dict() for r in results]

    if args.format == "json":
        print(
            json.dumps(
                {"vendor": profile.name, "count": len(rows), "results": rows},
                indent=2,
            )
        )
    else:
        print(_format_table(rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
