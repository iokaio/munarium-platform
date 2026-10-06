#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check local documentation paths, Markdown fragments and docs/ indexes.

Checks over root *.md files, .github/**/*.md and docs/**/*.md:

  * inline local links stay inside this repository and name an existing file or
    directory; same-file and cross-file Markdown fragments name a heading or
    explicit HTML <a id/name>;
  * every .md under docs/ is linked from the README.md of its own directory
    or of an ancestor directory, so the index tables stay complete.

    py scripts/docs_linkcheck.py

Exit 1 on any finding, naming the file and line. Stdlib only, no network.
Carried from iokaio/munarium's scripts/docs_linkcheck.py without that
repository's component-specific claim checks.

Supported subset: single-line inline links/images (optional quoted title), ATX
headings, single-line Setext headings, ordinary inline heading formatting and
quoted HTML <a id/name> anchors. Heading slugs lowercase Unicode letters, keep
letters/numbers/combining marks, hyphens and underscores, replace spaces with
hyphens, and disambiguate duplicates in document order. Paths and fragments are
URL-decoded separately. Fences, HTML comments and inline code links are ignored.
Resolved source and target paths must stay inside the repository; symlink escapes
are findings and their contents are never opened for anchor validation.
Rules follow https://docs.github.com/en/get-started/writing-on-github/
getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

This is not a full Markdown parser or a GitHub rendering oracle. Reference links,
nested link labels/destinations, multiline inline markup, nested container blocks
and raw-HTML headings are outside its subset. It does not check remote URLs or
fragments in PDFs, SVGs, directories or other non-Markdown targets. Heading
rendering outside the subset still needs manual review; a pass proves neither
external availability nor document correctness.
"""
from __future__ import annotations

import html
import pathlib
import re
import sys
import unicodedata
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]

LINK = re.compile(r"!?\[([^\]]*)\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[\"'][^\"']*[\"'])?\)")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?)|[ \t]*)$")
SETEXT = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
CODE_SPAN = re.compile(r"(`+)(?!`)(.*?)\1(?!`)")
ANCHOR = re.compile(r"<a\b[^>]*?\b(?:id|name)\s*=\s*([\"'])(.*?)\1[^>]*>", re.I)


def markdown_files(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    files = sorted(p for p in root.glob("*.md") if p.is_file())
    for base in (root / ".github", root / "docs"):
        if base.is_dir():
            files += sorted(p for p in base.rglob("*.md") if p.is_file())
    return files


def visible_lines(text: str) -> list[tuple[int, str]]:
    """Preserve line numbers while excluding comments and fenced examples."""
    out: list[tuple[int, str]] = []
    fence = None
    comment = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if comment:
            _, end, line = line.partition("-->")
            if not end:
                continue
            comment = False
        while "<!--" in line and fence is None:
            before, _, rest = line.partition("<!--")
            _, end, after = rest.partition("-->")
            line = before + after
            if not end:
                comment = True
                break
        marker = FENCE.match(line)
        if fence is not None:
            if (marker and marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence) and not marker[2].strip()):
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        out.append((lineno, line))
    return out


def links_in(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for lineno, line in visible_lines(text):
        for match in LINK.finditer(CODE_SPAN.sub("", line)):
            target = match[2] or match[3]
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
                continue
            if target:
                out.append((lineno, target))
    return out


def heading_slug(heading: str) -> str:
    """Generate the base anchor for the documented heading syntax subset."""
    heading = re.sub(r"[ \t]+#+[ \t]*$", "", heading)

    def plain_markup(value: str) -> str:
        value = LINK.sub(lambda match: match[1], value)
        value = re.sub(r"<[^>]*>", "", value)
        # Preserve underscores inside identifiers; remove emphasis delimiters.
        value = re.sub(r"(?<!\w)(_+)(\S(?:.*?\S)?)\1(?!\w)", r"\2", value)
        return html.unescape(re.sub(r"[*~]", "", value))

    # Code spans display their contents literally, including underscores/entities.
    parts: list[str] = []
    start = 0
    for match in CODE_SPAN.finditer(heading):
        parts.extend((plain_markup(heading[start:match.start()]), match[2]))
        start = match.end()
    parts.append(plain_markup(heading[start:]))
    heading = "".join(parts)
    return "".join(
        "-" if char == " " else char
        for char in heading.strip().lower()
        if char in " -_" or unicodedata.category(char)[0] in "LNM"
    )


def anchors_in(text: str) -> set[str]:
    anchors: set[str] = set()
    generated: set[str] = set()
    previous = ""
    previous_number = 0
    for lineno, line in visible_lines(text):
        anchors.update(html.unescape(match[2]) for match in ANCHOR.finditer(
            CODE_SPAN.sub("", line)))
        heading = HEADING.match(line)
        title = None
        if heading:
            title = heading[1] or ""
        elif (SETEXT.match(line) and previous.strip()
              and previous_number == lineno - 1
              and not re.match(r"^(?: {4}|\t| {0,3}[>#*+\-])", previous)):
            title = previous.strip()
        if title is not None:
            base = heading_slug(title)
            slug = base
            suffix = 0
            while slug in generated:
                suffix += 1
                slug = f"{base}-{suffix}"
            generated.add(slug)
            anchors.add(slug)
            previous = ""
        else:
            previous = line
        previous_number = lineno
    return anchors


def check(root: pathlib.Path = ROOT) -> tuple[list[pathlib.Path], list[str]]:
    root = root.resolve()
    docs = root / "docs"
    findings: list[str] = []
    files = markdown_files(root)
    linked_from_index: set[pathlib.Path] = set()
    anchor_cache: dict[pathlib.Path, set[str]] = {}

    for file in files:
        if not file.resolve().is_relative_to(root):
            findings.append(f"{file.relative_to(root).as_posix()}:1: "
                            "outside-repository Markdown file")
            continue
        text = file.read_text(encoding="utf-8", errors="replace")
        for lineno, target in links_in(text):
            path, _, fragment = target.partition("#")
            path = urllib.parse.unquote(path)
            fragment = urllib.parse.unquote(fragment)
            resolved = ((root / path.lstrip("/")) if path.startswith("/")
                        else (file.parent / path) if path else file).resolve()
            rel = file.relative_to(root).as_posix()
            if not resolved.is_relative_to(root):
                findings.append(f"{rel}:{lineno}: outside-repository link -> {target}")
                continue
            if not resolved.exists():
                findings.append(f"{rel}:{lineno}: broken link -> {target}")
                continue
            if (fragment and resolved.is_file() and resolved.suffix.lower() == ".md"):
                if resolved not in anchor_cache:
                    anchor_cache[resolved] = anchors_in(resolved.read_text(
                        encoding="utf-8", errors="replace"))
                if fragment not in anchor_cache[resolved]:
                    findings.append(f"{rel}:{lineno}: broken fragment -> {target}")
            if (file.name == "README.md" and resolved.suffix == ".md"
                    and file.parent.resolve() in resolved.parents):
                linked_from_index.add(resolved)

    for file in files:
        if docs not in file.parents or file.name == "README.md":
            continue
        if file.resolve() not in linked_from_index:
            rel = file.relative_to(root).as_posix()
            findings.append(f"{rel}:1: not listed from any README.md index above it")

    for directory in sorted({p.parent for p in files if docs in p.parents}):
        if not (directory / "README.md").is_file():
            rel = directory.relative_to(root).as_posix()
            findings.append(f"{rel}/: directory under docs/ has no README.md index")

    return files, findings


def main() -> int:
    files, findings = check()

    if findings:
        for finding in findings:
            print(finding)
        print(f"docs_linkcheck: {len(findings)} finding(s)")
        return 1
    print(f"docs_linkcheck: {len(files)} markdown files, supported local links/fragments resolve, "
          "every page is indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
