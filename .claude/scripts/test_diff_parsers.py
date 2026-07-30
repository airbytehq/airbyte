#!/usr/bin/env python3
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for annotate_diff_lines.py and review_pr_validate_findings.py.

Run directly -- stdlib only, no pytest, no CI wiring:

    python3 .claude/scripts/test_diff_parsers.py

The two parsers MUST agree with each other AND with the real file. Agreeing only
with each other is the dangerous failure: a shifted line number that both
produce still anchors, so it ships into the report looking validated while the
correctly numbered finding is discarded as unanchored. Every test here asserts
against hand-checked real line numbers, never against the other parser.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


def _load(module_name: str):
    path = Path(__file__).with_name(module_name + ".py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclasses needs the module registered
    spec.loader.exec_module(module)
    return module


annotate_mod = _load("annotate_diff_lines")
validate_mod = _load("review_pr_validate_findings")


def anchored_lines(diff: str, path: str) -> list[tuple[str, int, str]]:
    files = validate_mod._parse_diff(diff)
    if path not in files:
        return []
    return [(c.side, c.line_number, c.content) for c in files[path].changed_lines]


# A hunk whose changed lines include content that LOOKS like a file marker.
# Old file:  1 title: x | 2 --- | 3 line3 | 4 old_value_here | 5 line5
# New file:  1 title: x | 2 ++new marker | 3 line3 | 4 new_value_here | 5 line5
MARKER_CONTENT_DIFF = """\
diff --git a/docs/foo.md b/docs/foo.md
index 1111111..2222222 100644
--- a/docs/foo.md
+++ b/docs/foo.md
@@ -1,5 +1,5 @@
 title: x
----
+++new marker
 line3
-old_value_here
+new_value_here
 line5
"""

HEADERLESS_MULTIFILE_DIFF = """\
--- a/alpha.py
+++ b/alpha.py
@@ -10,2 +10,2 @@
 alpha_context
-alpha_removed_line
+alpha_added_line
--- a/beta.py
+++ b/beta.py
@@ -50,2 +50,2 @@
 beta_context
-beta_removed_line
+beta_added_line
"""


class MarkerLikeContentTest(unittest.TestCase):
    """A changed line starting with `--`/`++` must not shift the numbering."""

    def test_annotate_reports_real_line_numbers(self):
        rendered = annotate_mod.annotate(MARKER_CONTENT_DIFF)
        self.assertIn("-      2 | ---", rendered)
        self.assertIn("+      2 | ++new marker", rendered)
        self.assertIn("-      4 | old_value_here", rendered)
        self.assertIn("+      4 | new_value_here", rendered)

    def test_validator_agrees_with_the_real_file(self):
        self.assertEqual(
            anchored_lines(MARKER_CONTENT_DIFF, "docs/foo.md"),
            [
                ("removed", 2, "---"),
                ("added", 2, "++new marker"),
                ("removed", 4, "old_value_here"),
                ("added", 4, "new_value_here"),
            ],
        )

    def test_finding_on_the_real_line_anchors(self):
        finding = {"file": "docs/foo.md", "line": 4, "diff_quote": "+new_value_here"}
        buckets = validate_mod._bucketize([finding], validate_mod._parse_diff(MARKER_CONTENT_DIFF))
        self.assertEqual(len(buckets["anchored"]), 1, "a correctly numbered finding must anchor")

    def test_finding_on_the_shifted_line_does_not_anchor(self):
        finding = {"file": "docs/foo.md", "line": 3, "diff_quote": "+new_value_here"}
        buckets = validate_mod._bucketize([finding], validate_mod._parse_diff(MARKER_CONTENT_DIFF))
        self.assertEqual(len(buckets["needs_review"]), 1, "an off-by-one must NOT silently anchor")


class RoundTripTest(unittest.TestCase):
    """Every line the annotator emits must anchor when quoted back verbatim."""

    def test_annotated_numbers_anchor(self):
        rendered = annotate_mod.annotate(MARKER_CONTENT_DIFF)
        findings = []
        for line in rendered.splitlines():
            if line[:1] not in "+-":
                continue
            side, rest = line[0], line[1:]
            number, _, content = rest.partition(" | ")
            # A quote too short to anchor is a documented limit, not drift; it is
            # covered by BucketizeTest.test_short_quote_cannot_anchor.
            if len(content.strip()) < validate_mod._MIN_ANCHOR_QUOTE_LEN:
                continue
            findings.append({"file": "docs/foo.md", "line": int(number.strip()), "diff_quote": side + content})
        self.assertTrue(findings)
        buckets = validate_mod._bucketize(findings, validate_mod._parse_diff(MARKER_CONTENT_DIFF))
        self.assertEqual(len(buckets["anchored"]), len(findings), "every annotated line must anchor when quoted back verbatim")


class HeaderlessDiffTest(unittest.TestCase):
    """`diff -u` / `git diff --no-prefix` output has no `diff --git` headers."""

    def test_annotate_emits_both_files(self):
        rendered = annotate_mod.annotate(HEADERLESS_MULTIFILE_DIFF)
        self.assertIn("### alpha.py", rendered)
        self.assertIn("### beta.py", rendered)
        self.assertIn("+     11 | alpha_added_line", rendered)
        self.assertIn("+     51 | beta_added_line", rendered)

    def test_validator_attributes_each_file_separately(self):
        self.assertEqual(
            anchored_lines(HEADERLESS_MULTIFILE_DIFF, "alpha.py"),
            [("removed", 11, "alpha_removed_line"), ("added", 11, "alpha_added_line")],
        )
        self.assertEqual(
            anchored_lines(HEADERLESS_MULTIFILE_DIFF, "beta.py"), [("removed", 51, "beta_removed_line"), ("added", 51, "beta_added_line")]
        )


class OrdinaryDiffTest(unittest.TestCase):
    """The common shapes must keep working exactly as before."""

    def test_multiple_hunks_and_files(self):
        diff = """\
diff --git a/a.py b/a.py
index 1111111..2222222 100644
--- a/a.py
+++ b/a.py
@@ -1,3 +1,3 @@
 keep
-was_here
+is_here
@@ -20,3 +20,4 @@
 context
+brand_new_line
 tail
diff --git a/b.py b/b.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/b.py
@@ -0,0 +1,2 @@
+created_one
+created_two
"""
        self.assertEqual(
            anchored_lines(diff, "a.py"), [("removed", 2, "was_here"), ("added", 2, "is_here"), ("added", 21, "brand_new_line")]
        )
        self.assertEqual(anchored_lines(diff, "b.py"), [("added", 1, "created_one"), ("added", 2, "created_two")])
        rendered = annotate_mod.annotate(diff)
        self.assertIn("+     21 | brand_new_line", rendered)
        self.assertIn("### b.py", rendered)

    def test_single_line_hunk_without_counts(self):
        diff = """\
diff --git a/c.py b/c.py
--- a/c.py
+++ b/c.py
@@ -7 +7 @@
-before_value
+after_value
"""
        self.assertEqual(anchored_lines(diff, "c.py"), [("removed", 7, "before_value"), ("added", 7, "after_value")])

    def test_no_newline_marker_is_not_a_changed_line(self):
        diff = """\
diff --git a/d.py b/d.py
--- a/d.py
+++ b/d.py
@@ -1,2 +1,2 @@
 keep_this
-old_tail_value
\\ No newline at end of file
+new_tail_value
\\ No newline at end of file
"""
        self.assertEqual(anchored_lines(diff, "d.py"), [("removed", 2, "old_tail_value"), ("added", 2, "new_tail_value")])

    def test_rename_resolves_under_both_paths(self):
        diff = """\
diff --git a/old_name.py b/new_name.py
similarity index 90%
rename from old_name.py
rename to new_name.py
--- a/old_name.py
+++ b/new_name.py
@@ -3,2 +3,2 @@
-renamed_before
+renamed_after
"""
        files = validate_mod._parse_diff(diff)
        self.assertIs(files["old_name.py"], files["new_name.py"])

    def test_empty_diff_is_not_an_error(self):
        self.assertEqual(annotate_mod.annotate("").strip(), "")
        self.assertEqual(validate_mod._parse_diff(""), {})


class BucketizeTest(unittest.TestCase):
    def test_side_marker_is_enforced(self):
        diff = MARKER_CONTENT_DIFF
        removed_quote_on_added_line = {"file": "docs/foo.md", "line": 4, "diff_quote": "-new_value_here"}
        buckets = validate_mod._bucketize([removed_quote_on_added_line], validate_mod._parse_diff(diff))
        self.assertEqual(len(buckets["needs_review"]), 1)

    def test_causal_quote_matches_anywhere_in_the_file(self):
        finding = {"file": "docs/foo.md", "line": 999, "causal_diff_quote": "+new_value_here"}
        buckets = validate_mod._bucketize([finding], validate_mod._parse_diff(MARKER_CONTENT_DIFF))
        self.assertEqual(len(buckets["causal"]), 1)

    def test_unknown_file_needs_review(self):
        finding = {"file": "not/in/diff.py", "line": 1, "diff_quote": "+whatever_value"}
        buckets = validate_mod._bucketize([finding], validate_mod._parse_diff(MARKER_CONTENT_DIFF))
        self.assertEqual(len(buckets["needs_review"]), 1)

    def test_short_quote_cannot_anchor(self):
        # Documented behaviour: a normalized quote below _MIN_ANCHOR_QUOTE_LEN is
        # rejected. Pinned here so the threshold is a decision, not an accident.
        finding = {"file": "docs/foo.md", "line": 2, "diff_quote": "----"}
        buckets = validate_mod._bucketize([finding], validate_mod._parse_diff(MARKER_CONTENT_DIFF))
        self.assertEqual(len(buckets["needs_review"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
