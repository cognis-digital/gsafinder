"""GSAFINDER command-line interface."""
from cognis_core import build_cli
from gsafinder.core import scan, TOOL_NAME, TOOL_VERSION

main = build_cli(
    tool_name=TOOL_NAME,
    tool_version=TOOL_VERSION,
    description="GSA Schedule opportunity surveyor — SAM.gov + eBuy + FedConnect",
    scan_fn=scan,
)

if __name__ == "__main__":
    import sys
    sys.exit(main())
