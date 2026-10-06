# SPDX-License-Identifier: Apache-2.0
"""Workspace preflight negative controls; temporary repositories never use the network."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import workspace_inventory as inventory


@unittest.skipUnless(shutil.which("git"), "Git is required for repository identity tests")
class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def run_git(self, repo: Path, *args: str) -> None:
        subprocess.run(["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo),
                        *args], check=True, capture_output=True)

    def checkout(self) -> Path:
        repo = self.root / "munarium-matrix"
        repo.mkdir()
        self.run_git(repo, "init", "--initial-branch=main")
        self.run_git(repo, "remote", "add", "origin",
                     "https://github.com/iokaio/munarium-matrix.git")
        # Fictional test identity affects only this process, never user Git configuration.
        self.run_git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                     "commit", "--allow-empty", "-m", "fixture")
        return repo

    def test_missing_checkout_is_reported(self) -> None:
        self.assertEqual(inventory.inspect(self.root, "munarium-matrix")["status"], "missing")

    def test_matching_origin_reports_revision_and_dirty_count_without_paths(self) -> None:
        repo = self.checkout()
        (repo / "local-note.txt").write_text("fictional input", encoding="utf-8")
        def git_files() -> dict[str, bytes]:
            return {str(path.relative_to(repo)): path.read_bytes()
                    for path in (repo / ".git").rglob("*") if path.is_file()}
        before = git_files()
        row = inventory.inspect(self.root, "munarium-matrix")
        self.assertEqual(row["status"], "present")
        self.assertEqual(row["branch"], "main")
        self.assertEqual(row["changed_paths"], 1)
        self.assertEqual(len(row["revision"]), 40)
        self.assertNotIn("local-note", json.dumps(row))
        self.assertEqual(before, git_files())

    def test_wrong_remote_is_rejected_without_echoing_it(self) -> None:
        repo = self.checkout()
        self.run_git(repo, "remote", "set-url", "origin", "https://example.invalid/wrong.git")
        row = inventory.inspect(self.root, "munarium-matrix")
        self.assertEqual(row["status"], "origin-mismatch")
        self.assertNotIn("example.invalid", json.dumps(row))

    def test_ambient_git_directory_cannot_substitute_another_checkout(self) -> None:
        repo = self.checkout()
        self.run_git(repo, "remote", "set-url", "origin", "https://example.invalid/wrong.git")
        alternate = self.root / "alternate"
        alternate.mkdir()
        self.run_git(alternate, "init", "--initial-branch=main")
        self.run_git(alternate, "remote", "add", "origin",
                     "https://github.com/iokaio/munarium-matrix.git")
        self.run_git(alternate, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                     "commit", "--allow-empty", "-m", "fixture")
        with patch.dict(os.environ, {"GIT_DIR": str(alternate / ".git"),
                                     "GIT_WORK_TREE": str(repo)}):
            row = inventory.inspect(self.root, "munarium-matrix")
        self.assertEqual(row["status"], "origin-mismatch")
        self.assertNotIn("example.invalid", json.dumps(row))

    def test_parent_git_repository_is_not_a_matching_checkout(self) -> None:
        self.run_git(self.root, "init")
        (self.root / "munarium-matrix").mkdir()
        self.assertEqual(inventory.inspect(self.root, "munarium-matrix")["status"],
                         "not-repository-root")

    def test_status_never_executes_configured_clean_or_process_filters(self) -> None:
        repo = self.checkout()
        driver = "inventory.fixture;literal"
        (repo / ".gitattributes").write_text(f"data.txt filter={driver}\n", encoding="utf-8")
        (repo / "data.txt").write_text("before\n", encoding="utf-8")
        self.run_git(repo, "add", ".gitattributes", "data.txt")
        self.run_git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                     "commit", "-m", "tracked filter fixture")
        helper = self.root / "fixture-filter.py"
        helper.write_text(
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[1]).write_text('called')\n"
            "if sys.argv[2] == 'process': sys.exit(1)\n"
            "sys.stdout.write(sys.stdin.read())\n", encoding="utf-8")
        (repo / "data.txt").write_text("after!\n", encoding="utf-8")
        self.run_git(repo, "config", f"filter.{driver}.required", "true")
        for mode in ("clean", "process"):
            with self.subTest(mode=mode):
                marker = self.root / f"{mode}-invoked"
                command = shlex.join([Path(sys.executable).as_posix(), helper.as_posix(),
                                      marker.as_posix(), mode])
                self.run_git(repo, "config", f"filter.{driver}.{mode}", command)
                before = (repo / ".git" / "config").read_bytes()
                row = inventory.inspect(self.root, "munarium-matrix")
                self.assertFalse(marker.exists(), f"{mode} filter executed")
                self.assertEqual(row["status"], "present")
                self.assertEqual(row["changed_paths"], 1)
                self.assertEqual(before, (repo / ".git" / "config").read_bytes())

    def test_private_or_arbitrary_name_is_never_inspected(self) -> None:
        with self.assertRaises(ValueError):
            inventory.inspect(self.root, "unlisted-project")

    def test_optional_missing_does_not_fail_but_required_missing_does(self) -> None:
        def observation(root: Path, name: str) -> dict[str, object]:
            return {"repository": name, "required": name in inventory.REQUIRED,
                    "status": "present" if name in inventory.REQUIRED else "missing"}
        with patch.object(inventory, "inspect", side_effect=observation), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(inventory.main(["--root", str(self.root), "--include-supporting", "--json"]), 0)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(inventory.main(["--root", str(self.root), "--json"]), 1)


if __name__ == "__main__":
    unittest.main()
