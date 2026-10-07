#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export exact public Stage 1 candidate files; never publish or activate them."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "foundation.schema.json": "docs/decisions/candidates/foundation.schema.json",
    "record-vectors.json": "docs/decisions/candidates/record-vectors.json",
    "decision-json-v1-vectors.json": "docs/decisions/decision-json-v1-vectors.json",
}


def export(destination):
    pins = {}
    contents = {}
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT)]
    for name, relative in FILES.items():
        subprocess.run(git + ["ls-files", "--error-unmatch", relative], check=True, capture_output=True)
        raw = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
        committed = subprocess.check_output(git + ["show", f"HEAD:{relative}"]).replace(b"\r\n", b"\n")
        if raw != committed:
            raise ValueError(f"candidate differs from the recorded source revision: {relative}")
        pins[name] = {"source": relative, "sha256": hashlib.sha256(raw).hexdigest()}
        contents[name] = raw
    revision = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    lock = {"status": "proposed-not-released", "repository": "iokaio/munarium-platform",
            "revision": revision, "files": pins}
    contents["vendor-lock.json"] = (json.dumps(lock, sort_keys=True, indent=2) + "\n").encode()
    destination.mkdir(parents=True, exist_ok=True)
    for name, raw in contents.items():
        path = destination / name
        if path.exists() and path.read_bytes().replace(b"\r\n", b"\n") != raw:
            raise ValueError(f"refusing to overwrite different candidate: {name}")
    for name, raw in contents.items():
        (destination / name).write_bytes(raw)
    print(f"Exported {len(pins)} unchanged candidate files; no contract acceptance or activation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    export(parser.parse_args().destination.resolve())
