# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests verifying `callTranscripts` batches call IDs into grouped requests.

Gong's `POST /v2/calls/transcript` accepts an array of `callIds`. To avoid one
request per call (which exhausts Gong's rate limit and daily quota on large
backfills), the stream wraps its SubstreamPartitionRouter in a
GroupingPartitionRouter so up to `group_size` call IDs are sent per request.

These tests mock the parent `calls` response and the transcript endpoint and
assert that (1) a single transcript request carries multiple callIds, and
(2) private calls never reach the transcript request (compliance).
"""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}


def _call(call_id: str, is_private: bool = False) -> dict:
    return {
        "id": call_id,
        "started": "2024-01-02T10:00:00Z",
        "isPrivate": is_private,
    }


def _calls_response(*calls: dict) -> dict:
    return {
        "calls": list(calls),
        "records": {"totalRecords": len(calls), "currentPageSize": len(calls), "currentPageNumber": 0},
    }


def _transcript_response(*call_ids: str) -> dict:
    return {
        "callTranscripts": [{"callId": cid, "transcript": []} for cid in call_ids],
        "records": {"totalRecords": len(call_ids), "currentPageSize": len(call_ids), "currentPageNumber": 0},
    }


def test_transcript_request_batches_multiple_call_ids():
    """Multiple public call IDs are sent in a single POST /calls/transcript body."""
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("callTranscripts", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.gong.io/v2/calls", json=_calls_response(_call("c1"), _call("c2"), _call("c3")))
        mocker.post("https://api.gong.io/v2/calls/transcript", json=_transcript_response("c1", "c2", "c3"))
        read(source, _CONFIG, catalog)

        transcript_requests = [r for r in mocker.request_history if r.path == "/v2/calls/transcript"]
        assert len(transcript_requests) == 1, f"expected calls batched into 1 request, got {len(transcript_requests)}"
        sent_ids = transcript_requests[0].json()["filter"]["callIds"]
        assert sorted(sent_ids) == ["c1", "c2", "c3"], f"expected all ids batched, got {sent_ids}"


def test_transcript_request_excludes_private_calls():
    """Private calls are dropped by the parent stream and never sent to /calls/transcript."""
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("callTranscripts", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.gong.io/v2/calls",
            json=_calls_response(_call("public-1"), _call("private-1", is_private=True), _call("public-2")),
        )
        mocker.post("https://api.gong.io/v2/calls/transcript", json=_transcript_response("public-1", "public-2"))
        read(source, _CONFIG, catalog)

        transcript_requests = [r for r in mocker.request_history if r.path == "/v2/calls/transcript"]
        assert len(transcript_requests) == 1
        sent_ids = transcript_requests[0].json()["filter"]["callIds"]
        assert "private-1" not in sent_ids, f"private call leaked into transcript request: {sent_ids}"
        assert sorted(sent_ids) == ["public-1", "public-2"], f"expected only public ids, got {sent_ids}"
