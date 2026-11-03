# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Guards for the 3.0.0 removal of the Zendesk Talk incremental call exports.

Zendesk ends Incremental API access for third-party integrations (rollout 2026-12-02 to
2027-01-19) and lists no alternative endpoint for `/stats/incremental/calls` and
`/stats/incremental/legs`, so the `calls` and `call_legs` streams were removed. These tests
make sure nothing re-introduces a stream on those endpoints by accident.
"""

from pathlib import Path

import yaml


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"
REMOVED_STREAMS = {"calls", "call_legs"}
EXPECTED_STREAMS = {
    "account_overview",
    "addresses",
    "agents_activity",
    "agents_overview",
    "current_queue_activity",
    "greeting_categories",
    "greetings",
    "ivr_menus",
    "ivr_routes",
    "ivrs",
    "phone_numbers",
}


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def test_removed_streams_are_gone_everywhere():
    manifest = _manifest()
    assert REMOVED_STREAMS.isdisjoint(manifest["definitions"]["streams"])
    assert REMOVED_STREAMS.isdisjoint(manifest["schemas"])
    assert REMOVED_STREAMS.isdisjoint(manifest["metadata"]["autoImportSchema"])
    assert REMOVED_STREAMS.isdisjoint(ref["$ref"].rsplit("/", 1)[-1] for ref in manifest["streams"])


def test_no_stream_uses_an_incremental_export_endpoint():
    manifest = _manifest()
    for name, stream in manifest["definitions"]["streams"].items():
        requester = stream["retriever"]["requester"]
        path = requester.get("path") or requester.get("url") or ""
        assert "incremental" not in path, f"{name} reads an incremental export: {path}"


def test_stream_set_matches_the_documented_catalog():
    manifest = _manifest()
    assert {ref["$ref"].rsplit("/", 1)[-1] for ref in manifest["streams"]} == EXPECTED_STREAMS
    assert set(manifest["definitions"]["streams"]) == EXPECTED_STREAMS
    assert set(manifest["schemas"]) == EXPECTED_STREAMS
