#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

"""Regression test for the ``events`` stream paginator.

PostHog capped the deprecated events list endpoint at 1000 rows/request
(https://github.com/PostHog/posthog/pull/60124). The events endpoint paginates by
timestamp keyset: results come back newest-first and the response advertises the next
page as a ``next`` URL that advances ``before`` while preserving the slice's ``after``
(window start). The connector must walk every ``next`` link until it runs out.

Under the previous ``OffsetIncrement`` paginator (``page_size: 10000``) a short (capped)
first page stopped pagination, silently truncating the stream. This test serves a mocked
keyset endpoint -- including decoy events *outside* the slice window -- and asserts the
events stream (a) reads the whole window, (b) follows ``next`` past the 1000-row cap, and
(c) stays bounded on BOTH ends: page 1 carries the window's ``after`` and ``before``, and
``after`` (the window floor) is preserved on every subsequent page so nothing below
``start_time`` or above ``end_time`` leaks in.
"""

import urllib.parse as up
from datetime import datetime

import requests_mock
from source_posthog import SourcePosthog

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.types import StreamSlice


CONFIG = {"api_key": "test_api_key", "base_url": "https://eu.posthog.com", "start_date": "2026-05-19T00:00:00Z"}

WINDOW_START = "2026-05-19T00:00:00.000000+00:00"
WINDOW_END = "2026-05-21T00:00:00.000000+00:00"
EVENTS_SLICE = StreamSlice(
    partition={"project_id": 2331},
    cursor_slice={"start_time": WINDOW_START, "end_time": WINDOW_END},
)

PAGE_CAP = 1000  # PostHog's EVENT_LIST_MAX_LIMIT


def _ts(value):
    return datetime.fromisoformat(value)


def _mk(day, n):
    return {"id": f"{day}-{n:06d}", "event": "$pageview", "timestamp": f"2026-05-{day}T00:00:00.{n:06d}+00:00"}


# 2500 events inside the window (-> 3 capped pages of 1000/1000/500), plus decoys strictly
# below window_start and strictly above window_end that must never be returned.
INSIDE = [_mk("20", n) for n in range(2500)]
BELOW = [_mk("18", n) for n in range(1500)]
ABOVE = [_mk("22", n) for n in range(1500)]
ALL_EVENTS = sorted(BELOW + INSIDE + ABOVE, key=lambda e: e["timestamp"], reverse=True)  # newest first
INSIDE_IDS = {e["id"] for e in INSIDE}


def _events_response(request, context):
    """Mock PostHog keyset behaviour: newest-first, capped at 1000, ``next`` advances ``before`` and keeps ``after``."""
    context.status_code = 200
    if "/events" not in request.url:
        return {"next": None, "results": [{"id": 2331}]}  # projects substream "check"
    q = up.parse_qs(up.urlparse(request.url).query)
    after = q.get("after", [None])[0]
    before = q.get("before", [None])[0]
    pool = [
        e
        for e in ALL_EVENTS  # already newest-first
        if (before is None or _ts(e["timestamp"]) < _ts(before)) and (after is None or _ts(e["timestamp"]) > _ts(after))
    ]
    page = pool[:PAGE_CAP]
    next_url = None
    if len(pool) > PAGE_CAP and page:
        params = {"before": page[-1]["timestamp"]}
        if after is not None:
            params["after"] = after  # PostHog preserves the original `after` in the next link
        next_url = "https://eu.posthog.com/api/projects/2331/events/?" + up.urlencode(params)
    return {"next": next_url, "results": page}


def _events_stream():
    return next(s for s in SourcePosthog().streams(CONFIG) if s.name == "events")


def test_events_stream_follows_next_keyset_within_window():
    """The events stream walks every ``next`` page, reads the full window, and never escapes it."""
    events = _events_stream()
    with requests_mock.Mocker() as mock:
        mock.get(requests_mock.ANY, json=_events_response)
        records = list(events.read_records(sync_mode=SyncMode.full_refresh, stream_slice=EVENTS_SLICE))
        history = [h for h in mock.request_history if "/events" in h.url]

    ids = [r["id"] for r in records]
    # Full window read past the 1000-row cap, no truncation, no duplicates (-> no loop).
    assert set(ids) == INSIDE_IDS
    assert len(ids) == len(INSIDE_IDS)
    # Bounded on both ends: nothing below window_start or above window_end leaked in.
    assert all(_ts(WINDOW_START) < _ts(r["timestamp"]) < _ts(WINDOW_END) for r in records)

    # Page 1 carries the slice window bounds.
    p1 = up.parse_qs(up.urlparse(history[0].url).query)
    assert p1.get("before", [None])[0] == WINDOW_END
    assert p1.get("after", [None])[0] == WINDOW_START

    # Multiple pages fetched; `after` (the window floor) is kept on every page and `before` advances backwards.
    assert len(history) >= 3
    afters = [up.parse_qs(up.urlparse(h.url).query).get("after", [None])[0] for h in history]
    befores = [up.parse_qs(up.urlparse(h.url).query).get("before", [None])[0] for h in history]
    assert all(a == WINDOW_START for a in afters), "the window floor `after` must be preserved on every page"
    assert [_ts(b) for b in befores] == sorted((_ts(b) for b in befores), reverse=True), "`before` must move backwards"
