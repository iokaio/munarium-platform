#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export the committed ClearView review candidate under its own namespace."""
import argparse
from pathlib import Path

from generate_clearview_candidate import PROFILE, RELATIVE
from vendor_stage2 import read_committed, write_export


def export(destination):
    write_export(read_committed(source_directory=RELATIVE, profile=PROFILE), destination)
    print("Exported the committed ClearView review candidate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    export(parser.parse_args().destination.absolute())
