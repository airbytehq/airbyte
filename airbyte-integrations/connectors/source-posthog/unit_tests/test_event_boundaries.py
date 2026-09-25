# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import re
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import pytest
from dateutil.parser import isoparse
from source_posthog import SourcePosthog

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime


BASE = "https://app.posthog.com/api/"
CONFIG = {
    "api_key": "test",
    "base_url": "https://app.posthog.com",
    "start_date": "2021-01-01T00:00:00Z",
    "events_time_step": 5,
}
PREDICATE = re.compile(
    r"timestamp > toDateTime\('([^']+)'\) " r"OR \(timestamp = toDateTime\('([^']+)'\) " r"AND uuid > toUUID\('([^']+)'\)\)"
)


def database_key(timestamp, event_id):
    """ClickHouse compares the trailing UUID half before the leading half."""
    canonical_uuid = UUID(event_id).hex
    return (
        isoparse(timestamp),
        int(canonical_uuid[16:], 16),
        int(canonical_uuid[:16], 16),
    )


def record_key(record):
    return database_key(record["timestamp"], record["id"])


@pytest.mark.parametrize("server_page_size", [1, 2, 5])
def test_predicate_preserves_ties_precision_and_adjacent_slices(requests_mock, monkeypatch, tmp_path, server_page_size):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    requests_mock.get(BASE + "projects", json={"results": [{"id": 42}], "next": None})
    events = next(stream for stream in SourcePosthog().streams(CONFIG) if stream.name == "events")
    datetime_slicer = events.retriever.stream_slicer.stream_slicers[1]
    datetime_slicer.end_datetime = MinMaxDatetime(
        datetime="2021-01-15T00:00:00+0000",
        datetime_format="%Y-%m-%dT%H:%M:%S%z",
        parameters={},
    )
    slices = list(events.stream_slices(sync_mode=SyncMode.incremental))
    assert len(slices) == 3
    assert all(previous["end_time"] == following["start_time"] for previous, following in zip(slices, slices[1:]))

    records = []
    fixture_group = 0
    for part in slices:
        start = isoparse(part["start_time"])
        end = isoparse(part["end_time"])
        for timestamp in (
            start,
            start + timedelta(microseconds=1),
            end - timedelta(microseconds=1),
        ):
            # The first two UUIDs sort in opposite orders under Python's normal
            # UUID comparison and ClickHouse's UUID comparison.
            leading_half = fixture_group * 3
            fixture_group += 1
            uuid_values = (
                (leading_half + 1) << 64,
                (leading_half << 64) + 1,
                ((leading_half + 2) << 64) + 1,
            )
            for value in uuid_values:
                records.append(
                    {
                        "id": str(UUID(int=value)),
                        "timestamp": timestamp.isoformat(timespec="microseconds"),
                        "properties": {"nested": [1, {"preserve": True}]},
                    }
                )
    records.sort(key=record_key)
    assert len(records) == len({record["id"] for record in records}) == 27

    expected_bounds = {
        (
            (isoparse(part["start_time"]) - timedelta(microseconds=1)).isoformat(timespec="microseconds"),
            part["end_time"],
        )
        for part in slices
    }
    requests_by_bounds = {bounds: [] for bounds in expected_bounds}

    def serve_page(request, context):
        # Parse the raw URL so requests-mock's normalized/lowercase `qs` view
        # cannot hide changes to expression spelling or timestamp formatting.
        params = parse_qs(urlsplit(request.url).query)
        assert params["limit"] == ["1000"]
        assert json.loads(params["orderBy"][0]) == ["timestamp", "uuid"]
        bounds = params["after"][0], params["before"][0]
        assert bounds in expected_bounds
        after, before = map(isoparse, bounds)
        eligible = [record for record in records if after < isoparse(record["timestamp"]) < before]

        history = requests_by_bounds[bounds]
        if "properties" in params:
            filters = json.loads(params["properties"][0])
            assert len(filters) == 1
            assert filters[0]["type"] == "hogql"
            match = PREDICATE.fullmatch(filters[0]["key"])
            assert match, filters[0]["key"]
            greater_timestamp, equal_timestamp, cursor_id = match.groups()
            assert greater_timestamp == equal_timestamp
            assert history and history[-1]
            previous_record = history[-1][-1]
            assert database_key(greater_timestamp, cursor_id) == record_key(previous_record)

            # Apply both branches independently, including exact microseconds.
            cursor_timestamp = isoparse(greater_timestamp)
            cursor_uuid_order = database_key(greater_timestamp, cursor_id)[1:]
            eligible = [
                record
                for record in eligible
                if isoparse(record["timestamp"]) > cursor_timestamp
                or (isoparse(record["timestamp"]) == cursor_timestamp and record_key(record)[1:] > cursor_uuid_order)
            ]
        else:
            assert not history, "The next request lost its keyset predicate"

        batch = eligible[:server_page_size]
        history.append(batch)
        # Deliberately lie about exhaustion, as the legacy endpoint can do.
        return {"results": batch, "next": None}

    requests_mock.get(BASE + "projects/42/events/", json=serve_page)
    emitted = []
    for part in slices:
        emitted.extend(dict(record) for record in events.read_records(SyncMode.incremental, stream_slice=part))

    assert emitted == records
    assert all(history and history[-1] == [] for history in requests_by_bounds.values())
    assert events.state == {"42": {"timestamp": records[-1]["timestamp"]}}
