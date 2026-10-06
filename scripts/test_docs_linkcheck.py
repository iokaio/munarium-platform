# SPDX-License-Identifier: Apache-2.0
"""Regression and negative controls for the documented Markdown gate subset."""
from __future__ import annotations

import pathlib
import tempfile
import unittest
from unittest.mock import patch

import docs_linkcheck


class DocumentationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)

    def write(self, name: str, content: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def findings(self) -> list[str]:
        return docs_linkcheck.check(self.root)[1]

    def test_historical_numbered_toc_is_rejected_before_repair(self) -> None:
        # These are the exported link forms that previously passed the gate.
        self.write("README.md", """
[Registry](#munarium-registry-the-inventory-of-governed-capability)
[Appendix](#appendix-i.-matrix-consolidation-and-the-1.2.0-release)
# 7. Munarium Registry: the inventory of governed capability
# Appendix I. Matrix consolidation and the 1.2.0 release
""")
        findings = self.findings()
        self.assertEqual(len(findings), 2)
        self.assertIn("README.md:2: broken fragment", findings[0])
        self.assertIn("README.md:3: broken fragment", findings[1])

    def test_repaired_numbered_toc_and_appendix_resolve(self) -> None:
        self.write("README.md", """
[Registry](#7-munarium-registry-the-inventory-of-governed-capability)
[Appendix](#appendix-i-matrix-consolidation-and-the-120-release)
# 7. Munarium Registry: the inventory of governed capability
# Appendix I. Matrix consolidation and the 1.2.0 release
""")
        self.assertEqual(self.findings(), [])

    def test_cross_file_fragments_decode_paths_and_unicode(self) -> None:
        self.write("README.md", "[Résumé](docs/space%20name.md#caf%C3%A9-%E6%9D%B1%E4%BA%AC)\n")
        self.write("docs/README.md", "[Résumé](space%20name.md#caf%C3%A9-%E6%9D%B1%E4%BA%AC)\n")
        self.write("docs/space name.md", "# Café 東京\n")
        self.assertEqual(self.findings(), [])
        self.write("README.md", "[Missing](docs/space%20name.md#absent)\n")
        self.assertEqual(self.findings(), [
            "README.md:1: broken fragment -> docs/space%20name.md#absent"])

    def test_encoded_hash_belongs_to_filename(self) -> None:
        self.write("README.md", "[Target](part%23one.md#part)\n")
        self.write("part#one.md", "# Part\n")
        self.assertEqual(self.findings(), [])

    def test_duplicate_heading_suffixes_include_collisions(self) -> None:
        self.write("README.md", """
# Repeat
# Repeat-1
# Repeat
# Repeat
# Repeat-1
[First](#repeat) [Literal](#repeat-1) [Second](#repeat-2)
[Third](#repeat-3) [Literal duplicate](#repeat-1-1)
""")
        self.assertEqual(self.findings(), [])
        self.write("other.md", "[Absent](README.md#repeat-4)\n")
        self.assertEqual(len(self.findings()), 1)

    def test_inline_formatting_and_setext_heading(self) -> None:
        self.write("README.md", """
## **Bold** *italic* __underlined__ _emphasis_ `some_code` [Link](https://example.org) ###
[Formatted](#bold-italic-underlined-emphasis-some_code-link)
Plain &amp; useful
==================
[Setext](#plain--useful)
""")
        self.assertEqual(self.findings(), [])

    def test_fenced_examples_are_neither_links_nor_headings(self) -> None:
        self.write("README.md", """
````markdown
# Fake
[Missing](does-not-exist.md)
```
[Also missing](#absent)
````
~~~markdown
# Also fake
~~~
# Real
[Real](#real)
[Fake](#fake)
""")
        self.assertEqual(self.findings(), ["README.md:13: broken fragment -> #fake"])

    def test_code_heading_text_is_literal_not_markup(self) -> None:
        self.write("README.md", """
# `_arg_` `<T>` `&amp;`
[Literal code](#_arg_-t-amp)
""")
        self.assertEqual(self.findings(), [])

    def test_comments_and_inline_code_do_not_create_links_or_anchors(self) -> None:
        self.write("README.md", """
<!--
# Hidden
[Missing](missing.md)
-->
`[Missing](missing.md)` and ``<a id="code-anchor"></a>``
# Visible <!-- ignored heading text -->
[Visible](#visible)
[Hidden](#hidden) [Code anchor](#code-anchor)
""")
        self.assertEqual(len(self.findings()), 2)
        self.assertTrue(all(":9: broken fragment" in item for item in self.findings()))

    def test_explicit_html_anchors_and_case_sensitive_fragments(self) -> None:
        self.write("README.md", """
<a id="Exact-ID"></a>
<a name='legacy'></a>
[Exact](#Exact-ID) [Legacy](#legacy)
[Wrong case](#exact-id)
""")
        self.assertEqual(self.findings(), ["README.md:5: broken fragment -> #exact-id"])

    def test_non_markdown_fragments_and_remote_links_remain_outside_scope(self) -> None:
        self.write("README.md", """
[Paper](paper.pdf#page=4)
[Remote](https://example.org/absent#absent)
[Email](mailto:example@example.org)
[External](//example.org/absent)
[Start](#)
""")
        self.write("paper.pdf", "not a PDF; only path existence is checked\n")
        self.assertEqual(self.findings(), [])

    def test_root_relative_links_and_quoted_titles(self) -> None:
        self.write("README.md", "[Docs](docs/README.md)\n")
        self.write("docs/README.md", "[Guide](</guide name.md#one> \"Guide\")\n")
        self.write("guide name.md", "# One\n")
        self.assertEqual(self.findings(), [])

    def test_unicode_combining_marks_preserve_distinct_heading_text(self) -> None:
        self.write("README.md", "# Café\n# Cafe\u0301\n[Café](#caf%C3%A9)\n[Other](#cafe%CC%81)\n")
        self.assertEqual(self.findings(), [])

    def test_path_and_index_checks_are_retained(self) -> None:
        self.write("README.md", "[Missing](missing.md#anywhere)\n")
        self.write("docs/orphan.md", "# Orphan\n")
        self.assertEqual(self.findings(), [
            "README.md:1: broken link -> missing.md#anywhere",
            "docs/orphan.md:1: not listed from any README.md index above it",
            "docs/: directory under docs/ has no README.md index",
        ])

    def test_external_markdown_target_is_rejected_without_reading_it(self) -> None:
        self.root = self.root / "workspace"
        self.root.mkdir()
        outside = self.root.parent / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        self.write("README.md", "[Outside](../outside.md#outside)\n")
        original_read = pathlib.Path.read_text

        def bounded_read(path: pathlib.Path, *args: object, **kwargs: object) -> str:
            self.assertTrue(path.resolve().is_relative_to(self.root.resolve()),
                            "The checker attempted to read outside the repository")
            return original_read(path, *args, **kwargs)

        with patch.object(pathlib.Path, "read_text", bounded_read):
            self.assertEqual(self.findings(), [
                "README.md:1: outside-repository link -> ../outside.md#outside"])

    def test_resolved_symlink_cannot_escape_the_read_boundary(self) -> None:
        self.root = self.root / "workspace"
        self.root.mkdir()
        outside = self.root.parent / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        alias = self.root / "alias.md"
        alias.write_text("# Placeholder for a resolved symlink\n", encoding="utf-8")
        self.write("README.md", "[Outside](alias.md#outside)\n")
        original_read = pathlib.Path.read_text
        original_resolve = pathlib.Path.resolve

        def resolve_link(path: pathlib.Path, *args: object, **kwargs: object) -> pathlib.Path:
            # Model the OS resolution result without requiring Windows symlink privileges.
            resolved = original_resolve(path, *args, **kwargs)
            return outside if resolved == alias else resolved

        def bounded_read(path: pathlib.Path, *args: object, **kwargs: object) -> str:
            self.assertTrue(path.resolve().is_relative_to(self.root.resolve()),
                            "The checker attempted to follow an external symlink")
            return original_read(path, *args, **kwargs)

        with patch.object(pathlib.Path, "resolve", resolve_link), \
                patch.object(pathlib.Path, "read_text", bounded_read):
            self.assertCountEqual(self.findings(), [
                "README.md:1: outside-repository link -> alias.md#outside",
                "alias.md:1: outside-repository Markdown file",
            ])


if __name__ == "__main__":
    unittest.main()
