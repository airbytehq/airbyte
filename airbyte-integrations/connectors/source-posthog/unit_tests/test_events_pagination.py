#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

"""Regression test for the ``events`` stream paginator.

PostHog capped the deprecated events list endpoint at 1000 rows/request
(https://github.com/PostHog/posthog/pull/60124). The endpoint paginates via the
``next`` URL in the response body, so the connector must keep following ``next``
until it is empty rather than stop after the first (now short) page.

These tests mock a capped first page that still advertises a ``next`` URL and
assert the stream follows it, returns every record, and terminates. Under the
previous ``OffsetIncrement`` paginator (``page_size: 10000``) the short first
page stopped pagination, silently truncating the stream.
"""

import requests_mock
from source_posthog import SourcePosthog

from airbyte_cdk.models import SyncMode


CONFIG = {"api_key": "test_api_key", "start_date": "2021-01-01T00:00:00Z"}

# A single (project, time-window) slice, shaped like
# EventsCartesianProductStreamSlicer.stream_slices() output.
EVENTS_SLICE = {
    "project_id": 2331,
    "start_time": "2021-01-01T00:00:00.000000+0000",
    "end_time": "2021-02-01T00:00:00.000000+0000",
}

# Page 2 is reachable only by following the ``next`` URL returned by page 1.
PAGE_2_MARKER = "cursor=page2"

# Page 1 is intentionally short (2 records): PostHog now caps the response, and a
# short page used to stop the OffsetIncrement paginator. ``next`` is a full
# absolute URL carrying the keyset for the next (older) batch, exactly as PostHog
# returns it.
PAGE_1 = {
    "next": f"https://app.posthog.com/api/projects/2331/events/?{PAGE_2_MARKER}",
    "results": [
        {"id": "ev-1", "event": "$pageview", "timestamp": "2021-01-31T10:00:00.000000+00:00"},
        {"id": "ev-2", "event": "$pageview", "timestamp": "2021-01-31T09:00:00.000000+00:00"},
    ],
}
PAGE_2 = {
    "next": None,
    "results": [
        {"id": "ev-3", "event": "$pageview", "timestamp": "2021-01-30T08:00:00.000000+00:00"},
    ],
}


def _events_response(request, context):
    context.status_code = 200
    url = request.url
    if "/events" in url:
        return PAGE_2 if PAGE_2_MARKER in url else PAGE_1
    # Parent/other endpoints, only hit if the full slice graph is traversed.
    return {"next": None, "results": [{"id": 2331}]}


def _events_stream():
    return next(stream for stream in SourcePosthog().streams(CONFIG) if stream.name == "events")


def test_events_stream_follows_next_cursor_until_exhausted():
    """The events stream follows PostHog's ``next`` URL across pages and stops when it is null."""
    events = _events_stream()

    with requests_mock.Mocker() as mock:
        mock.get(requests_mock.ANY, json=_events_response)
        records = list(events.read_records(sync_mode=SyncMode.full_refresh, stream_slice=EVENTS_SLICE))
        history = mock.request_history

    # Every record from both pages is returned: no truncation after the short first page.
    assert [record["id"] for record in records] == ["ev-1", "ev-2", "ev-3"]

    # Exactly two requests: the second followed the absolute ``next`` URL from page 1.
    assert len(history) == 2
    assert PAGE_2_MARKER in history[1].url


def test_events_stream_requests_a_full_first_page():
    """Page 1 still injects ``limit`` (page_size_option) so we ask for a full page, not the default 100."""
    events = _events_stream()

    with requests_mock.Mocker() as mock:
        mock.get(requests_mock.ANY, json=_events_response)
        list(events.read_records(sync_mode=SyncMode.full_refresh, stream_slice=EVENTS_SLICE))
        first_request = mock.request_history[0]

    assert "limit=" in first_request.url
    # The first page is bounded by the slice window; the ``next`` URL carries the cursor thereafter.
    assert "before=" in first_request.url
