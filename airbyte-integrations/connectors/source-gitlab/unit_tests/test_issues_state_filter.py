#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _issues_record_filter() -> dict:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    issues = manifest["definitions"]["issues_stream"]
    return issues["retriever"]["record_selector"]["record_filter"]


def test_issues_stream_has_record_filter():
    record_filter = _issues_record_filter()
    assert record_filter["type"] == "RecordFilter"
    assert "state" in record_filter["condition"]


def test_issues_filter_keeps_open_issues():
    condition = _issues_record_filter()["condition"]
    assert "opened" in condition
