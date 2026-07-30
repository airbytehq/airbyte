#!/usr/bin/env python3
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Emit a unified diff's changed lines with their resolved file line numbers.

Usage: annotate_diff_lines.py <diff-file> [--out <path>]

Review agents are otherwise asked to compute line numbers by hand from `@@`
hunk headers, which is the least reliable step in a review pipeline: an
off-by-one silently demotes a real finding to "unanchored" and it gets dropped.
This script does that arithmetic mechanically so agents can quote a line number
instead of deriving one.

Output format, one block per file:

    ### <repo-relative path>
    +    120 | some added line
    -     87 | some removed line

The number is the NEW-file line number for `+` lines and the OLD-file line
number for `-` lines -- exactly the convention review_pr_validate_findings.py
enforces when anchoring findings, so a quoted number round-trips.

Context lines are omitted: only changed lines are anchorable.

Files are recognised from `diff --git` headers, falling back to bare `---`/`+++`
markers so a diff produced without them (`diff -u`, `git diff --no-prefix`) is
still annotated rather than silently yielding nothing.

Exit 0 on success (including an empty diff). Exit 2 when the diff cannot be read,
or when a non-empty diff produced no annotated lines at all -- that means the
input was not in a shape this parser understands, and a caller must not read the
empty result as "nothing changed".
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_DIFF_HEADER_RE = re.compile(r"^diff --git " r'(?:"a/(?P<old_q>[^"]+)"|a/(?P<old>\S+)) ' r'(?:"b/(?P<new_q>[^"]+)"|b/(?P<new>\S+))\s*$')
_HUNK_HEADER_RE = re.compile(r"^@@ -(?P<old>\d+)(?:,(?P<old_count>\d+))? \+(?P<new>\d+)(?:,(?P<new_count>\d+))? @@")
_FILE_MARKER_RE = re.compile(r'^(?:---|\+\+\+) (?:"[ab]/(?P<path_q>[^"]+)"|[ab]/(?P<path>\S+))\s*$')


def _header_paths(match: re.Match) -> tuple[str, str]:
    old = match.group("old_q") or match.group("old") or ""
    new = match.group("new_q") or match.group("new") or ""
    return old, new


def _file_marker_path(match: re.Match) -> str:
    return match.group("path_q") or match.group("path") or ""


def _hunk_lengths(match: re.Match) -> tuple[int, int]:
    """Return (old_length, new_length) for a hunk header.

    An omitted count means 1 (`@@ -3 +3 @@`). These lengths are what let the
    parser know where a hunk ENDS, which is the only reliable way to tell a
    `--- a/next_file.py` file marker from the removal of a line whose content
    happens to start with `--`.
    """
    return int(match.group("old_count") or 1), int(match.group("new_count") or 1)


def annotate(diff_text: str) -> str:
    out: list[str] = []
    current: str | None = None
    old_no = 0
    new_no = 0
    old_left = 0
    new_left = 0
    in_hunk = False
    emitted_for_file = False
    seen_paths: set[str] = set()

    for raw in diff_text.splitlines():
        header = _DIFF_HEADER_RE.match(raw)
        if header:
            old_path, new_path = _header_paths(header)
            current = new_path if new_path != "/dev/null" else old_path
            seen_paths.add(current)
            in_hunk = False
            emitted_for_file = False
            continue

        # Bare `---`/`+++` markers, for diffs with no `diff --git` headers. Only
        # consulted OUTSIDE a hunk: inside one they are content (see below).
        marker = _FILE_MARKER_RE.match(raw)
        if marker and not in_hunk:
            path = _file_marker_path(marker)
            if path and path != "/dev/null" and path != current:
                current = path
                emitted_for_file = path in seen_paths
                seen_paths.add(path)
            continue

        if current is None:
            continue

        hunk = _HUNK_HEADER_RE.match(raw)
        if hunk:
            old_no = int(hunk.group("old"))
            new_no = int(hunk.group("new"))
            old_left, new_left = _hunk_lengths(hunk)
            in_hunk = True
            continue

        # `in_hunk` MUST gate everything below, and the hunk's declared lengths
        # are what end it. Inside a hunk, `----` is the removal of a line whose
        # content is `---` (a YAML document separator, a markdown rule) and
        # `+++x` is the addition of `++x` -- both are content, not file markers.
        # Treating them as markers and skipping them without advancing the
        # counter shifts every later line number in the file, and because
        # review_pr_validate_findings.py parses identically, the wrong number
        # still anchors: a real finding lands on the wrong line while a
        # correctly numbered one is discarded as unanchored.
        if not in_hunk or raw.startswith("\\"):
            continue

        if raw.startswith("+"):
            if raw[1:].strip():
                if not emitted_for_file:
                    out.append("")
                    out.append(f"### {current}")
                    emitted_for_file = True
                out.append(f"+ {new_no:>6} | {raw[1:]}")
            new_no += 1
            new_left -= 1
        elif raw.startswith("-"):
            if raw[1:].strip():
                if not emitted_for_file:
                    out.append("")
                    out.append(f"### {current}")
                    emitted_for_file = True
                out.append(f"- {old_no:>6} | {raw[1:]}")
            old_no += 1
            old_left -= 1
        else:
            # context line
            old_no += 1
            new_no += 1
            old_left -= 1
            new_left -= 1

        if old_left <= 0 and new_left <= 0:
            in_hunk = False

    return "\n".join(out).lstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("diff_file", help="Path to a unified diff")
    parser.add_argument("--out", type=Path, help="Write here instead of stdout")
    args = parser.parse_args()

    try:
        diff_text = Path(args.diff_file).read_text()
    except OSError as exc:
        print(f"[annotate_diff_lines] cannot read diff: {exc}", file=sys.stderr)
        return 2

    rendered = annotate(diff_text)
    changed = sum(1 for line in rendered.splitlines() if line[:1] in "+-")
    print(f"[annotate_diff_lines] {changed} changed lines annotated", file=sys.stderr)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    else:
        sys.stdout.write(rendered)

    if changed == 0 and diff_text.strip():
        # Empty output from a non-empty diff means the input was not in a shape
        # this parser understands -- not that nothing changed. Fail loudly so a
        # caller cannot mistake one for the other.
        print("[annotate_diff_lines] the diff was non-empty but no changed lines were parsed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
