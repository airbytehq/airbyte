#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

"""Regression test for the ``events`` stream paginator.

PostHog capped the deprecated events list endpoint at 1000 rows/request
(https://github.com/PostHog/posthog/pull/60124). The events endpoint paginates
by timestamp keyset: results come back newest-first, and the next page is fetched
with ``before=<oldest timestamp on the previous page>``. The connector must keep
advancing ``before`` until a page comes back empty.

Under the previous ``OffsetIncrement`` paginator (``page_size: 10000``) a short
(capped) first page stopped pagination, silently truncating the stream. This test
serves a mocked keyset endpoint and asserts the events stream walks every page and
terminates.
"""

import urllib.parse as up

import requests_mock
from source_posthog import SourcePosthog

from airbyte_cdk.models import SyncMode


CONFIG = {"api_key": "test_api_key", "base_url": "https://eu.posthog.com", "start_date": "2026-05-19T00:00:00Z"}
EVENTS_SLICE = {
    "project_id": 2331,
    "start_time": "2026-05-19T00:00:00.000000+0000",
    "end_time": "2026-05-21T00:00:00.000000+0000",
}

# 2500 events, strictly descending timestamps (one second apart) -> 3 capped pages of 1000.
TOTAL = 2500
ALL_EVENTS = [
    {"id": f"e{i:05d}", "event": "$pageview", "timestamp": f"2026-05-20T12:{(TOTAL - i) // 60 % 60:02d}:{(TOTAL - i) % 60:02d}.000000+00:00"}
    for i in range(TOTAL)
]
# guarantee strict ordering regardless of the formula above
ALL_EVENTS = sorted(ALL_EVENTS, key=lambda e: e["timestamp"], reverse=True)
for n, e in enumerate(ALL_EVENTS):
    e["timestamp"] = f"2026-05-20T00:00:00.{n:06d}+00:00"
ALL_EVENTS = sorted(ALL_EVENTS, key=lambda e: e["timestamp"], reverse=True)

PAGE_CAP = 1000  # PostHog's EVENT_LIST_MAX_LIMIT


def _events_response(request, context):
    """Mock PostHog's keyset behaviour: newest-first, page capped at 1000, ``before`` exclusive."""
    context.status_code = 200
    q = up.parse_qs(up.urlparse(request.url).query)
    if "/events" not in request.url:
        return {"next": None, "results": [{"id": 2331}]}
    before = q.get("before", [None])[0]
    pool = [e for e in ALL_EVENTS if before is None or e["timestamp"] < before]  # already descending
    return {"next": None, "results": pool[:PAGE_CAP]}


def _events_stream():
    return next(s for s in SourcePosthog().streams(CONFIG) if s.name == "events")


def test_events_stream_pages_through_keyset_until_exhausted():
    """The events stream advances ``before`` across pages and returns every record without looping."""
    events = _events_stream()
    with requests_mock.Mocker() as mock:
        mock.get(requests_mock.ANY, json=_events_response)
        records = list(events.read_records(sync_mode=SyncMode.full_refresh, stream_slice=EVENTS_SLICE))
        history = mock.request_history

    ids = [r["id"] for r in records]
    # Every record across all pages is returned (no truncation at the capped first page).
    assert len(ids) == TOTAL
    assert len(set(ids)) == TOTAL  # no duplicates -> no loop
    # More than one page was fetched, and `before` strictly advanced (decreased) each page.
    befores = [up.parse_qs(up.urlparse(r.url).query).get("before", [None])[0] for r in history if "/events" in r.url]
    paged = [b for b in befores if b]
    assert len(paged) >= 2
    assert paged == sorted(paged, reverse=True), "before cursor must move monotonically backwards"
