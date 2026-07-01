"""Scenario 14 - walking the full set-aside ladder.

The socioeconomic ladder is the heart of federal eligibility: an SDVOSB
subsumes VOSB and Total SB; an EDWOSB subsumes WOSB; an 8(a) does not reach
HUBZone; and everyone may bid full-and-open. This demo asks the real
VendorProfile what each certification actually unlocks and prints the expanded
eligibility set, so the ladder is visible rather than implied.
"""
from _common import rule

from gsafinder.core import VendorProfile

CASES = [
    ("SDVOSB", ["SDVOSB"]),
    ("VOSB", ["VOSB"]),
    ("EDWOSB", ["EDWOSB"]),
    ("WOSB", ["WOSB"]),
    ("8(a)", ["8A"]),
    ("HUBZone", ["HUBZONE"]),
    ("Total SB", ["TOTAL_SB"]),
    ("no certs", []),
]


def main() -> None:
    rule("SET-ASIDE LADDER WALK  -  what each certification unlocks")

    print("\nEach profile's expanded eligibility (open competition omitted):\n")
    for label, certs in CASES:
        prof = VendorProfile(set_asides=certs)
        elig = prof.eligible_set_asides()
        # drop the always-present open-competition values for a clean view
        restricted = sorted(elig - {"", "NONE", "FULL_AND_OPEN", "FAO", "UNRESTRICTED"})
        print(f"   {label:<9} -> {restricted or ['(open competition only)']}")

    # spot-check the classic ladder facts the tool encodes
    edwosb = VendorProfile(set_asides=["EDWOSB"]).eligible_set_asides()
    eighta = VendorProfile(set_asides=["8A"]).eligible_set_asides()
    assert "WOSB" in edwosb, "EDWOSB should subsume WOSB"
    assert "HUBZONE" not in eighta, "8(a) should NOT reach HUBZONE"
    assert "SDVOSB" not in edwosb, "EDWOSB should NOT reach SDVOSB"

    print("\nEDWOSB reaches WOSB but not SDVOSB; 8(a) never reaches HUBZone.")
    print("The ladder is data, not guesswork — every gate decision traces to it.")


if __name__ == "__main__":
    main()
