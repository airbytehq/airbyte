#!/usr/bin/env -S uv run --script
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

# /// script
# requires-python = ">=3.11"
# ///
"""Blank the per-stream state inside a saved GLOBAL state file.

Reads the JSON array `extract-state.py` writes, and for every GLOBAL
state message replaces each `stream_states[*].stream_state` with `{}`
while leaving `shared_state` (the Debezium offset) untouched. This is
the exact shape the bulk CDK emits for a stream whose initial snapshot
was interrupted before its first checkpoint (airbytehq/airbyte#85286).

Usage:
  blank-stream-state.py state.json > empty-stream-state.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    states = json.loads(Path(sys.argv[1]).read_text())
    touched = 0
    for state in states:
        if state.get("type") != "GLOBAL":
            continue
        for stream_state in state.get("global", {}).get("stream_states", []):
            stream_state["stream_state"] = {}
            touched += 1
    if touched == 0:
        print("[blank-stream-state] no GLOBAL stream_states found", file=sys.stderr)
        return 1
    json.dump(states, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
