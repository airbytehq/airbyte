#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import subprocess
import sys
from pathlib import Path


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]


def test_spec_entrypoint() -> None:
    result = subprocess.run([sys.executable, "main.py", "spec"], cwd=CONNECTOR_ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr + result.stdout
    messages = [json.loads(line) for line in result.stdout.splitlines()]
    spec = next(message["spec"] for message in messages if message["type"] == "SPEC")
    assert spec == json.loads((CONNECTOR_ROOT / "source_zenloop/spec.json").read_text())
