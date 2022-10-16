#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pendulum
import pytest
from source_flexport.streams import IncrementalFlexportStream, Shipments


@pytest.fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalFlexportStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalFlexportStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalFlexportStream, "__abstractmethods__", set())
    mocker.patch.object(IncrementalFlexportStream, "cursor_field", "test_cursor")


@pytest.mark.parametrize(
    ("stream_class", "cursor"),
    [
        (Shipments, "updated_at"),
    ],
)
def test_cursor_field(patch_incremental_base_class, stream_class, cursor):
    stream = stream_class()
    expected_cursor_field = cursor
    assert stream.cursor_field == expected_cursor_field


@pytest.mark.parametrize(
    ("current", "latest", "expected"),
    [
        ({"test_cursor": "2021-01-01"}, {}, {"test_cursor": "2021-01-01"}),
        ({}, {"test_cursor": "2021-01-01"}, {"test_cursor": "2021-01-01"}),
        ({"test_cursor": "2021-01-01"}, {"test_cursor": "2050-01-01"}, {"test_cursor": "2050-01-01"}),
        ({"test_cursor": "2050-01-01"}, {"test_cursor": "2021-01-01"}, {"test_cursor": "2050-01-01"}),
    ],
)
def test_get_updated_state(patch_incremental_base_class, current, latest, expected):
    stream = IncrementalFlexportStream(start_date="2021-01-02")
    inputs = {"current_stream_state": current, "latest_record": latest}
    assert stream.get_updated_state(**inputs) == expected


def date(*args):
    return pendulum.datetime(*args).isoformat()


@pytest.mark.parametrize(
    ("now", "stream_state", "slice_count", "expected_from_date", "expected_to_date"),
    [
        (None, None, 24, date(2050, 1, 1), date(2050, 1, 2, 0, 0, 1)),
        (date(2050, 1, 2), None, 48, date(2050, 1, 1), date(2050, 1, 3, 0, 0, 1)),
        (None, {"test_cursor": date(2050, 1, 4)}, 1, date(2050, 1, 4), date(2050, 1, 4, 0, 0, 1)),
        (
            date(2050, 1, 5),
            {"test_cursor": date(2050, 1, 4)},
            48,
            date(2050, 1, 4),
            date(2050, 1, 6, 0, 0, 1),
        ),
        (
            # Yearly
            date(2052, 1, 1),
            {"test_cursor": date(2050, 1, 1)},
            25,
            date(2050, 1, 1),
            date(2052, 1, 2, 0, 0, 1),
        ),
        (
            # Monthly
            date(2050, 4, 1),
            {"test_cursor": date(2050, 1, 1)},
            13,
            date(2050, 1, 1),
            date(2050, 4, 2, 0, 0, 1),
        ),
        (
            # Weekly
            date(2050, 1, 31),
            {"test_cursor": date(2050, 1, 1)},
            5,
            date(2050, 1, 1),
            date(2050, 2, 1, 0, 0, 1),
        ),
        (
            # Daily
            date(2050, 1, 1, 23, 59, 59),
            {"test_cursor": date(2050, 1, 1)},
            24,
            date(2050, 1, 1),
            date(2050, 1, 2, 0, 0, 1),
        ),
    ],
)
def test_stream_slices(patch_incremental_base_class, now, stream_state, slice_count, expected_from_date, expected_to_date):
    start_date = date(2050, 1, 1)
    pendulum.set_test_now(pendulum.parse(now if now else start_date))

    stream = IncrementalFlexportStream(start_date=start_date)
    stream_slices = list(stream.stream_slices(stream_state))

    assert len(stream_slices) == slice_count
    assert stream_slices[0]["from"] == expected_from_date
    assert stream_slices[-1]["to"] == expected_to_date


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalFlexportStream, "cursor_field", "dummy_field")
    stream = IncrementalFlexportStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalFlexportStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalFlexportStream()
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
