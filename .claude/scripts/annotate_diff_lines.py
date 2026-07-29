#!/usr/bin/env python3
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

Exit 0 on success (including an empty diff). Exit 2 when the diff cannot be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_DIFF_HEADER_RE = re.compile(
    r"^diff --git "
    r'(?:"a/(?P<old_q>[^"]+)"|a/(?P<old>\S+)) '
    r'(?:"b/(?P<new_q>[^"]+)"|b/(?P<new>\S+))\s*$'
)
_HUNK_HEADER_RE = re.compile(r"^@@ -(?P<old>\d+)(?:,\d+)? \+(?P<new>\d+)(?:,\d+)? @@")


def _header_paths(match: re.Match) -> tuple[str, str]:
    old = match.group("old_q") or match.group("old") or ""
    new = match.group("new_q") or match.group("new") or ""
    return old, new


def annotate(diff_text: str) -> str:
    out: list[str] = []
    current: str | None = None
    old_no = 0
    new_no = 0
    in_hunk = False
    emitted_for_file = False

    for raw in diff_text.splitlines():
        header = _DIFF_HEADER_RE.match(raw)
        if header:
            old_path, new_path = _header_paths(header)
            current = new_path if new_path != "/dev/null" else old_path
            in_hunk = False
            emitted_for_file = False
            continue

        if current is None:
            continue

        hunk = _HUNK_HEADER_RE.match(raw)
        if hunk:
            old_no = int(hunk.group("old"))
            new_no = int(hunk.group("new"))
            in_hunk = True
            continue

        if raw.startswith("+++") or raw.startswith("---"):
            continue
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
            continue

        if raw.startswith("-"):
            if raw[1:].strip():
                if not emitted_for_file:
                    out.append("")
                    out.append(f"### {current}")
                    emitted_for_file = True
                out.append(f"- {old_no:>6} | {raw[1:]}")
            old_no += 1
            continue

        # context line
        old_no += 1
        new_no += 1

    return "\n".join(out).lstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
