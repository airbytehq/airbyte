#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
"""Runtime tests that load the declarative manifest through the CDK and verify
incremental cursor state and rate-limit behaviour end-to-end.
"""

from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import build_source


def _read_messages(config, requests_mock, state=None):
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    state = StateBuilder().build() if not state else state
    return read(build_source(config, state), config, catalog, state)


def test_messages_incremental_checkpoints_internal_date(base_config, requests_mock):
    """After a successful sync, the cursor state must be the max `internalDate`
    seen (as unix seconds), proving `messages` is genuinely incremental."""
    # internalDate is returned as millis by Gmail.
    requests_mock.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        json={
            "messages": [
                {"id": "m1", "threadId": "t1", "internalDate": "1700000000000"},
                {"id": "m2", "threadId": "t2", "internalDate": "1700001000000"},
            ]
        },
    )

    output = _read_messages(base_config, requests_mock)

    assert output.records, "Expected at least one record from the messages stream"
    states = output.state_messages
    assert states, "Expected at least one state message — messages must be incremental"

    final_state = states[-1].state.stream.stream_state.__dict__
    # The cursor value is stored in the manifest's datetime_format (%s = unix seconds).
    cursor_value = final_state.get("internalDate")
    assert cursor_value == "1700001000"


def test_messages_request_injects_after_from_start_date(config_with_start_date, requests_mock):
    """With a configured start_date, the first request must include
    `q=after:<unix_seconds>` so Gmail filters server-side from the start."""
    requests_mock.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        json={"messages": []},
    )

    _read_messages(config_with_start_date, requests_mock)

    assert requests_mock.call_count >= 1
    history = [r for r in requests_mock.request_history if r.url.startswith("https://gmail.googleapis.com/gmail/v1/users/me/messages")]
    assert history, "Expected at least one call to the Gmail messages endpoint"

    qs = parse_qs(urlparse(history[0].url).query)
    assert "q" in qs, "Expected `q` parameter to be present"
    q_value = qs["q"][0]
    assert q_value.startswith("after:"), f"Expected after: filter, got {q_value!r}"
    # 2024-01-01T00:00:00Z = 1704067200 unix seconds
    assert q_value == "after:1704067200"


def test_retry_after_on_429_is_honoured(base_config, requests_mock, mocker):
    """When Gmail returns a 429 with a Retry-After header, the CompositeErrorHandler
    on the base_requester must sleep for that duration and then retry the request."""
    sleep_mock = mocker.patch("time.sleep")

    requests_mock.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        [
            {
                "status_code": 429,
                "headers": {"Retry-After": "7"},
                "json": {"error": {"code": 429, "message": "rateLimitExceeded"}},
            },
            {
                "status_code": 200,
                "json": {"messages": [{"id": "m1", "threadId": "t1", "internalDate": "1700000000000"}]},
            },
        ],
    )

    output = _read_messages(base_config, requests_mock)

    # The CDK's WaitTimeFromHeader honours the Retry-After header (with a small
    # safety padding); the resulting sleep must be at least the header value.
    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert any(7 <= duration <= 10 for duration in sleep_durations), f"Expected a backoff honouring Retry-After=7s; got {sleep_durations!r}"
    assert output.records, "Expected the retry to succeed and produce a record"
