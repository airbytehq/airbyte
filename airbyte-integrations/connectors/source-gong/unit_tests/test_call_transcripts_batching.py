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


def _call(call_id: str, is_private: bool = False, started: str = "2024-01-02T10:00:00Z") -> dict:
    return {
        "id": call_id,
        "started": started,
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


def test_incremental_cursor_advances_to_newest_call_in_batch():
    """The emitted cursor state must advance to the newest `started` in the grouped batch.

    Records have no timestamp of their own, so the stream stamps `started` with
    `max(extra_fields['started'])` across the grouped calls. This asserts the
    resulting incremental state matches the newest call in the batch (so the
    cursor never rewinds and no calls are re-fetched needlessly), covering the
    forwards-compat / rollback concern for the GroupingPartitionRouter swap.
    """
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("callTranscripts", SyncMode.incremental).build()

    calls = _calls_response(
        _call("c1", started="2024-03-01T09:00:00Z"),
        _call("c2", started="2024-03-05T12:00:00Z"),  # newest in the batch
        _call("c3", started="2024-03-03T15:00:00Z"),
    )

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.gong.io/v2/calls", json=calls)
        mocker.post("https://api.gong.io/v2/calls/transcript", json=_transcript_response("c1", "c2", "c3"))
        output = read(source, _CONFIG, catalog)

    # Every emitted record should carry the batch-max `started`.
    stamped = {record.record.data.get("started") for record in output.records}
    assert stamped == {"2024-03-05T12:00:00Z"}, f"expected records stamped with batch-max started, got {stamped}"

    # The final cursor state must reflect the newest call in the batch, so the
    # cursor never rewinds and calls are not needlessly re-fetched. With
    # global_substream_cursor the value lives under the "state" key.
    assert output.state_messages, "expected at least one state message for an incremental sync"
    stream_state = output.most_recent_state.stream_state
    state_value = stream_state if isinstance(stream_state, dict) else stream_state.__dict__
    cursor = state_value.get("state", state_value).get("started")
    assert cursor == "2024-03-05T12:00:00Z", (
        f"expected cursor to advance to newest call time in batch, got {cursor}"
    )
