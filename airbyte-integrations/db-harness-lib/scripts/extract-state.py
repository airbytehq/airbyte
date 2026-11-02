#!/usr/bin/env -S uv run --script
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

# /// script
# requires-python = ">=3.11"
# ///
"""Extract Airbyte STATE values from a regression-test stdout.txt.

Reads JSONL from the given file (or stdin), filters to AirbyteMessages
whose `type` is `STATE`, unwraps each one to its inner
`AirbyteStateMessage` (`msg["state"]`), and writes the resulting list
to stdout.

The connector's `--state-path` expects a JSON array of
AirbyteStateMessage objects (each with `type` in
`{GLOBAL, STREAM, LEGACY}`), not the outer AirbyteMessage envelope. By
default this script keeps only the most recent STATE message — which
is what a real platform sync would replay on the next run.

Usage:
  extract-state.py /path/to/stdout.txt > state.json
  extract-state.py --all /path/to/stdout.txt > state.json
  extract-state.py < /path/to/stdout.txt > state.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    args = sys.argv[1:]
    keep_all = False
    if args and args[0] == "--all":
        keep_all = True
        args = args[1:]
    text = Path(args[0]).read_text() if args else sys.stdin.read()

    states: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "STATE" and isinstance(msg.get("state"), dict):
            states.append(msg["state"])

    if not states:
        print("[extract-state] no STATE messages found", file=sys.stderr)
        return 1

    output = states if keep_all else [states[-1]]
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
