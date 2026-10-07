#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export a committed Stage 2 candidate into a NEW consumer namespace."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = Path("docs/decisions/stage2-v1")
FILES = {"README.md", "schema.json", "profile.json", "vectors.json"}


def verify_lock(contents):
    lock = json.loads(contents["bundle-lock.json"])
    if (set(lock) != {"status", "profile", "files", "bundle_sha256"} or
            lock["status"] != "candidate-not-accepted-not-released" or lock["profile"] != "stage2-single-cell-v1" or
            set(lock["files"]) != FILES or set(contents) != FILES | {"bundle-lock.json"}):
        raise ValueError("unexpected candidate lock or file set")
    hashes = {name: hashlib.sha256(contents[name]).hexdigest() for name in sorted(FILES)}
    aggregate = "".join(name + "\0" + sha + "\n" for name, sha in hashes.items()).encode()
    if hashes != lock["files"] or hashlib.sha256(aggregate).hexdigest() != lock["bundle_sha256"]:
        raise ValueError("candidate lock mismatch")
    return lock


def read_committed(root=ROOT):
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]
    revision = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    contents = {}
    for name in sorted(FILES | {"bundle-lock.json"}):
        relative = (RELATIVE / name).as_posix()
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to((root / RELATIVE).resolve()):
            raise ValueError("candidate symlink is not exportable")
        committed = subprocess.check_output(git + ["show", f"{revision}:{relative}"], stderr=subprocess.PIPE).replace(b"\r\n", b"\n")
        if path.read_bytes().replace(b"\r\n", b"\n") != committed:
            raise ValueError("candidate differs from committed source: " + relative)
        contents[name] = committed
    lock = verify_lock(contents)
    contents["vendor-lock.json"] = (json.dumps(dict(status="candidate-not-accepted-not-released",
        repository="iokaio/munarium-platform", revision=revision, source_directory=RELATIVE.as_posix(),
        bundle_sha256=lock["bundle_sha256"], files=lock["files"]), sort_keys=True, indent=2) + "\n").encode()
    return contents


def write_export(contents, destination):
    if set(contents) != FILES | {"bundle-lock.json", "vendor-lock.json"}:
        raise ValueError("unexpected export file set")
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise ValueError("destination must be a directory, not a symlink")
    # Check every collision before creating or changing any destination file.
    for name, raw in contents.items():
        path = destination / name
        if path.is_symlink() or (path.exists() and (not path.is_file() or path.read_bytes().replace(b"\r\n", b"\n") != raw)):
            raise ValueError("refusing different destination artifact: " + name)
    destination.mkdir(parents=True, exist_ok=True)
    for name in sorted(contents, key=lambda name: (name == "vendor-lock.json", name)):
        (destination / name).write_bytes(contents[name])


def export(destination):
    contents = read_committed()
    write_export(contents, destination)
    print("Exported committed Stage 2 candidate with immutable source/bundle pins; no activation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    export(parser.parse_args().destination.absolute())
