#!/usr/bin/env python3
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Validate PR review findings against actual diff hunks.

Usage: review_pr_validate_findings.py <diff-file> <findings-json>

Reads the unified diff from <diff-file> and a JSON array of findings from
<findings-json>, then bucketizes each finding into one of three lists:

  - anchored: the finding's `file` is in the diff AND `line` matches the
    new-file (for `+`) or old-file (for `-`) line number of a changed
    line whose content contains the finding's `diff_quote` (substring
    match, whitespace-tolerant, minimum length enforced).
  - causal:   the finding's `file` is in the diff AND its
    `causal_diff_quote` matches a changed line anywhere in the same
    file. Preserves the "nearby-unchanged-but-now-broken" pattern where
    the finding sits on an unchanged line but a changed call site in
    the same file caused the regression. Prose alone (a `causal_link`
    string without a quoted changed line) is NOT sufficient.

    IMPORTANT -- this bucket is NOT a causality proof, despite the name.
    It establishes only that the quoted text appears among the changed
    lines SOMEWHERE in the same file: there is no proximity, ordering,
    or dataflow check. Callers must weigh the finding's stated causal
    mechanism themselves, and must not describe this bucket as
    "mechanically validated causality". Note also that a removed-line
    (`-`) anchor resolves to an OLD-file line number, so a `file:line`
    derived from it does not point at the same content at the PR head.
  - needs_review: everything else -- file not in diff, `line` missing/
    wrong, `diff_quote` does not match the recorded line, or the
    causal_diff_quote is absent/doesn't match a changed line. Surfaced
    to the coordinator for manual re-check; never silently dropped.

Output: JSON object {"anchored": [...], "causal": [...], "needs_review": [...]}.

Exit 0 on successful bucketization (including empty diff or all-unmatched).
Exit 2 only when the diff or findings input is malformed (cannot be parsed).

Stderr emits a one-line summary:
  [review_pr_validate] N in, A anchored, C causal, R needs_review

Coordinator contract:
  * `anchored[]` and `causal[]` count toward the remediation plan/verdict.
  * `needs_review[]` is reported separately as unvalidated material and
    MUST be excluded from issue counts unless the coordinator manually
    verifies each entry against the diff.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


_DIFF_HEADER_RE = re.compile(r"^diff --git " r'(?:"a/(?P<old_q>[^"]+)"|a/(?P<old>\S+)) ' r'(?:"b/(?P<new_q>[^"]+)"|b/(?P<new>\S+))\s*$')
_HUNK_HEADER_RE = re.compile(r"^@@ -(?P<old>\d+)(?:,(?P<old_count>\d+))? \+(?P<new>\d+)(?:,(?P<new_count>\d+))? @@")
_FILE_MARKER_RE = re.compile(r'^(?:---|\+\+\+) (?:"[ab]/(?P<path_q>[^"]+)"|[ab]/(?P<path>\S+))\s*$')
_WHITESPACE_RE = re.compile(r"\s+")

_MIN_ANCHOR_QUOTE_LEN = 5


def _diff_header_paths(match: re.Match) -> tuple[str, str]:
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


@dataclass
class ChangedLine:
    content: str
    line_number: int
    side: str  # "added" or "removed"


@dataclass
class DiffFile:
    path: str
    changed_lines: list[ChangedLine] = field(default_factory=list)


def _normalize(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def _parse_diff(diff_text: str) -> dict[str, DiffFile]:
    files: dict[str, DiffFile] = {}
    current: DiffFile | None = None
    old_line_no = 0
    new_line_no = 0
    old_left = 0
    new_left = 0
    in_hunk = False

    for raw in diff_text.splitlines():
        header = _DIFF_HEADER_RE.match(raw)
        if header:
            old_path, new_path = _diff_header_paths(header)
            primary = new_path if new_path != "/dev/null" else old_path
            current = DiffFile(path=primary)
            files[primary] = current
            if old_path and old_path != primary and old_path != "/dev/null":
                files[old_path] = current
            in_hunk = False
            continue

        # Bare `---`/`+++` markers, for diffs with no `diff --git` headers. Only
        # consulted OUTSIDE a hunk: inside one they are content (see below).
        marker = _FILE_MARKER_RE.match(raw)
        if marker and not in_hunk:
            path = _file_marker_path(marker)
            if path == "/dev/null" or not path:
                continue
            current = files.get(path) or DiffFile(path=path)
            files.setdefault(path, current)
            continue

        if current is None:
            continue

        hunk = _HUNK_HEADER_RE.match(raw)
        if hunk:
            old_line_no = int(hunk.group("old"))
            new_line_no = int(hunk.group("new"))
            old_left, new_left = _hunk_lengths(hunk)
            in_hunk = True
            continue

        # `in_hunk` MUST gate everything below, and the hunk's declared lengths
        # are what end it. Inside a hunk, `----` is the removal of a line whose
        # content is `---` (a YAML document separator, a markdown rule) and
        # `+++x` is the addition of `++x` -- both are content, not file markers.
        # Treating them as markers and skipping them without advancing the
        # counter shifts every later line number in the file, and since
        # annotate_diff_lines.py parses identically, the shifted number still
        # anchors here: a real finding lands on the wrong line while a correctly
        # numbered one is discarded as unanchored.
        if not in_hunk or raw.startswith("\\"):
            continue

        if raw.startswith("+"):
            content = _normalize(raw[1:])
            if content:
                current.changed_lines.append(ChangedLine(content=content, line_number=new_line_no, side="added"))
            new_line_no += 1
            new_left -= 1
        elif raw.startswith("-"):
            content = _normalize(raw[1:])
            if content:
                current.changed_lines.append(ChangedLine(content=content, line_number=old_line_no, side="removed"))
            old_line_no += 1
            old_left -= 1
        else:
            old_line_no += 1
            new_line_no += 1
            old_left -= 1
            new_left -= 1

        if old_left <= 0 and new_left <= 0:
            in_hunk = False

    return files


def _finding_path(finding: dict) -> str | None:
    path = finding.get("file")
    if not isinstance(path, str) or not path.strip():
        return None
    return path.strip()


def _parse_quote(raw: object) -> tuple[str | None, str] | None:
    """Return (required_side, normalized_content) for a raw diff_quote value.

    `required_side` is "added" when the quote begins with `+`, "removed" when it
    begins with `-`, and None when the quote has no leading marker (side-agnostic
    match, preserves back-compat for agents that stripped the prefix).

    Returns None when the quote is not a non-empty string or the normalized
    content falls below the minimum anchor length.
    """
    if not isinstance(raw, str):
        return None
    stripped = raw.strip()
    if not stripped:
        return None

    # Strip exactly ONE marker character. Do NOT special-case `+++`/`---` here:
    # a quote of `+++new marker` is the addition of the line `++new marker`, and
    # refusing to strip its prefix leaves an unmatchable `+++new marker` that
    # cannot anchor against any real content. A quote of a genuine file marker
    # (`--- a/foo.py`) still fails to match any changed line, which is the
    # outcome we want for it anyway.
    side: str | None = None
    if stripped.startswith("+"):
        side = "added"
        stripped = stripped[1:]
    elif stripped.startswith("-"):
        side = "removed"
        stripped = stripped[1:]

    normalized = _normalize(stripped)
    if len(normalized) < _MIN_ANCHOR_QUOTE_LEN:
        return None
    return side, normalized


def _match_diff_quote(finding: dict, diff_file: DiffFile) -> bool:
    """Return True only if (file, line, diff_quote) all anchor to the same changed line.

    If the raw `diff_quote` carries a leading `+` / `-` marker, the changed
    line's `side` must match it. A `+someCall();` quote must not anchor
    against a `-someCall();` removal at the same line, and vice versa.
    """
    parsed = _parse_quote(finding.get("diff_quote"))
    if parsed is None:
        return False
    required_side, normalized = parsed

    line = finding.get("line")
    if not isinstance(line, int) or isinstance(line, bool):
        return False

    for cl in diff_file.changed_lines:
        if cl.line_number != line:
            continue
        if required_side is not None and cl.side != required_side:
            continue
        if normalized in cl.content:
            return True
    return False


def _match_causal(finding: dict, diff_file: DiffFile) -> bool:
    """Return True if causal_diff_quote names an actual changed line in the same file.

    Prose alone (a `causal_link` string without a quoted changed line) is NOT
    sufficient -- the agent must quote the changed hunk that caused the
    regression, even though the finding itself sits on an unchanged line.

    Side enforcement: if the raw quote carries a leading `+` / `-` marker, the
    changed line's `side` must match.
    """
    parsed = _parse_quote(finding.get("causal_diff_quote"))
    if parsed is None:
        return False
    required_side, normalized = parsed

    for cl in diff_file.changed_lines:
        if required_side is not None and cl.side != required_side:
            continue
        if normalized in cl.content:
            return True
    return False


def _bucketize(findings: list[dict], files: dict[str, DiffFile]) -> dict[str, list[dict]]:
    anchored: list[dict] = []
    causal: list[dict] = []
    needs_review: list[dict] = []

    for finding in findings:
        if not isinstance(finding, dict):
            needs_review.append({"raw": finding, "reason": "finding is not a JSON object"})
            continue

        path = _finding_path(finding)
        if path is None:
            needs_review.append(finding)
            continue

        diff_file = files.get(path)
        if diff_file is None:
            needs_review.append(finding)
            continue

        if _match_diff_quote(finding, diff_file):
            anchored.append(finding)
            continue

        if _match_causal(finding, diff_file):
            causal.append(finding)
            continue

        needs_review.append(finding)

    return {"anchored": anchored, "causal": causal, "needs_review": needs_review}


def _load_findings(path: Path) -> list[dict]:
    try:
        raw = path.read_text()
    except OSError as exc:
        raise SystemExit(f"[review_pr_validate] cannot read findings file: {exc}") from exc
    try:
        data = json.loads(raw) if raw.strip() else []
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[review_pr_validate] malformed findings JSON: {exc}") from exc
    if not isinstance(data, list):
        raise SystemExit("[review_pr_validate] findings JSON must be an array")
    return data


def _load_diff(path: Path) -> str:
    try:
        return path.read_text()
    except OSError as exc:
        raise SystemExit(f"[review_pr_validate] cannot read diff file: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("diff_file", help="Path to unified diff (e.g., output of `gh pr diff <PR>`)")
    parser.add_argument("findings_file", help="Path to JSON array of findings from review agents")
    args = parser.parse_args()

    try:
        diff_text = _load_diff(Path(args.diff_file))
        findings = _load_findings(Path(args.findings_file))
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2

    files = _parse_diff(diff_text)
    buckets = _bucketize(findings, files)

    summary = (
        f"[review_pr_validate] {len(findings)} in, "
        f"{len(buckets['anchored'])} anchored, "
        f"{len(buckets['causal'])} causal, "
        f"{len(buckets['needs_review'])} needs_review"
    )
    print(summary, file=sys.stderr)
    print(json.dumps(buckets, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
