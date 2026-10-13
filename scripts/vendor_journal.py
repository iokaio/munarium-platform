#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export the exact committed inert journal candidate into a new namespace."""
import argparse
from pathlib import Path

from generate_journal_candidate import PROFILE
from vendor_stage2 import read_committed, write_export

RELATIVE = Path("docs/decisions/journal-v1")


def export(destination):
    contents = read_committed(source_directory=RELATIVE, profile=PROFILE)
    write_export(contents, destination)
    print("Exported committed journal candidate; no activation or accepted contract.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    export(parser.parse_args().destination.absolute())
