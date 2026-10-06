#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Inspect explicitly selected sibling checkouts without fetching or changing them.

This is a workspace preflight, not a build, compatibility or release check. Only
the public repository allowlist is inspected. Unknown remote URLs and Git errors
are never echoed: either may contain local paths or credentials. Git optional
locks, filesystem monitors and configured clean/process filters are disabled for
these read-only observations. Dirty counts can conservatively include files that
normally compare clean only after a filter runs; submodule contents are excluded.
Ambient Git environment overrides are excluded so another worktree, index or
configuration cannot replace the explicitly selected checkout during inspection.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess

REQUIRED = (
    "munarium-platform", "munarium", "munarium-matrix", "munarium-registry",
    "munarium-gate", "munarium-warden", "munarium-council", "munarium-harness",
    "munarium-gateway", "munarium-sentinel", "munarium-assure", "munarium-console",
)
SUPPORTING = ("munarium-demo", "munarium-clients-publish")


def git(repo: Path, *args: str, no_match_ok: bool = False) -> str:
    env = {key: value for key, value in os.environ.items()
           if not key.upper().startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo.as_posix()}", "-c", "core.fsmonitor=false",
         "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=env, timeout=15, check=False,
    )
    if result.returncode and not (no_match_ok and result.returncode == 1):
        raise ValueError("Git inspection failed")
    return result.stdout.strip()


def status_without_filters(repo: Path) -> str:
    # Read matching names only, never config values. A status scan can otherwise
    # execute a clean/process filter, even when optional index locks are disabled.
    names = git(repo, "config", "--null", "--name-only", "--get-regexp",
                r"^filter\..*\.(clean|process|required)$", no_match_ok=True)
    filters = {name.rsplit(".", 1)[0] for name in names.split("\0") if name}
    overrides: list[str] = []
    for driver in sorted(filters):
        for suffix, value in (("clean", ""), ("process", ""), ("required", "false")):
            overrides.extend(("-c", f"{driver}.{suffix}={value}"))
    return git(repo, *overrides, "status", "--porcelain=v1", "--untracked-files=normal",
               "--ignore-submodules=all")


def inspect(root: Path, name: str) -> dict[str, object]:
    if name not in REQUIRED + SUPPORTING:
        raise ValueError("Repository is outside the public allowlist")
    repo = root / name
    row: dict[str, object] = {"repository": name, "required": name in REQUIRED}
    if not repo.is_dir():
        return dict(row, status="missing")
    # Do not follow a checkout link outside the explicitly selected workspace.
    if repo.resolve().parent != root.resolve():
        return dict(row, status="outside-workspace")
    repo = repo.resolve()
    try:
        if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
            return dict(row, status="not-repository-root")
        origin = git(repo, "remote", "get-url", "origin")
        allowed = {
            f"https://github.com/iokaio/{name}", f"https://github.com/iokaio/{name}.git",
            f"git@github.com:iokaio/{name}.git", f"ssh://git@github.com/iokaio/{name}.git",
        }
        if origin not in allowed:
            return dict(row, status="origin-mismatch")
        head = git(repo, "rev-parse", "--verify", "HEAD")
        branch = git(repo, "branch", "--show-current") or "(detached)"
        changed = status_without_filters(repo)
        return dict(row, status="present", revision=head, branch=branch,
                    changed_paths=len(changed.splitlines()))
    except (ValueError, OSError, subprocess.TimeoutExpired):
        return dict(row, status="inspection-failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Parent of public checkouts")
    parser.add_argument("--include-supporting", action="store_true")
    parser.add_argument("--json", action="store_true", help="Machine-readable observations")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error("workspace root must be an existing directory")
    names = REQUIRED + (SUPPORTING if args.include_supporting else ())
    rows = [inspect(args.root.resolve(), name) for name in names]
    if args.json:
        print(json.dumps({"kind": "workspace-observation", "repositories": rows}, indent=2))
    else:
        for row in rows:
            details = ""
            if row["status"] == "present":
                details = (f" {row['revision']} {row['branch']}"
                           f" changed_paths={row['changed_paths']}")
            print(f"{row['repository']}: {row['status']}{details}")
        print("Presence and origin only; no fetch, tests, compatibility or qualification implied.")
    # Optional support checkouts are reported but never become runtime prerequisites.
    return int(any(row["required"] and row["status"] != "present" for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
