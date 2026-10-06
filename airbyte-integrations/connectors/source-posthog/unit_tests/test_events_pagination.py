#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Regression test for the `events` stream pagination.

PostHog caps `GET /api/projects/:id/events/` at 1000 rows per request and returns a
`next` URL that points at the next keyset page (`before=<oldest timestamp of the
previous page>`, keeping the slice's `after`). The `events` stream has to follow that
URL: an offset paginator stops as soon as a page is shorter than `page_size`, which
silently truncated every slice to PostHog's 1000 row page cap.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, List, Mapping

import requests_mock
from source_posthog import SourcePosthog

from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


logger = logging.getLogger("airbyte")

BASE_URL = "https://app.posthog.com"
PROJECT_ID = 2331
PAGE_SIZE = 1000
# PostHog page size cap; the first two pages are full, then the slice runs out of records.
FULL_PAGES = 2
LAST_PAGE_RECORDS = 500

CONFIG = {
    "api_key": "test_api_key",
    "base_url": BASE_URL,
    "start_date": (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
}


def _records(page_index: int, count: int) -> List[Mapping[str, Any]]:
    """Events are returned newest first, so timestamps decrease with every page."""
    newest = datetime(2021, 1, 1, 12, 0, 0, tzinfo=timezone.utc) - timedelta(seconds=page_index * PAGE_SIZE)
    return [
        {
            "id": f"{page_index}-{record_index}",
            "timestamp": (newest - timedelta(seconds=record_index)).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
            "event": "test_event",
        }
        for record_index in range(count)
    ]


def _next_url(page_index: int) -> str:
    return f"{BASE_URL}/api/projects/{PROJECT_ID}/events?after=SLICE_START&before=PAGE_BOUNDARY_{page_index}&limit={PAGE_SIZE}"


class _PosthogMock:
    """Serves `projects` and, for `events`, one full page per call with a `next` link."""

    def __init__(self) -> None:
        self.events_urls: List[str] = []

    def __call__(self, request: Any, context: Any) -> str:
        url = request.url
        if url.split("?")[0].rstrip("/").endswith("/projects"):
            return json.dumps({"results": [{"id": PROJECT_ID}], "next": None})

        page_index = len(self.events_urls)
        self.events_urls.append(url)
        if page_index < FULL_PAGES:
            results, next_page = _records(page_index, PAGE_SIZE), _next_url(page_index)
        elif page_index == FULL_PAGES:
            results, next_page = _records(page_index, LAST_PAGE_RECORDS), None
        else:
            raise AssertionError(f"events pagination did not stop, unexpected request: {url}")
        return json.dumps({"results": results, "next": next_page})


def _configured_catalog(source: SourcePosthog) -> ConfiguredAirbyteCatalog:
    discovered = source.discover(logger, dict(CONFIG))
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream,
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=["timestamp"],
            )
            for stream in discovered.streams
            if stream.name == "events"
        ]
    )


def _read_events() -> "tuple[List[Mapping[str, Any]], _PosthogMock]":
    mock = _PosthogMock()
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{BASE_URL}/api/projects", text=json.dumps({"results": [{"id": PROJECT_ID}], "next": None}))
        mocker.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/events/", text=mock)
        mocker.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/events", text=mock)

        source = SourcePosthog()
        messages = list(source.read(logger, dict(CONFIG), _configured_catalog(source), None))

    records = [message.record.data for message in messages if message.type == Type.RECORD and message.record.stream == "events"]
    return records, mock


def test_events_pagination_follows_next_url_to_the_oldest_record_of_the_slice():
    records, mock = _read_events()

    expected_total = FULL_PAGES * PAGE_SIZE + LAST_PAGE_RECORDS
    assert len(mock.events_urls) == FULL_PAGES + 1, "every page returned by PostHog has to be requested"
    assert len(records) == expected_total

    record_ids = {record["id"] for record in records}
    assert len(record_ids) == expected_total, "no duplicate or missing records"
    # the oldest records of the slice are the ones an offset paginator used to drop
    assert f"{FULL_PAGES}-{LAST_PAGE_RECORDS - 1}" in record_ids


def test_events_pagination_requests_the_next_url_verbatim():
    _, mock = _read_events()

    # the slice's `after`/`before` must not override the keyset cursor embedded in the `next` URL
    assert mock.events_urls[1] == _next_url(0)
    assert mock.events_urls[2] == _next_url(1)


def test_events_pagination_requests_the_page_size_the_api_actually_honors():
    _, mock = _read_events()

    # PostHog clamps `limit` to 1000, so asking for more truncates the slice
    assert f"limit={PAGE_SIZE}" in mock.events_urls[0]
