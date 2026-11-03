#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import sys
from pathlib import Path

import pytest
from destination_amazon_sqs.run import run


def test_run_emits_spec(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["destination-amazon-sqs", "spec"])

    run()

    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()]
    spec_message = next(message for message in messages if message.get("type") == "SPEC")
    spec_path = Path(__file__).parent.parent / "destination_amazon_sqs" / "spec.json"
    expected_spec = json.loads(spec_path.read_text())
    assert spec_message["spec"]["connectionSpecification"] == expected_spec["connectionSpecification"]
